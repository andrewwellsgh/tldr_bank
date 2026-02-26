#!/bin/bash

# Update TLDR Bank KeywordManager with entity-based grouping

FILE="src/tldr_bank/keyword_manager.py"

cat > "$FILE" << 'EOF'
import pandas as pd
from rapidfuzz import fuzz
import re

class KeywordManager:
    def __init__(self, df, fuzzy_threshold=90):
        """
        Args:
            df (pd.DataFrame): Must contain 'description' and 'amount'
            fuzzy_threshold (int): 0-100, threshold for fuzzy grouping
        """
        self.df = df
        self.fuzzy_threshold = fuzzy_threshold

    def _extract_entity(self, desc: str) -> str:
        desc = str(desc).upper()
        # Remove numeric codes, dates, and generic words
        desc = re.sub(r'\b\d{1,6}\b', '', desc)
        desc = re.sub(r'\b\d{1,2}[A-Z]{3}\d{2}\b', '', desc)
        desc = re.sub(r'\bONLINE|INTERNET|VIA MOBILE|PYMT|GROCERIES|TOPUP|PAYMENT|TRANSFER\b', '', desc)
        # Split by comma and strip
        parts = [p.strip() for p in desc.split(',') if p.strip()]
        if parts:
            return parts[0]
        return desc.strip()

    def _fuzzy_group(self, entities):
        mapping = {}
        groups = {}
        for e in entities:
            found = False
            for key in groups:
                if fuzz.token_set_ratio(e, key) >= self.fuzzy_threshold:
                    groups[key].append(e)
                    mapping[e] = key
                    found = True
                    break
            if not found:
                groups[e] = [e]
                mapping[e] = e
        return mapping

    def run(self, reverse=False):
        df = self.df.copy()
        df['entity'] = df['description'].apply(self._extract_entity)

        # Apply fuzzy grouping to extracted entities
        mapping = self._fuzzy_group(df['entity'])
        df['keyword'] = df['entity'].map(mapping)

        totals = df.groupby('keyword')['amount'].sum().sort_values(ascending=not reverse)
        return totals
EOF

echo "KeywordManager has been updated with entity-based grouping."