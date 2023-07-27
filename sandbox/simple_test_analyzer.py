from presidio_analyzer import AnalyzerEngine

text="My phone number is 212-555-5555\n My name is Mr. John Travolta"

# Set up the engine, loads the NLP module (spaCy model by default) 
# and other PII recognizers
analyzer = AnalyzerEngine()

# Call analyzer to get results
results = analyzer.analyze(text=text,
                           #entities=["PHONE_NUMBER"],
                           language='en')
print(results)
