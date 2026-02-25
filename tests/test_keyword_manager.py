import pandas as pd
from src.tldr_bank.keyword_manager import KeywordManager

def test_keyword_manager_basic():
    df = pd.DataFrame({'description':['Coffee','coffee'],'amount':[10,5]})
    km = KeywordManager()
    totals = km.run(df)
    assert 'coffee' in totals['keyword'].values
