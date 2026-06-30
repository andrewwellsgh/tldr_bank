# TLDR Bank
by Andy

- Please note, this is an experimental hobby project. It comes with no warranty or guaruntees of functionality. Use at your own risk.


"The car built for Homer"

"See where your money really goes. Trades you any CSV(s) of your bankroll for a clear picture on what you spent - or who paid you. Can order by in, out or net per merchant/person/custom group. Features editable auto "Fuzzy Logic" grouping, custom grouping and spoofing. I needed this myself - It truly is the car built for Homer. Enjoy." - Andy

**TLDR Bank** is a command-line tool for quickly analyzing and summarizing your personal or business CSV bank transaction files. It cleans, processes, and aggregates your transaction data, generating insightful summaries and charts to understand your spending and income patterns at a glance.

Currently tested and working with NatWest Bank's exported CSV files in the UK. 28/2/26
It is designed to work with anything that looks like a Bank formatted CSV.

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

### Custom Groups
...
  On command line in project root:
  ```
  touch .custom_group_settings
  open .custom_group_settings
  ```

  Add one word or phrase per line to .custom_group_settings . Any transaction containing that string will be grouped under that label.

  Usage (in .custom_group_settings)
  One line per group, format: keyword1 keyword2 ... = GROUP_NAME
  No GROUP_NAME means the first keyword is used as the group name.

### Spoof Amounts

  On command line in project root:
  ```
  touch .custom_spoof_settings
  open .custom_spoof_settings
  ```
  
  You can spoof amounts onto any group, either one you have created or the program has.
  Note: Use the label, not the pattern.

### Example of spoofing a specific transaction group
  ```
  bob = DAD
  use
  DAD = +10
  not
  bob = +10
  ```

  Equally, you can use the output of the program itself to create more of these and improve your own setup for clean viewing.

  Usage (in .custom_spoof_settings)
  ```
  GROUP_NAME = +NUMBER
  GROUP_NAME = -NUMBER

  # e.g.
  RENT = +200
  FOOD = -183
  ```

  ### Hiding Specific Transaction Groups
  ...
  On command line in project root:
  ```
  touch .hide_custom_settings
  open .hide_custom_settings
  ```

  You can prevent certain merchants or groups from ever appearing in the output by listing them in a `.hide_custom_settings` file. The program automatically uppercases entries, so you don’t need to worry about case.

  ```
  ANDY
  AMAZON
  ```

  - All transactions that resolve to `ANDY` or `AMAZON` (after pattern matching and fuzzy grouping) will be **excluded** from the totals and detailed DataFrame. (That's the graph.)
  - Hide rules **override any spoof adjustments**, so even if a hidden group has a spoof applied, it will be ignored.  

  Equally, you can use the output of the program itself to discover groups you want to hide for cleaner reporting.

  Usage (in `.hide_custom_settings` file)

  ```
  GROUP_NAME
  ANOTHER_GROUP

  # e.g.
  ANDY
  AMAZON
  ```

  - Simply add one group per line.  
  - Blank lines and lines starting with `#` are ignored.  
  - The hide feature works in combination with patterns and fuzzy grouping, so you can hide both raw me

### Saving your settings
  - Use the provided settings folder to store different sets of .custom_group_settings, .custom_spoof_settings and .hide_custom_settings files.


### Saving your CSVs
  - Use the csv_store file to store CSVs. These do not get output. To use them, copy or move them to the csv_input folder. You can move any example csvs in and out as needed. The program is provided with an example csv or two, to get you going.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/30405208/tldr_bank.git
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
| `--net` | Shows each entry ordered by all its transactions, both in and out |

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
├── settings.py        # Runs .custom_group_settings and .custom_spoof_settings
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

See license.MD included in root folder for more info.


---

## Contributing / Support

We welcome contributions, bug reports, and suggestions to improve TLDR Bank!

- **Reporting issues:** Please open an [issue](https://github.com/30405208/tldr_bank/issues) on GitHub with details of any bug or feature request.
- **Contributing code:** Fork the repository, make your changes, and submit a pull request. Make sure your code follows the existing style and includes documentation if needed.
- **Questions / Support:** For help using TLDR Bank, you can open an issue or reach out via GitHub Discussions (if enabled).

Thank you for helping make TLDR Bank better!

> Note: TLDR Bank is licensed under the Elastic License. Contributions are welcome for personal or non-commercial use. Commercial use requires permission.
