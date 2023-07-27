import pymongo
import yaml
from pprint import pprint


class Globals:
    PROF_CONF_PATH = 'mongo_profiler.yaml'


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
        pipeline = [{ "$sample": { "size": 3}}]
        pprint(list(self.collection_obj.aggregate(pipeline)))

    def close_connection(self):
        if self.client:
            self.client.close()
            print("Connection to MongoDB closed.")



def connect_to_database(uri, db, collection):
    connector = MongoDBConnector(uri, db, collection)
    connector.connect()
    return connector


def generate_samples(connector):
    connector.generate_samples()



def create_fmt_using_samples(connector):
    generate_samples(connector)
    pass


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

    # STEP : Create fmt using samples
    create_fmt_using_samples(connector)


    connector.close_connection()

