# TLDR Bank

This readme needs rewriting. please ignore it for now.

! Problem: Negative Transactions not printing when in --all mode



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

- **Custom Groups**
On Command line in project root:
touch .custom_group_settings

Add one word or phrase per line to /.custom_group_settings . Any transaction containing that string will be grouped under that label."

Usage (in /.custom_group_settings)
One line per group, format: keyword1 keyword2 ... = GROUP_NAME
No GROUP_NAME means the first keyword is used as the group name.

- **Spoof Amounts**

On Command line in project root:
touch .custom_spoof_settings

You can spoof amounts on to any group, either one you have created or the program has.
Note: Use the label, not the pattern.

bob = DAD
use
DAD = +10
not
bob = +10

Equally, use the output of the program itself to create more of these.
Don't try and guess it yourself from your CSV.

Usage (in /.custom_spoof_settings)
GROUP_NAME = +NUMBER
GROUP_NAME = -NUMBER

e.g
RENT = +200
FOOD = -183


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
| `--fuzzy` | Fuzzy matching threshold for grouping descriptions (0-100, default: 90) |
| `--net` | Shows each entry ordered by all it's transactions, both in and out |

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
├── settings.py        # Runs /.custom_group_settings and /.custom_spoof_settings
└── __init__.py
```

---

## Notes

- The fuzzy grouping feature is useful for combining similar merchant descriptions (e.g., `Starbucks #123` and `Starbucks #456`) into a single category.
- The tool works best with well-structured CSVs but can handle variations in column names automatically.
- Terminal charts are ASCII-based for portability, no GUI required.

---

## License

Elastic License.
Play with the source code all you want for your own purposes.
Ask if you want to make money with it and we will do it together, fairly.

I can't stop you stealing this, but it's not very nice.
Bad guys all die in a volcano at the end of the movie.

If that's you, you deserve better.
See license.MD included in root folder for more info.