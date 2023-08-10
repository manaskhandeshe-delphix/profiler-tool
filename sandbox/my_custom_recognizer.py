from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

original_data="""
$[*]['userId']
$[*]['jobTitleName']
$[*]['firstName']
$[*]['lastName']
$[*]['preferredFullName']
$[*]['employeeCode']
$[*]['region']
$[*]['phoneNumber']
$[*]['emailAddress']
"""

#original_data = "firstName Mr. and Mrs. Smith Mr. Mr. Mr."
#original_data = "Mr. John Smith's drivers license is AC432223. firstName manas"

yaml_file = "my_recognizers.yaml"
registry = RecognizerRegistry()
registry.load_predefined_recognizers()
registry.add_recognizers_from_yaml(yaml_file)

analyzer = AnalyzerEngine(registry=registry)
results = analyzer.analyze(text=original_data, language="en")
print("Detecting following sensitive information.")
for result in results:
    print(f"- {original_data[result.start:result.end]} as {result.entity_type}")
