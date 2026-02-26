# src/tldr_bank/keyword_manager.py

import pandas as pd
from rapidfuzz import fuzz

class KeywordManager:
    def __init__(self, df, currency='GBP', fuzzy_threshold=100):
        """
        Args:
            df (pd.DataFrame): Must contain 'description' and 'amount'
            currency (str): Currency code
            fuzzy_threshold (int): 0-100, threshold for fuzzy grouping
        """
        self.df = df
        self.currency = currency
        self.fuzzy_threshold = fuzzy_threshold

    def _fuzzy_group(self, descriptions):
        """
        Group similar descriptions based on fuzzy matching.
        """
        mapping = {}
        groups = {}

        for d in descriptions:
            found = False
            for key in groups:
                if fuzz.ratio(d.lower(), key.lower()) >= self.fuzzy_threshold:
                    groups[key].append(d)
                    mapping[d] = key
                    found = True
                    break
            if not found:
                groups[d] = [d]
                mapping[d] = d
        return mapping

    def run(self, reverse=False):
        df = self.df.copy()
        df['description'] = df['description'].fillna('unknown')

        if self.fuzzy_threshold < 100:
            mapping = self._fuzzy_group(df['description'])
            df['keyword'] = df['description'].map(mapping)
        else:
            df['keyword'] = df['description'].str.lower().str.strip()

        totals = df.groupby('keyword')['amount'].sum().sort_values(ascending=not reverse)
        return totals