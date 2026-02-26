# TLDR Bank

**TLDR Bank** is a command-line tool for quickly analyzing and summarizing your personal or business CSV bank transaction files. It cleans, processes, and aggregates your transaction data, generating insightful summaries and charts to understand your spending and income patterns at a glance.

---

## Features

- **Automatic CSV Parsing & Cleaning**  
  Handles multiple CSV files with varying column names and formats, automatically detecting `date`, `description`, and `amount` columns.  

- **Fuzzy Keyword Grouping**  
  Groups similar transaction descriptions using fuzzy matching to provide meaningful aggregated totals.

- **Insightful Reports**  
  Generates tables and visualizations of:
  - Top expenses or income sources
  - Monthly and yearly totals
  - Largest and smallest transactions
  - Most/least purchased items

- **Flexible CLI Options**  
  Customize your analysis with filters like year, income-only mode, ignore certain descriptions, and control fuzzy grouping thresholds.

- **Charts in Terminal**  
  Simple ASCII bar charts for top 5 expenses or income.

- **Safe File Handling**  
  Supports file locking to prevent simultaneous edits during processing.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/tldr_bank.git
cd tldr_bank
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

**Dependencies include:** `pandas`, `rich`, `plotext`, `rapidfuzz`, `filelock`

---

## Usage

Run the CLI tool:

```bash
python -m tldr_bank.main [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--folder` | Folder containing CSV files (default: `csv_input`) |
| `--all` | Show all entries in the summary table |
| `--ignore` | Ignore transactions containing a string (can be used multiple times) |
| `--currency` | Currency code for totals (default: `GBP`) |
| `--year` | Filter transactions by a specific year |
| `--income` | Analyze income transactions instead of expenses |
| `--no-chart` | Disable terminal charts |
| `--fuzzy` | Fuzzy matching threshold for grouping descriptions (0-100, default: 85) |

### Example

```bash
python -m tldr_bank.main --folder csv_input --year 2025 --income --fuzzy 90
```

This will analyze all income transactions from 2025 in the `csv_input` folder, grouping similar descriptions with a fuzzy threshold of 90.

---

## Project Structure

```
tldr_bank/
│
├── main.py            # CLI entry point
├── processor.py       # Handles CSV reading and merging
├── security.py        # Cleans and validates CSV columns
├── keyword_manager.py # Groups transaction descriptions and aggregates totals
├── reporter.py        # Generates tables, charts, and insights
├── lock.py            # File locking utility
└── __init__.py
```

---

## Notes

- The fuzzy grouping feature is useful for combining similar merchant descriptions (e.g., `Starbucks #123` and `Starbucks #456`) into a single category.
- The tool works best with well-structured CSVs but can handle variations in column names automatically.
- Terminal charts are ASCII-based for portability, no GUI required.

---

## License

MIT License – free to use a