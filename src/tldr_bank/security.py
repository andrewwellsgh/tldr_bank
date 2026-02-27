import pandas as pd
import re


class SecurityCheck:
    """Validates and normalises raw CSV DataFrames into a standard schema.

    Attempts to detect date, description, and amount columns by name hints
    first, then by scoring column content if hints fail.
    """

    required_fields = ["date", "description", "amount"]
    header_hints = {
        "date": ["date", "transactiondate", "posted"],
        "description": ["desc", "description", "merchant", "type", "label"],
        "amount": ["value", "amount", "amt", "debit", "credit"],
    }

    def guess_columns(self, df: pd.DataFrame) -> dict:
        """Return a mapping of {standard_field: original_column_name}."""
        df_columns = [c.strip() for c in df.columns]
        mapping = {}

        # Pass 1: name-hint matching
        for field, hints in self.header_hints.items():
            for hint in hints:
                for col in df_columns:
                    if hint.lower() in col.lower():
                        mapping[field] = col
                        break
                if field in mapping:
                    break

        # Pass 2: content-scoring for any fields still missing
        sample = df.head(10)
        for field in self.required_fields:
            if field in mapping:
                continue
            already_claimed = set(mapping.values())
            scores = {}
            for col in df_columns:
                if col in already_claimed:
                    continue
                col_values = sample[col]
                if field == "date":
                    scores[col] = col_values.apply(
                        lambda x: pd.notna(pd.to_datetime(x, errors="coerce"))
                    ).mean()
                elif field == "amount":
                    cleaned = (
                        col_values.astype(str)
                        .str.replace(",", "", regex=False)
                        .str.replace(r"[^\d\.\-]", "", regex=True)
                    )
                    scores[col] = cleaned.apply(
                        lambda x: bool(re.match(r"^-?\d+(\.\d+)?$", x.strip()))
                    ).mean()
                elif field == "description":
                    scores[col] = col_values.apply(lambda x: isinstance(x, str)).mean()

            if scores:
                best_col = max(scores, key=scores.get)
                if scores[best_col] > 0.5:
                    mapping[field] = best_col

        missing = [f for f in self.required_fields if f not in mapping]
        if missing:
            raise ValueError(f"Cannot identify required columns: {missing}")
        return mapping

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalise a raw CSV DataFrame.

        Returns a DataFrame with columns: date (datetime), description (str),
        amount (float).  Rows with unparseable dates or amounts are dropped.
        """
        mapping = self.guess_columns(df)
        df = df.rename(columns={v: k for k, v in mapping.items()})

        df["amount"] = pd.to_numeric(
            df["amount"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(r"[^\d\.\-]", "", regex=True),
            errors="coerce",
        )
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce",
            format="mixed",  # prevents the inference warning
        )
        df["description"] = df["description"].fillna("unknown").astype(str)
        df = df.dropna(subset=["amount", "date"])
        return df.reset_index(drop=True)
