#!/bin/bash

set -e

# =============================
# Create project structure
# =============================
mkdir -p src/tldr_bank
mkdir -p tests
mkdir -p csv_examples

# =============================
# pyproject.toml
# =============================
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "tldr_bank"
version = "0.1.0"
description = "Spotify-wrapped-style analysis for your bank CSVs"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [
    { include = "tldr_bank", from = "src" }
]

[tool.poetry.dependencies]
python = "^3.13"
pandas = "^2.1"
filelock = "^3.24"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"

[tool.poetry.scripts]
tldr_bank = "tldr_bank.main:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# =============================
# src/tldr_bank/security.py
# =============================
cat > src/tldr_bank/security.py << 'EOF'
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
EOF

# =============================
# src/tldr_bank/processor.py
# =============================
cat > src/tldr_bank/processor.py << 'EOF'
import os
import pandas as pd
from .security import SecurityCheck

class CSVProcessor:
    def __init__(self, folder='csv_examples'):
        self.folder = folder
        self.security = SecurityCheck()

    def run(self):
        all_files = [os.path.join(self.folder, f) for f in os.listdir(self.folder) if f.endswith('.csv')]
        df_list = []
        for f in all_files:
            df = pd.read_csv(f)
            df = self.security.run(df)
            df_list.append(df)
        if df_list:
            return pd.concat(df_list, ignore_index=True)
        return pd.DataFrame(columns=['date','description','amount'])
EOF

# =============================
# src/tldr_bank/keyword_manager.py
# =============================
cat > src/tldr_bank/keyword_manager.py << 'EOF'
import pandas as pd

class KeywordManager:
    def __init__(self, df):
        self.df = df

    def run(self):
        df = self.df.copy()
        df['keyword'] = df['description'].str.lower().str.strip()
        totals = df.groupby('keyword')['amount'].sum().sort_values(ascending=False)
        return totals
EOF

# =============================
# src/tldr_bank/reporter.py
# =============================
cat > src/tldr_bank/reporter.py << 'EOF'
class Reporter:
    def __init__(self, totals):
        self.totals = totals

    def run(self):
        print("Spending per keyword:")
        for k, v in self.totals.items():
            print(f"{k}: {v:.2f}")
        total_days = self.totals.index.size
        print(f"Total keywords: {total_days}")
EOF

# =============================
# src/tldr_bank/main.py
# =============================
cat > src/tldr_bank/main.py << 'EOF'
import argparse
from .processor import CSVProcessor
from .keyword_manager import KeywordManager
from .reporter import Reporter

def main():
    parser = argparse.ArgumentParser(description="tldr_bank CLI")
    parser.add_argument('--folder', default='csv_examples', help='CSV folder')
    args = parser.parse_args()

    processor = CSVProcessor(folder=args.folder)
    df = processor.run()

    km = KeywordManager(df)
    totals = km.run()

    reporter = Reporter(totals)
    reporter.run()

if __name__ == "__main__":
    main()
EOF

# =============================
# tests/test_security.py
# =============================
cat > tests/test_security.py << 'EOF'
import pandas as pd
import pytest
from src.tldr_bank.security import SecurityCheck

sc = SecurityCheck()

def test_standard_headers():
    df = pd.DataFrame({'date':['2026-01-01'], 'description':['Coffee'], 'amount':[3]})
    result = sc.run(df)
    assert 'amount' in result.columns

def test_nonstandard_headers():
    df = pd.DataFrame({'TransactionDate':['2026-01-01'], 'MerchantName':['Coffee'], 'Value':[3]})
    result = sc.run(df)
    assert 'amount' in result.columns
    assert 'date' in result.columns
    assert 'description' in result.columns

def test_invalid_missing_column():
    df = pd.DataFrame({'random':[1,2]})
    with pytest.raises(ValueError):
        sc.run(df)

def test_partial_invalid_rows():
    df = pd.DataFrame({'date':['bad','2026-01-02'], 'description':['Coffee', None], 'amount':['NaN','20']})
    result = sc.run(df)
    assert len(result) == 1
EOF

# =============================
# Done
# =============================
echo "Setup complete. Now run:"
echo "  poetry install"
echo "  poetry run tldr_bank --folder csv_examples"