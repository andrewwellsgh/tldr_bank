import pandas as pd
from src.tldr_bank.processor import CSVProcessor

def test_processor_empty_folder():
    processor = CSVProcessor(folder="tests/empty_folder")
    df = processor.run()
    assert df.empty or 'amount' in df.columns
