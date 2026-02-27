import re
import os

# Looks two levels up from src/tldr_bank/ → project root
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".custom_group_settings")


def load_group_patterns(settings_file: str = SETTINGS_FILE) -> list[tuple[str, str]]:
    """Load grouping rules from the settings file.

    Each line can be:
        pattern = LABEL     ->  transactions matching pattern are labelled LABEL
        pattern             ->  pattern is used as its own label

    Patterns are normalised the same way _extract_entity does (upper-case,
    strip non-alpha characters) so that e.g. "WELLS D & J" matches the entity
    "WELLS D  J" produced after stripping punctuation.

    Returns a list of (normalised_pattern, label) tuples.
    """
    patterns = []
    if not os.path.exists(settings_file):
        return patterns

    with open(settings_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                pattern, label = [p.strip().upper() for p in line.split("=", 1)]
            else:
                pattern = label = line.upper()

            # Normalise: strip non-alpha chars to match _extract_entity output
            pattern = re.sub(r"[^A-Z ]", "", pattern).strip()
            if pattern:
                patterns.append((pattern, label))

    return patterns
