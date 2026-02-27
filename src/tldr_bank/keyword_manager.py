import pandas as pd
from rapidfuzz import fuzz
import re

class KeywordManager:
    def __init__(self, df, currency='GBP', fuzzy_threshold=90):
        self.df = df
        self.currency = currency
        self.fuzzy_threshold = fuzzy_threshold

    def _extract_entity(self, desc: str) -> str:
        desc = str(desc).upper()
        # Remove numeric codes, dates, and generic words
        desc = re.sub(r'\b\d{1,6}\b', '', desc)  # short numeric codes
        desc = re.sub(r'\b\d{1,2}[A-Z]{3}\d{2}\b', '', desc)  # date codes like 21FEB24
        desc = re.sub(r'\bONLINE|INTERNET|VIA MOBILE|PYMT|GROCERIES|TOPUP|PAYMENT|TRANSFER\b', '', desc)
        # Split by comma and strip
        parts = [p.strip() for p in desc.split(',') if p.strip()]
        if parts:
            candidate = parts[0]
        else:
            candidate = desc.strip()

        # Remove non-alphabetic junk
        candidate = re.sub(r'[^A-Z ]', '', candidate).strip()

        # If too short or single letter, fallback to full cleaned description
        if len(candidate) < 3 or len(candidate.split()) == 1:
            candidate = re.sub(r'[^A-Z ]', '', desc).strip()

        return candidate

    def _fuzzy_group(self, entities):
        mapping = {}
        groups = {}
        for e in entities:
            if not e:  # skip empty or invalid entities
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

    def run(self, reverse=False, income_mode=False):
        df = self.df.copy()
        df['entity'] = df['description'].apply(self._extract_entity)
        mapping = self._fuzzy_group(df['entity'])
        df['keyword'] = df['entity'].map(mapping)

        if income_mode:
            totals = df.groupby('keyword')['amount'].sum().sort_values(ascending=reverse)
        else:
            totals = df.groupby('keyword')['amount'].sum().sort_values(ascending=not reverse)

        return totals

