import re
import pandas as pd


class SecurityCheck:
    required_fields = ["date", "description", "amount"]
    header_hints = {
        "date": ["date", "transactiondate", "posted"],
        "description": ["desc", "description", "merchant", "type", "label", "details"],
        "amount": ["value", "amount", "amt"],
    }

    def guess_columns(self, df: pd.DataFrame) -> dict:
        """Map standard fields to CSV columns. Excludes debit/credit handling."""
        df_columns = [c.strip() for c in df.columns]
        mapping = {}

        # Name hints
        for field, hints in self.header_hints.items():
            for hint in hints:
                for col in df_columns:
                    if hint.lower() in col.lower():
                        mapping[field] = col
                        break
                if field in mapping:
                    break

        # Content scoring for missing
        sample = df.head(10)
        for field in ["date", "description"]:
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
                elif field == "description":
                    scores[col] = col_values.apply(lambda x: isinstance(x, str)).mean()

            if scores:
                best_col = max(scores, key=scores.get)
                if scores[best_col] > 0.5:
                    mapping[field] = best_col

        missing = [f for f in ["date", "description"] if f not in mapping]
        if missing:
            raise ValueError(f"Cannot identify required columns: {missing}")

        return mapping

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize CSV to date/description/amount, handling debit/credit columns."""

        mapping = self.guess_columns(df)
        df = df.rename(columns={v: k for k, v in mapping.items()})

       # --- Amount handling ---
        columns_lower = [c.lower() for c in df.columns]

        if "amount" not in df.columns:
            if "debit" in columns_lower and "credit" in columns_lower:
                df["amount"] = df[df.columns[columns_lower.index("credit")]].fillna(0) - \
                            df[df.columns[columns_lower.index("debit")]].fillna(0)
            elif "debit" in columns_lower:
                df["amount"] = -df[df.columns[columns_lower.index("debit")]].fillna(0)
            elif "credit" in columns_lower:
                df["amount"] = df[df.columns[columns_lower.index("credit")]].fillna(0)
            else:
                raise ValueError("Cannot identify amount column: no amount/debit/credit found")
    
        # Clean amount
        df["amount"] = pd.to_numeric(
            df["amount"].astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(r"[^\d\.\-]", "", regex=True),
            errors="coerce",
        )

        # Parse date
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Clean description
        df["description"] = df["description"].fillna("unknown").astype(str)

        # Drop rows where amount/date failed parsing
        df = df.dropna(subset=["amount", "date"])

        return df.reset_index(drop=True)