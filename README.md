# TLDR Bank

**TLDR Bank** is a terminal CLI to summarize your bank CSVs (expenses & income) with tables, insights, and charts.

## Features

- Aggregates expenses & income by description.
- Shows top 5 (default) or all (`--all`).
- Insights include:
  - Most/Least expensive month & year
  - Largest/Smallest transactions
  - Most/Least bought items
  - Most/Least expensive things
- ASCII bar charts for top transactions.
- Ignore strings (`--ignore`), filter by year (`--year`), set currency (`--currency`).

## Installation

```bash
git clone <repo>
cd <repo>
poetry install
poetry run tldr_bank --help
