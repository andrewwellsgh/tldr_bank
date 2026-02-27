import pandas as pd
import pytest

from src.tldr_bank.settings import load_group_patterns
from src.tldr_bank.settings import load_spoof_adjustments


@pytest.fixture
def settings_file(tmp_path):
    def _write(content: str) -> str:
        path = tmp_path / ".custom_group_settings"
        path.write_text(content)
        return str(path)
    return _write


def test_missing_file_returns_empty(tmp_path):
    result = load_group_patterns(str(tmp_path / "nonexistent"))
    assert result == []


def test_empty_file_returns_empty(settings_file):
    assert load_group_patterns(settings_file("")) == []


def test_comment_lines_skipped(settings_file):
    assert load_group_patterns(settings_file("# this is a comment\n")) == []


def test_blank_lines_skipped(settings_file):
    assert load_group_patterns(settings_file("\n\n\n")) == []


def test_pattern_with_label(settings_file):
    patterns = load_group_patterns(settings_file("wells d j = PARENTS\n"))
    assert len(patterns) == 1
    pattern, label = patterns[0]
    assert pattern == "WELLS D J"
    assert label == "PARENTS"


def test_pattern_without_label_uses_itself(settings_file):
    patterns = load_group_patterns(settings_file("DWP\n"))
    pattern, label = patterns[0]
    assert pattern == label == "DWP"


def test_ampersand_stripped_from_pattern(settings_file):
    patterns = load_group_patterns(settings_file("wells d & j = PARENTS\n"))
    pattern, label = patterns[0]
    assert "&" not in pattern
    assert "WELLS D" in pattern
    assert label == "PARENTS"


def test_multiple_patterns_loaded(settings_file):
    content = "wells d j = PARENTS\nINFINITE INK = ALEX TATTOO\nDWP\n"
    assert len(load_group_patterns(settings_file(content))) == 3


def test_patterns_are_uppercased(settings_file):
    pattern, label = load_group_patterns(settings_file("amazon = shopping\n"))[0]
    assert pattern == pattern.upper()
    assert label == label.upper()


def test_empty_pattern_after_stripping_skipped(settings_file):
    assert load_group_patterns(settings_file("& = SOMETHING\n")) == []

def test_load_spoof_adjustments_basic(tmp_path):
    file = tmp_path / "spoof.txt"
    file.write_text("""
    PARENTS = +200
    AMAZON = -50.5
    # comment line
    INVALID LINE
    WELLS = 100
    """)
    
    adjustments = load_spoof_adjustments(str(file))
    
    assert adjustments["PARENTS"] == 200
    assert adjustments["AMAZON"] == -50.5
    assert adjustments["WELLS"] == 100
    # lines without "=" are ignored
    assert "INVALID LINE" not in adjustments

def test_load_spoof_adjustments_empty_or_missing(tmp_path):
    file = tmp_path / "empty.txt"
    file.write_text("")
    adjustments = load_spoof_adjustments(str(file))
    assert adjustments == {}

    # missing file
    adjustments2 = load_spoof_adjustments(str(tmp_path / "nonexistent.txt"))
    assert adjustments2 == {}

def test_apply_spoof_adjustments(tmp_path):
    totals = pd.Series({
        "PARENTS": -1500.0,
        "AMAZON": -300.0
    })

    # Create a spoof file
    file = tmp_path / "spoof.txt"
    file.write_text("""
    PARENTS = +200
    AMAZON = -50
    NEW_GROUP = +500
    """)

    spoofs = load_spoof_adjustments(str(file))

    # Apply adjustments
    for group, adjustment in spoofs.items():
        if group in totals.index:
            totals.loc[group] += adjustment
        else:
            totals.loc[group] = adjustment

    assert totals["PARENTS"] == -1300  # -1500 + 200
    assert totals["AMAZON"] == -350    # -300 + -50
    assert totals["NEW_GROUP"] == 500  # added new group