#!/bin/bash
# ================================================
# TLDR_BANK Fix & Installer
# Fixes: chart crash, table + insights display
# ================================================

echo "Updating tldr_bank files..."

# --- 1️⃣ Update reporter.py ---
mkdir -p src/tldr_bank
cat > src/tldr_bank/reporter.py << 'EOF'
from rich.console import Console
from rich.table import Table
import plotext as plt
import pandas as pd

class Reporter:
    def __init__(self, totals, df=None, show_all=False, truncate=10):
        self.totals = totals
        self.df = df
        self.show_all = show_all
        self.truncate = truncate
        self.console = Console()

    def run(self, no_chart=False):
        # --- Table ---
        if self.totals.empty:
            self.console.print("No data to display.")
        else:
            data_table = self.totals if self.show_all else self.totals.head(5)
            table = Table(title="Top Costs / Income")
            table.add_column("#")
            table.add_column("Thing")
            table.add_column("Total")
            for i, (k, v) in enumerate(data_table.items(), 1):
                table.add_row(str(i), k, f"{v:.2f}")
            self.console.print(table)

        # --- Insights ---
        if self.df is not None and not self.df.empty:
            df = self.df
            months = df.groupby(df['date'].dt.to_period("M"))['amount'].sum()
            years = df.groupby(df['date'].dt.year)['amount'].sum()
            largest = df.loc[df['amount'].idxmax()]
            smallest = df.loc[df['amount'].idxmin()]
            most_bought = df['description'].value_counts().idxmax()
            least_bought = df['description'].value_counts().idxmin()
            most_expensive_thing = df.groupby('description')['amount'].sum().idxmax()
            cheapest_thing = df.groupby('description')['amount'].sum().idxmin()

            if not months.empty:
                self.console.print(f"\nMost Expensive Month: {months.idxmax()} ({months.max():.2f})")
                self.console.print(f"Cheapest Month: {months.idxmin()} ({months.min():.2f})")
            if not years.empty:
                self.console.print(f"\nMost Expensive Year: {years.idxmax()} ({years.max():.2f})")
                self.console.print(f"Cheapest Year: {years.idxmin()} ({years.min():.2f})")

            self.console.print(f"\nLargest Expense: {largest['description']} ({largest['amount']:.2f})")
            self.console.print(f"Smallest Expense: {smallest['description']} ({smallest['amount']:.2f})")
            self.console.print(f"\nMost Expensive Thing: {most_expensive_thing}")
            self.console.print(f"Cheapest Thing: {cheapest_thing}")
            self.console.print(f"Most Bought Thing: {most_bought}")
            self.console.print(f"Least Bought Thing: {least_bought}")

        # --- Chart ---
        if not no_chart and not self.totals.empty:
            chart_data = self.totals.abs().sort_values(ascending=False).head(5)
            labels = [k[:self.truncate] for k in chart_data.index]
            values = list(chart_data.values)
            # Removed plt.clt() to prevent clearing terminal
            plt.bar(labels, values)
            plt.title("Top 5 Expenses / Income (absolute)")
            plt.xlabel("Item")
            plt.ylabel("Amount")
            plt.show()  # ✅ correct method

        self.console.print("\nAnd that's your bank - wrapped. 💳")
EOF

# --- 2️⃣ Update README.md ---
cat > README.md << 'EOF'
# TLDR Bank

Terminal-based CLI to summarize and visualize your bank transactions.

## Installation

```bash
git clone <your_repo>
cd <your_repo>
pip install -r requirements.txt