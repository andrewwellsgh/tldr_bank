import pandas as pd
from rapidfuzz import fuzz
import re
from .settings import load_group_patterns  # moved here

class KeywordManager:
    def __init__(self, df, currency='GBP', fuzzy_threshold=90):
        self.df = df
        self.currency = currency
        self.fuzzy_threshold = fuzzy_threshold

    def _extract_entity(self, desc: str) -> str:
        desc = str(desc).upper()
        desc = re.sub(r'\b\d{1,6}\b', '', desc)
        desc = re.sub(r'\b\d{1,2}[A-Z]{3}\d{2}\b', '', desc)
        desc = re.sub(r'\bONLINE|INTERNET|VIA MOBILE|PYMT|GROCERIES|TOPUP|PAYMENT|TRANSFER\b', '', desc)
        parts = [p.strip() for p in desc.split(',') if p.strip()]
        candidate = parts[0] if parts else desc.strip()
        candidate = re.sub(r'[^A-Z ]', '', candidate).strip()
        if len(candidate) < 3 or len(candidate.split()) == 1:
            candidate = re.sub(r'[^A-Z ]', '', desc).strip()
        return candidate

    def _fuzzy_group(self, entities):
        mapping = {}
        groups = {}
        for e in entities:
            if not e:
                continue
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

    def run(self, reverse=False, income_mode=False, net_mode=False):
            df = self.df.copy()
            df['entity'] = df['description'].apply(self._extract_entity)
            patterns = load_group_patterns()
            print("Loaded patterns:", patterns)
            print("Sample entities:", df['entity'].head(20).tolist())
            patterns = load_group_patterns()
            def apply_patterns(entity):
                for pattern, label in patterns:
                    if pattern in entity.upper():
                        return label
                return entity
            df['entity'] = df['entity'].apply(apply_patterns)
            mapping = self._fuzzy_group(df['entity'])
            df['keyword'] = df['entity'].map(mapping)

            totals = df.groupby('keyword')['amount'].sum()
            if net_mode or income_mode:
                totals = totals.sort_values(ascending=reverse)
            else:
                totals = totals.sort_values(ascending=not reverse)

            return totals, df