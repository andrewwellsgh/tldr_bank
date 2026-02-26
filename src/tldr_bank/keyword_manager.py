import pandas as pd

class KeywordManager:
    def __init__(self, df, currency='GBP'):
        self.df = df
        self.currency = currency

    def run(self, reverse=False):
        df = self.df.copy()
        df['keyword'] = df['description'].str.lower().str.strip()
        totals = df.groupby('keyword')['amount'].sum().sort_values(ascending=not reverse)
        return totals
