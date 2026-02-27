import pandas as pd
import pytest

from src.tldr_bank.keyword_manager import KeywordManager


def make_df(descriptions, amounts):
    return pd.DataFrame({
        "description": descriptions,
        "amount": amounts,
        "date": pd.to_datetime(["2024-01-01"] * len(descriptions)),
    })


# ---------------------------------------------------------------------------
# _extract_entity
# ---------------------------------------------------------------------------

def test_extract_entity_uppercases(tmp_path):
    km = KeywordManager(make_df([], []))
    assert km._extract_entity("coffee shop") == km._extract_entity("COFFEE SHOP")


def test_extract_entity_strips_numbers():
    km = KeywordManager(make_df([], []))
    result = km._extract_entity("6969 15JAN24 AMAZON LONDON GB")
    assert "6969" not in result
    assert "AMAZON" in result


def test_extract_entity_strips_noise_words():
    km = KeywordManager(make_df([], []))
    result = km._extract_entity("ASDA GROCERIES ONLINE INTERNET GB")
    assert "ONLINE" not in result
    assert "INTERNET" not in result
    assert "ASDA" in result


def test_extract_entity_takes_first_csv_segment():
    km = KeywordManager(make_df([], []))
    result = km._extract_entity("STARBUCKS, HIGH STREET, EASTBOURNE, GB")
    assert "STARBUCKS" in result


def test_extract_entity_strips_punctuation():
    km = KeywordManager(make_df([], []))
    result = km._extract_entity("WELLS D & J")
    assert "&" not in result
    assert "WELLS D  J" == result or "WELLS D J" in result


# ---------------------------------------------------------------------------
# _fuzzy_group
# ---------------------------------------------------------------------------

def test_fuzzy_group_merges_similar():
    km = KeywordManager(make_df([], []), fuzzy_threshold=80)
    # These differ only by a number suffix — token_set_ratio will be 100
    mapping = km._fuzzy_group(["STARBUCKS 123", "STARBUCKS 456"])
    assert len(set(mapping.values())) == 1


def test_fuzzy_group_keeps_distinct():
    km = KeywordManager(make_df([], []), fuzzy_threshold=90)
    mapping = km._fuzzy_group(["AMAZON", "SAINSBURYS"])
    assert len(set(mapping.values())) == 2


def test_fuzzy_group_ignores_empty_strings():
    km = KeywordManager(make_df([], []))
    mapping = km._fuzzy_group(["", "AMAZON", ""])
    assert "" not in mapping


# ---------------------------------------------------------------------------
# run() — expense mode (default)
# ---------------------------------------------------------------------------

def test_run_returns_series_and_dataframe():
    df = make_df(["AMAZON", "ASDA"], [-10.0, -20.0])
    km = KeywordManager(df)
    totals, labelled = km.run()
    assert isinstance(totals, pd.Series)
    assert isinstance(labelled, pd.DataFrame)
    assert "keyword" in labelled.columns


def test_run_expense_sorted_most_negative_first():
    df = make_df(["AMAZON", "ASDA", "TESCO"], [-5.0, -50.0, -20.0])
    km = KeywordManager(df)
    totals, _ = km.run()
    assert totals.iloc[0] <= totals.iloc[-1]


def test_run_sums_amounts_per_keyword():
    df = make_df(["AMAZON", "AMAZON", "ASDA"], [-10.0, -15.0, -20.0])
    km = KeywordManager(df, fuzzy_threshold=100)
    totals, _ = km.run()
    # Both AMAZON rows should be grouped together
    amazon_total = totals[totals.index.str.contains("AMAZON", case=False)]
    assert not amazon_total.empty
    assert amazon_total.sum() == pytest.approx(-25.0)


# ---------------------------------------------------------------------------
# run() — income mode
# ---------------------------------------------------------------------------

def test_run_income_mode_sorted_highest_first():
    df = make_df(["EMPLOYER", "BENEFIT", "BONUS"], [1000.0, 200.0, 500.0])
    km = KeywordManager(df)
    totals, _ = km.run(income_mode=True)
    assert totals.iloc[0] >= totals.iloc[-1]


# ---------------------------------------------------------------------------
# run() — net mode
# ---------------------------------------------------------------------------

def test_run_net_mode_includes_negative_net():
    df = make_df(
        ["WELLS D J", "WELLS D J", "EMPLOYER"],
        [-500.0, -200.0, 1000.0],
    )
    km = KeywordManager(df, fuzzy_threshold=100)
    totals, _ = km.run(net_mode=True)
    # At least one group should be negative
    assert (totals < 0).any()


def test_run_net_mode_sums_both_directions():
    df = make_df(
        ["PARENTS", "PARENTS", "PARENTS"],
        [-300.0, 100.0, -50.0],
    )
    km = KeywordManager(df, fuzzy_threshold=100)
    totals, _ = km.run(net_mode=True)
    parents = totals[totals.index.str.contains("PARENTS", case=False)]
    assert parents.sum() == pytest.approx(-250.0)


# ---------------------------------------------------------------------------
# Pattern matching (no settings file — patterns passed via mock)
# ---------------------------------------------------------------------------

def test_pattern_matching_groups_descriptions(monkeypatch):
    import src.tldr_bank.keyword_manager as km_module
    monkeypatch.setattr(km_module, "load_group_patterns", lambda: [("WELLS D J", "PARENTS")])

    df = make_df(["WELLS D J RENT", "WELLS D J LOAN"], [-456.0, -100.0])
    km = KeywordManager(df, fuzzy_threshold=100)
    totals, labelled = km.run()
    assert "PARENTS" in labelled["keyword"].values


def test_ampersand_in_pattern_normalised(monkeypatch):
    """WELLS D & J in settings should match WELLS D  J entity after stripping &."""
    import src.tldr_bank.keyword_manager as km_module
    # Simulate what load_group_patterns returns after normalisation
    monkeypatch.setattr(km_module, "load_group_patterns", lambda: [("WELLS D  J", "PARENTS")])

    df = make_df(["WELLS D & J VIA MOBILE PYMT"], [300.0])
    km = KeywordManager(df)
    _, labelled = km.run()
    assert "PARENTS" in labelled["keyword"].values
