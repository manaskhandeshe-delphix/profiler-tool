
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

yaml_file = "recognizers.yaml"
registry = RecognizerRegistry()
registry.load_predefined_recognizers()

registry.add_recognizers_from_yaml(yaml_file)

analyzer = AnalyzerEngine()
results = analyzer.analyze(text="Mr. and Mrs. Smith", language="en")
print(results)

