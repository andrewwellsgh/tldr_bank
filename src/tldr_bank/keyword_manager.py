import pandas as pd

class KeywordManager:
    def __init__(self, df):
        self.df = df

    def run(self):
        df = self.df.copy()
        df['keyword'] = df['description'].str.lower().str.strip()
        totals = df.groupby('keyword')['amount'].sum().sort_values(ascending=False)
        return totals
