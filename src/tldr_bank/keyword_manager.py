import re

import pandas as pd
from rapidfuzz import fuzz

from .settings import load_group_patterns


class KeywordManager:
    """Groups transaction descriptions into labelled keywords and sums amounts.

    Pipeline:
        1. Extract a clean entity name from each raw description.
        2. Apply user-defined pattern->label rules from settings.
        3. Fuzzy-merge remaining similar entity names into a single canonical key.
        4. Group by keyword and sum amounts.
    """

    def __init__(self, df: pd.DataFrame, currency: str = "GBP", fuzzy_threshold: int = 90):
        self.df = df
        self.currency = currency
        self.fuzzy_threshold = fuzzy_threshold

    def _extract_entity(self, desc: str) -> str:
        """Reduce a raw transaction description to a clean merchant/entity name."""
        desc = str(desc).upper()

        # Strip date fragments like 12JAN24
        desc = re.sub(r"\b\d{1,2}[A-Z]{3}\d{2}\b", "", desc)
        # Strip standalone short numbers (card suffixes, reference numbers)
        desc = re.sub(r"\b\d{1,6}\b", "", desc)
        # Strip generic noise words
        desc = re.sub(
            r"\b(ONLINE|INTERNET|VIA MOBILE|PYMT|GROCERIES|TOPUP|PAYMENT|TRANSFER)\b",
            "",
            desc,
        )

        # Take the first comma-separated segment as the candidate
        parts = [p.strip() for p in desc.split(",") if p.strip()]
        candidate = parts[0] if parts else desc.strip()

        # Keep only letters and spaces
        candidate = re.sub(r"[^A-Z ]", "", candidate).strip()

        # Fall back to the full (cleaned) description if candidate is too short
        if len(candidate) < 3 or len(candidate.split()) == 1:
            candidate = re.sub(r"[^A-Z ]", "", desc).strip()

        return candidate

    def _fuzzy_group(self, entities: list[str]) -> dict[str, str]:
        """Map each entity to a canonical group key using fuzzy matching."""
        mapping: dict[str, str] = {}
        groups: dict[str, list[str]] = {}

        for entity in entities:
            if not entity:
                continue
            matched = False
            for key in groups:
                if fuzz.token_set_ratio(entity, key) >= self.fuzzy_threshold:
                    groups[key].append(entity)
                    mapping[entity] = key
                    matched = True
                    break
            if not matched:
                groups[entity] = [entity]
                mapping[entity] = entity

        return mapping

    def run(
        self, reverse: bool = False, income_mode: bool = False, net_mode: bool = False
    ) -> tuple[pd.Series, pd.DataFrame]:
        """Return (totals Series, labelled DataFrame).

        Args:
            reverse:     Reverse the default sort order.
            income_mode: Sort highest income first (ascending=False by default).
            net_mode:    Sort by net value (same ordering as income_mode).

        Returns:
            totals:      pd.Series indexed by keyword, values are summed amounts.
            df:          Copy of input DataFrame with 'entity' and 'keyword' columns.
        """
        df = self.df.copy()
        df["entity"] = df["description"].apply(self._extract_entity)

        # Apply user-defined pattern rules
        patterns = load_group_patterns()

        def apply_patterns(entity: str) -> str:
            for pattern, label in patterns:
                if pattern in entity.upper():
                    return label
            return entity

        df["entity"] = df["entity"].apply(apply_patterns)

        # Fuzzy-group whatever wasn't caught by explicit patterns
        mapping = self._fuzzy_group(df["entity"].tolist())
        df["keyword"] = df["entity"].map(mapping)

        totals = df.groupby("keyword")["amount"].sum()

        if net_mode or income_mode:
            totals = totals.sort_values(ascending=reverse)
        else:
            totals = totals.sort_values(ascending=not reverse)

        return totals, df
