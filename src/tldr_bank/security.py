import pandas as pd
import re

class SecurityCheck:
    """Robust CSV validator and smart column guesser."""

    required_fields = ['date', 'description', 'amount']

    header_hints = {
        'date': ['date', 'transactiondate', 'posted'],
        'description': ['desc', 'description', 'merchant', 'type', 'label'],
        'amount': ['value', 'amount', 'amt', 'debit', 'credit']
    }

    def guess_columns(self, df: pd.DataFrame):
        df_columns = [c.strip() for c in df.columns]
        mapping = {}

        # --- header hints first ---
        for field, hints in self.header_hints.items():
            for hint in hints:
                for c in df_columns:
                    if hint.lower() in c.lower():
                        mapping[field] = c
                        break
                if field in mapping:
                    break

        # --- fallback: sample inspection ---
        sample = df.head(10)
        for field in self.required_fields:
            if field not in mapping:
                scores = {}
                for c in df_columns:
                    col_values = sample[c]
                    if field == 'date':
                        scores[c] = col_values.apply(lambda x: pd.notna(pd.to_datetime(x, errors='coerce'))).mean()
                    elif field == 'amount':
                        s = col_values.astype(str).str.replace(',','').str.replace(r'[^\d\.-]', '', regex=True)
                        scores[c] = s.apply(lambda x: bool(re.match(r'^-?\d+(\.\d+)?$', x.strip()))).mean()
                    elif field == 'description':
                        scores[c] = col_values.apply(lambda x: isinstance(x,str)).mean()
                best_col = max(scores, key=scores.get)
                if scores[best_col] > 0.5:
                    mapping[field] = best_col

        missing = [f for f in self.required_fields if f not in mapping]
        if missing:
            raise ValueError(f"Cannot guess columns for: {missing}")

        return mapping

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        mapping = self.guess_columns(df)
        df = df.rename(columns={v: k for k, v in mapping.items()})
        df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',','').str.replace(r'[^\d\.-]', '', regex=True), errors='coerce')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['description'] = df['description'].fillna('unknown').astype(str)
        df = df.dropna(subset=['amount','date'])
        return df
