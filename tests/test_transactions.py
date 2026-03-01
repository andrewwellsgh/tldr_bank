import os
import pytest
from tldr_bank.transactions import normalize_csv, top_n_items

# Use a temporary CSV for testing
TEST_CSV = "test_sample.csv"

@pytest.fixture(scope="module")
def sample_csv():
    data = """Transaction Date,Details,Debit,Credit,Balance
01/01/2026,FOO BAR,1234.56,,5000
02/02/2026,ALICE SMITH,7890.12,,0
03/03/2026,BOB JONES,3456.78,,0
04/04/2026,CHARLIE CO,987.65,,0
05/05/2026,DELTA INC,4321.09,,0
"""
    with open(TEST_CSV, 'w', encoding='utf-8') as f:
        f.write(data)
    yield TEST_CSV
    os.remove(TEST_CSV)

def test_normalize_csv(sample_csv):
    txs = normalize_csv(sample_csv)
    assert len(txs) == 5
    for tx in txs:
        assert 'details' in tx
        assert 'amount' in tx
        assert isinstance(tx['amount'], float)

def test_top_n_items(sample_csv):
    txs = normalize_csv(sample_csv)
    top_items = top_n_items(txs, n=3)
    assert len(top_items) == 3
    # Check descending by absolute value
    amounts = [abs(item['total']) for item in top_items]
    assert amounts == sorted(amounts, reverse=True)