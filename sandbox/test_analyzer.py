from presidio_analyzer import AnalyzerEngine, PatternRecognizer

#text="""
#$[*]['userId']
#$[*]['jobTitleName']
#$[*]['firstName']
#$[*]['lastName']
#$[*]['preferredFullName']
#$[*]['employeeCode']
#$[*]['region']
#$[*]['phoneNumber']
#$[*]['emailAddress']
#"""


text_to_anonymize = "His name is Mr. Jones and his phone number is 212-555-5555"

analyzer = AnalyzerEngine()

titles_recognizer = PatternRecognizer(supported_entity="TITLE",
                                      deny_list=["Mr.","Mrs.","Miss"])

pronoun_recognizer = PatternRecognizer(supported_entity="PRONOUN",
                                       deny_list=["he", "He", "his", "His", "she", "She", "hers", "Hers"])

analyzer.registry.add_recognizer(titles_recognizer)
analyzer.registry.add_recognizer(pronoun_recognizer)

analyzer_results = analyzer.analyze(text=text_to_anonymize,
                            #entities=["TITLE", "PRONOUN"],
                            language="en")
print(analyzer_results)
for x in analyzer_results:
    print(x)
    print("====")
