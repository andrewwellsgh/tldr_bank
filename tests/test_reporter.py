import pandas as pd
from src.tldr_bank.reporter import Reporter

def test_reporter_basic():
    df = pd.DataFrame({'date':pd.to_datetime(['2026-01-01','2026-01-02']),
                       'description':['Coffee','Groceries'],
                       'amount':[10,20]})
    totals = pd.DataFrame({'keyword':['coffee','groceries'],'amount':[10,20]})
    reporter = Reporter()
    reporter.run(df, totals)
