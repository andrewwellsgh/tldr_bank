#!/usr/bin/env bash

echo "Installing full CLI-reflective README for Tl;Dr Bank v3..."

cat << 'EOF' > README.md
# 💳 Tl;Dr Bank v3 — Complete CLI Reference

**Tl;Dr Bank** wraps your bank CSVs into a terminal-friendly summary.

It produces:

- Top 5 costs (or all with --all)
- Most/least expensive month & year
- Largest/smallest expenses
- Most/least bought items
- Terminal bar charts
- Unknown/blank transactions handling

---

## 🔹 CLI Flags & Options

| Flag | Description | Notes |
|------|-------------|-------|
| `--folder <path>` | Folder containing CSV files | Default: `csv_input` |
| `--all` | Show all grouped expenses instead of top 5 | - |
| `--ignore "string"` | Ignore transactions containing this string (repeatable) | Case-insensitive |
| `--currency <CODE>` | Set currency symbol | Options: GBP (£), USD ($), EUR (€), JPY (¥), AUD ($), CAD ($), CHF (CHF), CNY (¥), INR (₹) |
| `--year <YYYY>` | Filter transactions by year | - |
| `--income` | Analyze income instead of expenses | - |
| `--no-chart` | Disable terminal bar chart | - |
| `--version` | Show version | v3.0.0 |
| `--help` | Show help | - |

---

## 💷 Currency Options

| Code | Symbol |
|------|--------|
| GBP  | £      |
| USD  | $      |
| EUR  | €      |
| JPY  | ¥      |
| AUD  | $      |
| CAD  | $      |
| CHF  | CHF    |
| CNY  | ¥      |
| INR  | ₹      |

Default: GBP (£)

---

## 📝 Usage Examples

### Default Top 5 Costs

```bash
tldr_bank