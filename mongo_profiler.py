import sys
import pymongo
import yaml
from pprint import pprint

# modules for json parsing
import json
import re
from jsonpathgenerator import jsonpath
import jsonpath_ng   
from collections import OrderedDict                                            

# modules for presidio
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry


class Globals:
    PROF_CONF_PATH = 'mongo_profiler.yaml'
    JSONPATHS_FILE_PATH = f"{{db_name}}_{{collection}}_meta.jsonpath"
    FMT_FILE_PATH = f"{{db_name}}_{{collection}}_meta.fmt"
    MASKING_INVENTORY_FILE_PATH = f"{{db_name}}_{{collection}}_masking_inventory.json"
    RECOGNIZER_PATH = 'recognizers.yaml'
    ALGORITHMS_MAPPING = {
            'FIRST_NAME' : 'dlpx-core:FirstName',
            'LAST_NAME' : 'dlpx-core:LastName',
            'ZIP' : 'USstatecodesLookup',
    }


class MongoDBConnector:
    def __init__(self, uri, db_name, collection):
        self.uri = uri
        self.db_name = db_name
        self.collection = collection
        self.client = None
        self.db_obj = None


    def connect(self):
        try:
            self.client = pymongo.MongoClient(self.uri)
            self.db_obj = self.client[self.db_name]
            self.collection_obj = self.db_obj[self.collection]
            print("Connected to MongoDB successfully!")
        except pymongo.errors.ConnectionFailure:
            print("Failed to connect to MongoDB.")

    def generate_samples(self, default=3):
        pipeline = [{ "$sample": { "size": default}}]
        #pprint(list(self.collection_obj.aggregate(pipeline)))
        return list(self.collection_obj.aggregate(pipeline))

    def close_connection(self):
        if self.client:
            self.client.close()
            print("Connection to MongoDB closed.")


class JsonProcessor:
    def __init__(self, jp_obj=None, jsondata=None):
        self.jp_obj = jp_obj
        self.jsondata = jsondata

    def generate_jsonpaths_using_samples(self):
        find_pattern = "\[[0-9]*\]"
        replace_pattern = '[*]'
        jsonpath_dict = OrderedDict()

        jsonpaths_of_jsondata = self.jp_obj.get_json_path(
                            self.jsondata,
                            notation="bracket"
                            )
        for p in jsonpaths_of_jsondata:
            p = re.sub(find_pattern, replace_pattern, p)
            jsonpath_dict[p] = None

        return jsonpath_dict
        #print(*jsonpath_dict.keys(), sep="\n")
        #sys.exit(0)


def connect_to_database(uri, db, collection):
    connector = MongoDBConnector(uri, db, collection)
    connector.connect()
    return connector


def generate_samples(connector):
    return connector.generate_samples()


def create_jsonpaths_using_samples(connector, jsonpaths_file_path):
    json_samples_data = generate_samples(connector)
    json_processor = JsonProcessor(
                jp_obj=jsonpath(),
                jsondata=json_samples_data
            )

    jsonpaths_dict = json_processor.generate_jsonpaths_using_samples()
    with open(jsonpaths_file_path, "w") as f:
        for k in jsonpaths_dict.keys():
            f.write(f"{k}\n")

    return jsonpaths_dict


def create_fmt_using_jsonpaths(connector, jsonpaths_dict, fmt_path):
    indexed_jsonpath_list = list(jsonpaths_dict.keys()) 
    find_pattern = "\[\*\]"
    replace_pattern = '[0]'
    indexed_jsonpath_list = [re.sub(find_pattern, replace_pattern, p) for p in indexed_jsonpath_list]

    IS_LIST = False
    if indexed_jsonpath_list[0].startswith("$[0]"):
        IS_LIST = True

    if IS_LIST:
        d = {0: {}}
    else:
        d = {}

    for p in indexed_jsonpath_list:
        l = jsonpath_ng.parse(p)
        try:
            l.update_or_create(d, '')
        except TypeError:
            p2 = "[".join(p.split('[')[:-1])
            l2 = jsonpath_ng.parse(p2)
            l2.update_or_create(d, {})
            l.update_or_create(d, '')

    if IS_LIST:
        d = [d[0]]

    fmt_jsondata = json.dumps(d, indent=4)
    with open(fmt_path, 'w') as f:
        f.write(fmt_jsondata)


def profile_and_create_masking_inventory(
        jsonpaths_file_path,
        masking_inventory_file_path,
        recognizer_file_path
        ):

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()
    registry.add_recognizers_from_yaml(recognizer_file_path)

    analyzer = AnalyzerEngine(registry=registry)
    masking_inventory_list = []
    with open(masking_inventory_file_path, "w") as f_masking_inventory:
        with open(jsonpaths_file_path) as f_jsonpaths:
            for jsonpath_text in f_jsonpaths.readlines():
                results = analyzer.analyze(
                                text=jsonpath_text,
                                language="en"
                            )
                for result in results:
                    if result.entity_type:
                        # write to inventory
                        masking_inventory_list.append({
                            "field_name": jsonpath_text,
                            "domain_name": result.entity_type,
                            "algorithm_name": Globals.ALGORITHMS_MAPPING[result.entity_type]
                        })

        masking_inventory_json = json.dumps(masking_inventory_list, indent=4)
        f_masking_inventory.write(masking_inventory_json)


def read_config(conf_path):
    with open(conf_path, 'r') as file:
        conf_data = yaml.safe_load(file)
        return conf_data


if __name__ == "__main__":

    # STEP : Accept DB credentails and connect
    prof_conf_path = Globals.PROF_CONF_PATH
    prof_conf_data = read_config(prof_conf_path)

    connector = connect_to_database(
                    prof_conf_data['mongodb_uri'],
                    prof_conf_data['database'],
                    prof_conf_data['collection'],
                )

    # STEP : Create jsonpaths using samples
    jsonpaths_file_path = Globals.JSONPATHS_FILE_PATH.format(
                    db_name=prof_conf_data['database'],
                    collection=prof_conf_data['collection']
                )
    jsonpaths_dict = create_jsonpaths_using_samples(
            connector,
            jsonpaths_file_path
        )


    # STEP : Create fmt using jsonpaths
    fmt_file_path = Globals.FMT_FILE_PATH.format(
                    db_name=prof_conf_data['database'],
                    collection=prof_conf_data['collection']
                )
    create_fmt_using_jsonpaths(
            connector,
            jsonpaths_dict,
            fmt_file_path
            )

    # STEP : Profiling and create masking_inventory json
    masking_inventory_file_path = Globals.MASKING_INVENTORY_FILE_PATH.format(
                    db_name=prof_conf_data['database'],
                    collection=prof_conf_data['collection']
            )
    recognizer_file_path = Globals.RECOGNIZER_PATH
    profile_and_create_masking_inventory(
        jsonpaths_file_path,
        masking_inventory_file_path,
        recognizer_file_path
    )

    connector.close_connection()

