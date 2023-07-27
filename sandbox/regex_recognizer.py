
from presidio_analyzer import Pattern, PatternRecognizer

# Define the regex pattern in a Presidio `Pattern` object:
numbers_pattern = Pattern(name="numbers_pattern", regex="\d+", score=0.5)
firstname_pattern = Pattern(name="firstname_pattern", regex="(firstName)", score=0.5)

# Define the recognizer with one or more patterns
number_recognizer = PatternRecognizer(
    supported_entity="NUMBER", patterns=[numbers_pattern]
)

firstname_recognizer = PatternRecognizer(
    supported_entity="FIRST_NAME", patterns=[firstname_pattern]
)

text2 = "I live in 510 Broad st. firstName manas"
results = number_recognizer.analyze(text=text2, entities=["NUMBER"])

for result in results:
    print(f"- {text2[result.start:result.end]} as {result.entity_type}")

results = firstname_recognizer.analyze(text=text2, entities=["FIRST_NAME"])
for result in results:
    print(f"- {text2[result.start:result.end]} as {result.entity_type}")
