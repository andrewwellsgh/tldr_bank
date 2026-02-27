import pandas as pd
import pytest

from src.tldr_bank.security import SecurityCheck


@pytest.fixture
def sc():
    return SecurityCheck()


def test_standard_headers(sc):
    df = pd.DataFrame({"date": ["2024-01-01"], "description": ["Coffee"], "amount": [-3.50]})
    result = sc.run(df)
    assert list(result.columns[:3]) == ["date", "description", "amount"]


def test_nonstandard_headers_are_mapped(sc):
    df = pd.DataFrame({
        "TransactionDate": ["2024-01-01"],
        "MerchantName": ["Coffee"],
        "Value": [-3.50],
    })
    result = sc.run(df)
    assert "date" in result.columns
    assert "description" in result.columns
    assert "amount" in result.columns


def test_amount_hint_matches_debit(sc):
    df = pd.DataFrame({
        "date": ["2024-01-01"],
        "description": ["Coffee"],
        "debit": [-3.50],
    })
    result = sc.run(df)
    assert "amount" in result.columns


def test_unrecognisable_columns_raise(sc):
    df = pd.DataFrame({"col_a": [1, 2], "col_b": ["x", "y"]})
    with pytest.raises(ValueError, match="Cannot identify required columns"):
        sc.run(df)


def test_amount_is_numeric(sc):
    df = pd.DataFrame({"date": ["2024-01-01"], "description": ["Test"], "amount": ["-12.50"]})
    result = sc.run(df)
    assert result["amount"].dtype == float
    assert result["amount"].iloc[0] == -12.50


def test_amount_with_commas_parsed(sc):
    df = pd.DataFrame({"date": ["2024-01-01"], "description": ["Test"], "amount": ["1,234.56"]})
    result = sc.run(df)
    assert result["amount"].iloc[0] == pytest.approx(1234.56)


def test_negative_amounts_preserved(sc):
    df = pd.DataFrame({"date": ["2024-01-01"], "description": ["Test"], "amount": [-99.99]})
    result = sc.run(df)
    assert result["amount"].iloc[0] == -99.99


def test_unparseable_date_row_dropped(sc):
    df = pd.DataFrame({
        "date": ["not-a-date", "2024-01-02"],
        "description": ["Bad", "Good"],
        "amount": [-1.0, -2.0],
    })
    result = sc.run(df)
    assert len(result) == 1
    assert result["description"].iloc[0] == "Good"


def test_unparseable_amount_row_dropped(sc):
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "description": ["Bad", "Good"],
        "amount": ["not_a_number", "-5.00"],
    })
    result = sc.run(df)
    assert len(result) == 1


def test_null_description_becomes_unknown(sc):
    df = pd.DataFrame({
        "date": ["2024-01-01"],
        "description": [None],
        "amount": [-1.0],
    })
    result = sc.run(df)
    assert result["description"].iloc[0] == "unknown"


def test_all_bad_rows_returns_empty(sc):
    df = pd.DataFrame({
        "date": ["bad", "also-bad"],
        "description": ["X", "Y"],
        "amount": [-1.0, -2.0],
    })
    result = sc.run(df)
    assert result.empty


def test_date_parsed_to_datetime(sc):
    df = pd.DataFrame({"date": ["2024-06-15"], "description": ["Test"], "amount": [-1.0]})
    result = sc.run(df)
    assert pd.api.types.is_datetime64_any_dtype(result["date"])
