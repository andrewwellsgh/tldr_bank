import pytest

from src.tldr_bank.settings import load_group_patterns


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
