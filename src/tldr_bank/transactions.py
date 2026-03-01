import csv
from datetime import datetime
from typing import List, Dict

def normalize_csv(file_path: str) -> List[Dict]:
    """
    Read a CSV file and normalize it into a list of dictionaries:
    - Ensures Debit and Credit are floats (Debit negative, Credit positive)
    - Parses the date
    - Strips extra whitespace
    """
    normalized = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = {}
            # Normalize date
            try:
                item['date'] = datetime.strptime(row['Transaction Date'], "%d/%m/%Y").date()
            except ValueError:
                # Fallback: leave as string
                item['date'] = row['Transaction Date']

            # Normalize name/details
            item['details'] = row['Details'].strip()

            # Normalize amounts
            debit = row.get('Debit', '').replace(',', '').strip()
            credit = row.get('Credit', '').replace(',', '').strip()

            if debit:
                item['amount'] = -float(debit)
            elif credit:
                item['amount'] = float(credit)
            else:
                item['amount'] = 0.0

            normalized.append(item)
    return normalized


def top_n_items(transactions: List[Dict], n: int = 5) -> List[Dict]:
    """
    Return top N items by absolute total amount
    """
    totals = {}
    for tx in transactions:
        totals[tx['details']] = totals.get(tx['details'], 0) + tx['amount']

    # Sort by absolute value descending
    sorted_items = sorted(totals.items(), key=lambda x: abs(x[1]), reverse=True)
    return [{'details': k, 'total': v} for k, v in sorted_items[:n]]