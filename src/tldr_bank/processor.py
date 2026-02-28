import os

import pandas as pd

from .security import SecurityCheck


class CSVProcessor:
    """Loads, validates, and merges all CSV files from a folder."""

    def __init__(self, folder: str = "csv_input"):
        self.folder = folder
        self.security = SecurityCheck()

    def run(self) -> pd.DataFrame:
        """Read all CSVs from self.folder and return a single merged DataFrame.

        Raises:
            FileNotFoundError: if the specified folder does not exist.

        Returns:
            Merged DataFrame with columns: date, description, amount.
            Returns an empty DataFrame with those columns if no CSVs are found.
        """
        if not os.path.isdir(self.folder):
            raise FileNotFoundError(f"CSV folder not found: '{self.folder}'")

        csv_files = [
            os.path.join(self.folder, f)
            for f in os.listdir(self.folder)
            if f.lower().endswith(".csv")
        ]

        if not csv_files:
            return pd.DataFrame(columns=["date", "description", "amount"])

        frames = []
        for filepath in csv_files:
            df = pd.read_csv(filepath)
            df = self.security.run(df)
            frames.append(df)

        return pd.concat(frames, ignore_index=True)
