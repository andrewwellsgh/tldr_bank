from rich.console import Console
from rich.table import Table
import plotext as plt
import pandas as pd

class Reporter:
    def __init__(self, totals, df=None, show_all=False, truncate=10, income_mode=False, net_mode=False):
        self.totals = totals
        self.df = df
        self.show_all = show_all
        self.truncate = truncate
        self.income_mode = income_mode
        self.net_mode = net_mode
        self.console = Console()

    def run(self, no_chart=False):
        # --- Table ---
        if self.totals.empty:
            self.console.print("No data to display.")
        else:
            data_table = self.totals if self.show_all else self.totals.head(10)
            if self.income_mode:
                title = "Top Income Sources"
            elif self.net_mode:
                title = "Top Items by Net Value"
            else:
                title = "Top Costs"
            table = Table(title=title)
            table.add_column("#")
            table.add_column("Item")
            table.add_column("Total")
            for i, (k, v) in enumerate(data_table.items(), 1):
                table.add_row(str(i), k, f"{v:.2f}")
            self.console.print(table)

        # --- Chart ---
        if not no_chart and not self.totals.empty:
            if self.net_mode or self.income_mode:
                chart_data = self.totals.sort_values(ascending=False).head(5)
            else:
                chart_data = self.totals.abs().sort_values(ascending=False).head(5)
            labels = [k[:self.truncate] for k in chart_data.index]
            values = list(chart_data.values)
            plt.bar(labels, values)
            plt.title("Top 5")
            plt.xlabel("Item")
            plt.ylabel("Amount")
            plt.show()

        # --- Interactive inspection ---
        if self.df is not None and not self.df.empty:
            while True:
                choice = input("\nEnter the # of a keyword to see its transactions (or press Enter to finish): ").strip()
                if not choice:
                    break
                if not choice.isdigit() or int(choice) < 1 or int(choice) > len(self.totals):
                    print("Invalid selection, try again.")
                    continue
                idx = int(choice) - 1
                keyword = list(self.totals.index)[idx]
                print(f"\nTransactions for '{keyword}':")
                transactions = self.df[self.df['keyword'] == keyword].sort_values('date')
                for _, row in transactions.iterrows():
                    print(f"{row['date'].date()} | {row['description']} | {row['amount']:.2f}")

        self.console.print("\nAnd that's your bank - wrapped. 💳")