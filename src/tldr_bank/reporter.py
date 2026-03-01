import pandas as pd
import plotext as plt
from rich.console import Console
from rich.table import Table


class Reporter:
    """Renders a summary table, a terminal bar chart, and an interactive
    transaction drill-down for a set of keyword totals."""

    def __init__(
        self,
        totals: pd.Series,
        df: pd.DataFrame | None = None,
        show_all: bool = False,
        truncate: int = 10,
        income_mode: bool = False,
        net_mode: bool = False,
    ):
        self.totals = totals
        self.df = df
        self.show_all = show_all
        self.truncate = truncate
        self.income_mode = income_mode
        self.net_mode = net_mode
        self.console = Console()

    def run(self, no_chart: bool = False) -> None:
        self._render_table()
        if not no_chart:
            self._render_chart()
        if self.df is not None and not self.df.empty:
            self._interactive_inspect()
        self.console.print("\nAnd that's your bank - wrapped. 💳")

    def _render_table(self) -> None:
        if self.totals.empty:
            self.console.print("No data to display.")
            return

        if self.income_mode:
            title = "Top Income Sources"
        elif self.net_mode:
            title = "Net Flow by Group"
        else:
            title = "Top Costs"

        data = self.totals if self.show_all else self.totals.head(10)

        table = Table(title=title)
        table.add_column("#", style="dim")
        table.add_column("Item")
        table.add_column("Total", justify="right")

        for i, (keyword, value) in enumerate(data.items(), 1):
            colour = "green" if value >= 0 else "red"
            table.add_row(str(i), keyword, f"[{colour}]{value:.2f}[/{colour}]")

        self.console.print(table)

    def _render_chart(self) -> None:
        if self.totals.empty:
            return

        # Pick top 5 by absolute value
        data = self.totals if self.show_all else self.totals.head(10)
        chart_data = data.head(5)  # take top 5 exactly as table
        labels = [k[: self.truncate] for k in chart_data.index]
        values = list(chart_data.abs()) # absolute value ensures bars are upward

        # For display, take absolute value (bars always upward)
        labels = [k[: self.truncate] for k in chart_data.index]
        values = list(chart_data.abs())  # <-- absolute value ensures bars are upward

        plt.clf()
        plt.bar(labels, values)
        plt.title("Top 5")
        plt.xlabel("Item")
        plt.ylabel("Amount")
        plt.show()

    def _interactive_inspect(self) -> None:
        while True:
            choice = input(
                "\nEnter the # of a keyword to inspect its transactions (or Enter to quit): "
            ).strip()
            if not choice:
                break
            if not choice.isdigit() or not (1 <= int(choice) <= len(self.totals)):
                print("Invalid selection — please enter a number from the table.")
                continue

            keyword = list(self.totals.index)[int(choice) - 1]
            transactions = self.df[self.df["keyword"] == keyword].sort_values("date")

            print(f"\nTransactions for '{keyword}' ({len(transactions)} rows):")

            for _, row in transactions.iterrows():
                desc = row["description"]
                max_len = 50
                if len(desc) > max_len:
                    desc = desc[: max_len - 3] + "..."

                print(f"  {row['date'].date()}  |  {desc:<50}  |  {row['amount']:>10.2f}")
