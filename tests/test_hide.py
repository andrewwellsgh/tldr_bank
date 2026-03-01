import pandas as pd
import pytest

from src.tldr_bank.settings import load_hidden_groups
from src.tldr_bank.keyword_manager import KeywordManager


@pytest.fixture
def hide_file(tmp_path):
    def _write(content: str) -> str:
        path = tmp_path / ".hide"
        path.write_text(content)
        return str(path)
    return _write


def test_missing_file_returns_empty(tmp_path):
    hidden = load_hidden_groups(str(tmp_path / "nonexistent.hide"))
    assert hidden == set()


def test_empty_file_returns_empty(hide_file):
    hidden = load_hidden_groups(hide_file(""))
    assert hidden == set()


def test_lines_are_uppercased(hide_file):
    hidden = load_hidden_groups(hide_file("andy\namazon"))
    assert hidden == {"ANDY", "AMAZON"}


def test_comments_and_blank_lines_skipped(hide_file):
    content = """
    # comment line
    ANDY

    AMAZON
    """
    hidden = load_hidden_groups(hide_file(content))
    assert hidden == {"ANDY", "AMAZON"}


# ---------------------------------------------------------------------------
# Integration test with KeywordManager
# ---------------------------------------------------------------------------

def test_hidden_groups_filter_totals_and_df(tmp_path):
    # Create sample transactions
    df = pd.DataFrame({
        "description": ["ANDY", "AMAZON", "TESCO", "BOB"],
        "amount": [-10.0, -20.0, -30.0, -40.0],
        "date": pd.to_datetime(["2024-01-01"] * 4),
    })

    # Save hide file
    hide_path = tmp_path / ".hide"
    hide_path.write_text("ANDY\nAMAZON")

    hidden_groups = load_hidden_groups(str(hide_path))

    km = KeywordManager(df, fuzzy_threshold=100)
    totals, df_labelled = km.run()

    # Apply hide filter
    filtered_totals = totals[~totals.index.str.upper().isin(hidden_groups)]
    filtered_df = df_labelled[~df_labelled["keyword"].str.upper().isin(hidden_groups)]

    # Only TESCO and BOB should remain
    assert set(filtered_totals.index) == {"TESCO", "BOB"}
    assert set(filtered_df["keyword"]) == {"TESCO", "BOB"}

    # Amounts unchanged for remaining groups
    assert filtered_totals.loc["TESCO"] == -30.0
    assert filtered_totals.loc["BOB"] == -40.0

# ---------------------------------------------------------------------------
# Integration test: hide overrides spoof
# ---------------------------------------------------------------------------

def test_hide_overrides_spoof(tmp_path):
    # Sample transactions
    df = pd.DataFrame({
        "description": ["AMAZON", "TESCO"],
        "amount": [-20.0, -30.0],
        "date": pd.to_datetime(["2024-01-01"] * 2),
    })

    # Hide file contains AMAZON
    hide_path = tmp_path / ".hide"
    hide_path.write_text("AMAZON")

    hidden_groups = load_hidden_groups(str(hide_path))

    # Spoof file tries to add 50 to AMAZON
    from src.tldr_bank.settings import load_spoof_adjustments
    spoof_path = tmp_path / "spoof.txt"
    spoof_path.write_text("AMAZON = +50\nTESCO = +10")
    spoofs = load_spoof_adjustments(str(spoof_path))

    km = KeywordManager(df, fuzzy_threshold=100)
    totals, df_labelled = km.run()

    # Apply spoof adjustments first
    for group, adj in spoofs.items():
        if group.upper() in hidden_groups:  # hidden groups are skipped
            continue
        if group in totals.index:
            totals.loc[group] += adj
        else:
            totals.loc[group] = adj

    # Filter DataFrame for hidden groups
    totals = totals[~totals.index.str.upper().isin(hidden_groups)]
    df_labelled = df_labelled[~df_labelled["keyword"].str.upper().isin(hidden_groups)]

    # AMAZON should be gone
    assert "AMAZON" not in totals.index
    assert "AMAZON" not in df_labelled["keyword"].values

    # TESCO should remain with spoof applied
    assert totals.loc["TESCO"] == -30.0 + 10.0