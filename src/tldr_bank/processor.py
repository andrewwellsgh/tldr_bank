import os
import pandas as pd
from .security import SecurityCheck

class CSVProcessor:
    def __init__(self, folder='csv_input'):
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
