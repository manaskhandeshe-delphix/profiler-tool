from typing import List, Optional, Dict, Union, Iterator, Iterable
import collections
from dataclasses import dataclass
import pprint

import pandas as pd

from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine, RecognizerResult, DictAnalyzerResult

columns = ["name phrase", "phone number phrase", "integer", "boolean" ]
#sample_data = [
#        ('Charlie likes this', 'Please call 212-555-1234 after 2pm', 1, True),
#        ('You should talk to Mike', 'his number is 978-428-7111', 2, False),
#        ('Mary had a little startup', 'Phone number: 202-342-1234', 3, False)
#]
sample_data = [
        ('', '', 0, True),
        ('', '', 2, False),
        ('', '', 3, False)
]
df  = pd.DataFrame(sample_data,columns=columns)

# DataFrame to dict
df_dict = df.to_dict(orient="list")
#pprint.pprint(df_dict)

analyzer = AnalyzerEngine()
batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
analyzer_results = batch_analyzer.analyze_dict(df_dict, language="en")
analyzer_results = list(analyzer_results)
for x in analyzer_results:
    print(x)
    print("======")
