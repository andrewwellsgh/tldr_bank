from rich.console import Console
from rich.table import Table
import plotext as plt
import pandas as pd

class Reporter:
    def __init__(self, totals, df=None, show_all=False, truncate=10, income_mode=False):
        self.totals = totals
        self.df = df
        self.show_all = show_all
        self.truncate = truncate
        self.income_mode = income_mode
        self.console = Console()

    def run(self, no_chart=False):
        # --- Table ---
        if self.totals.empty:
            self.console.print("No data to display.")
        else:
            data_table = self.totals if self.show_all else self.totals.head(5)
            table = Table(title="Top Costs")
            table.add_column("#")
            table.add_column("Thing")
            table.add_column("Total")
            for i, (k, v) in enumerate(data_table.items(), 1):
                table.add_row(str(i), k, f"{v:.2f}")
            self.console.print(table)

        # --- Insights ---
        if self.df is not None and not self.df.empty:
            df = self.df
            if self.income_mode:
                filtered = df[df['amount'] > 0]
            else:
                filtered = df[df['amount'] < 0]

            if not filtered.empty:
                months = filtered.groupby(filtered['date'].dt.to_period("M"))['amount'].sum()
                years = filtered.groupby(filtered['date'].dt.year)['amount'].sum()
                largest_expense = filtered.loc[filtered['amount'].idxmin() if not self.income_mode else filtered['amount'].idxmax()]
                smallest_expense = filtered.loc[filtered['amount'].idxmax() if not self.income_mode else filtered['amount'].idxmin()]
                most_expensive_thing = filtered.groupby('description')['amount'].sum().idxmin() if not self.income_mode else filtered.groupby('description')['amount'].sum().idxmax()
                cheapest_thing = filtered.groupby('description')['amount'].sum().idxmax() if not self.income_mode else filtered.groupby('description')['amount'].sum().idxmin()
                most_bought = filtered['description'].value_counts().idxmax()
                least_bought = filtered['description'].value_counts().idxmin()

                if not months.empty:
                    self.console.print(f"\nMost Expensive Month: {months.idxmin() if not self.income_mode else months.idxmax()} ({months.min() if not self.income_mode else months.max():.2f})")
                    self.console.print(f"Cheapest Month: {months.idxmax() if not self.income_mode else months.idxmin()} ({months.max() if not self.income_mode else months.min():.2f})")
                if not years.empty:
                    self.console.print(f"\nMost Expensive Year: {years.idxmin() if not self.income_mode else years.idxmax()} ({years.min() if not self.income_mode else years.max():.2f})")
                    self.console.print(f"Cheapest Year: {years.idxmax() if not self.income_mode else years.idxmin()} ({years.max() if not self.income_mode else years.min():.2f})")

                self.console.print(f"\nLargest Expense: {largest_expense['description']} ({largest_expense['amount']:.2f})")
                self.console.print(f"Smallest Expense: {smallest_expense['description']} ({smallest_expense['amount']:.2f})")
                self.console.print(f"\nMost Expensive Thing: {most_expensive_thing}")
                self.console.print(f"Cheapest Thing: {cheapest_thing}")
                self.console.print(f"Most Bought Thing: {most_bought}")
                self.console.print(f"Least Bought Thing: {least_bought}")

        # --- Chart ---
        if not no_chart and not self.totals.empty:
            chart_data = self.totals.abs().sort_values(ascending=False).head(5)
            labels = [k[:self.truncate] for k in chart_data.index]
            values = list(chart_data.values)
            plt.bar(labels, values)
            plt.title("Top 5 Expenses / Income (absolute)")
            plt.xlabel("Item")
            plt.ylabel("Amount")
            plt.show()

        self.console.print("\nAnd that's your bank - wrapped. 💳")
