from unittest.mock import patch

import pandas as pd
import pytest

from src.tldr_bank.reporter import Reporter


def make_totals(data):
    return pd.Series(data)


def make_df(keywords, amounts):
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01"] * len(keywords)),
        "description": [f"desc_{k}" for k in keywords],
        "amount": amounts,
        "keyword": keywords,
    })


def test_empty_totals_no_crash():
    reporter = Reporter(pd.Series(dtype=float))
    with patch("builtins.input", return_value=""):
        reporter.run(no_chart=True)


def test_expense_mode_flags():
    reporter = Reporter(make_totals({"AMAZON": -50.0}))
    assert not reporter.income_mode and not reporter.net_mode


def test_income_mode_flag():
    assert Reporter(make_totals({"EMPLOYER": 1000.0}), income_mode=True).income_mode


def test_net_mode_flag():
    assert Reporter(make_totals({"PARENTS": -200.0}), net_mode=True).net_mode


def test_show_all_false_limits_to_10():
    totals = make_totals({f"item_{i}": -float(i) for i in range(1, 20)})
    reporter = Reporter(totals, show_all=False)
    assert len(totals if reporter.show_all else totals.head(10)) == 10


def test_show_all_true_shows_everything():
    totals = make_totals({f"item_{i}": -float(i) for i in range(1, 20)})
    reporter = Reporter(totals, show_all=True)
    assert len(totals if reporter.show_all else totals.head(10)) == 19


def test_interactive_inspect_enter_exits():
    reporter = Reporter(make_totals({"AMAZON": -50.0}), df=make_df(["AMAZON"], [-50.0]))
    with patch("builtins.input", return_value=""):
        reporter._interactive_inspect()


def test_interactive_inspect_valid_choice(capsys):
    reporter = Reporter(
        make_totals({"AMAZON": -50.0, "ASDA": -30.0}),
        df=make_df(["AMAZON", "ASDA"], [-50.0, -30.0]),
    )
    with patch("builtins.input", side_effect=["1", ""]):
        reporter._interactive_inspect()
    assert "AMAZON" in capsys.readouterr().out


def test_interactive_inspect_invalid_choice(capsys):
    reporter = Reporter(make_totals({"AMAZON": -50.0}), df=make_df(["AMAZON"], [-50.0]))
    with patch("builtins.input", side_effect=["99", "abc", ""]):
        reporter._interactive_inspect()
    assert "Invalid" in capsys.readouterr().out


def test_run_no_crash():
    reporter = Reporter(
        make_totals({"AMAZON": -50.0, "ASDA": -30.0}),
        df=make_df(["AMAZON", "ASDA"], [-50.0, -30.0]),
    )
    with patch("builtins.input", return_value=""):
        reporter.run(no_chart=True)
