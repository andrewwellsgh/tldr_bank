class Reporter:
    def __init__(self, totals):
        self.totals = totals

    def run(self):
        print("Spending per keyword:")
        for k, v in self.totals.items():
            print(f"{k}: {v:.2f}")
        total_days = self.totals.index.size
        print(f"Total keywords: {total_days}")
