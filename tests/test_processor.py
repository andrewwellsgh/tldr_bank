import pandas as pd
import pytest

from src.tldr_bank.processor import CSVProcessor


@pytest.fixture
def csv_folder(tmp_path):
    (tmp_path / "bank1.csv").write_text(
        "Date,Description,Amount\n2024-01-01,Coffee,-3.50\n2024-01-02,Salary,1000.00\n"
    )
    (tmp_path / "bank2.csv").write_text(
        "Date,Description,Amount\n2024-02-01,Groceries,-45.00\n"
    )
    return str(tmp_path)


def test_missing_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        CSVProcessor(folder=str(tmp_path / "nonexistent")).run()


def test_empty_folder_returns_empty_df(tmp_path):
    df = CSVProcessor(folder=str(tmp_path)).run()
    assert df.empty
    assert list(df.columns) == ["date", "description", "amount"]


def test_multiple_csvs_merged(csv_folder):
    assert len(CSVProcessor(folder=csv_folder).run()) == 3


def test_output_has_required_columns(csv_folder):
    df = CSVProcessor(folder=csv_folder).run()
    for col in ("date", "description", "amount"):
        assert col in df.columns


def test_non_csv_files_ignored(tmp_path):
    (tmp_path / "bank.csv").write_text("Date,Description,Amount\n2024-01-01,Coffee,-3.50\n")
    (tmp_path / "notes.txt").write_text("ignore me")
    assert len(CSVProcessor(folder=str(tmp_path)).run()) == 1


def test_amounts_are_numeric(csv_folder):
    assert pd.api.types.is_float_dtype(CSVProcessor(folder=csv_folder).run()["amount"])


def test_dates_are_datetime(csv_folder):
    assert pd.api.types.is_datetime64_any_dtype(CSVProcessor(folder=csv_folder).run()["date"])


def test_invalid_rows_dropped(tmp_path):
    (tmp_path / "bad.csv").write_text(
        "Date,Description,Amount\nnot-a-date,Coffee,-3.50\n2024-01-02,Valid,-10.00\n"
    )
    df = CSVProcessor(folder=str(tmp_path)).run()
    assert len(df) == 1
    assert df["description"].iloc[0] == "Valid"
