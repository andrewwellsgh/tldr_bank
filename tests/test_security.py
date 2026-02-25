import pandas as pd
import pytest
from src.tldr_bank.security import SecurityCheck

sc = SecurityCheck()

def test_standard_headers():
    df = pd.DataFrame({'date':['2026-01-01'], 'description':['Coffee'], 'amount':[3]})
    result = sc.run(df)
    assert 'amount' in result.columns

def test_nonstandard_headers():
    df = pd.DataFrame({'TransactionDate':['2026-01-01'], 'MerchantName':['Coffee'], 'Value':[3]})
    result = sc.run(df)
    assert 'amount' in result.columns
    assert 'date' in result.columns
    assert 'description' in result.columns

def test_invalid_missing_column():
    df = pd.DataFrame({'random':[1,2]})
    with pytest.raises(ValueError):
        sc.run(df)

def test_partial_invalid_rows():
    df = pd.DataFrame({'date':['bad','2026-01-02'], 'description':['Coffee', None], 'amount':['NaN','20']})
    result = sc.run(df)
    assert len(result) == 1
