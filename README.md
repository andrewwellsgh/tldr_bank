# TLDR Bank

**TLDR Bank** is a terminal-based CLI tool that summarizes and visualizes your bank transactions from CSV files. It helps you quickly see your top expenses, and insights about your spending patterns, all in a compact, readable format with optional charts.

---

## 🔹 Features

- Automatically aggregates expenses and income by description/keyword.
- Shows top 5 costs/income by default, with a `--all` flag to see everything.
- Provides detailed insights:
  - Most/Least expensive month
  - Most/Least expensive year
  - Largest/Smallest expense
  - Most/Least bought item
  - Most/Least expensive item
- ASCII terminal bar chart for visualizing top transactions.
- Ignore specific transactions using `--ignore`.
- Filter transactions by year.
- Choose currency symbol (`£` default, supports common currencies).
- Fully configurable for income or expense focus.

---

## 📦 Dependencies

The project uses **Poetry** to manage dependencies. It requires:

- Python 3.10+
- pandas
- rich
- plotext
- filelock

All dependencies are listed in `pyproject.toml`.

---

## ⚙️ Installation with Poetry

1. Clone the repository:

```bash
git clone <your_repo_url>
cd <your_repo>