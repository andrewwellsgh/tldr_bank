import argparse
from .processor import CSVProcessor
from .keyword_manager import KeywordManager
from .reporter import Reporter

def main():
    parser = argparse.ArgumentParser(description="tldr_bank CLI")
    parser.add_argument('--folder', default='csv_input', help='CSV folder')
    parser.add_argument('--all', action='store_true', help='Show all entries')
    parser.add_argument('--ignore', action='append', help='Ignore strings', default=[])
    parser.add_argument('--currency', default='GBP', help='Currency code')
    parser.add_argument('--year', type=int, help='Filter by year')
    parser.add_argument('--income', action='store_true', help='Income mode')
    parser.add_argument('--no-chart', action='store_true', help='Disable chart')
    parser.add_argument('--fuzzy', type=int, default=90, help='Fuzzy grouping threshold (0-100)')
    args = parser.parse_args()

    # Load full DataFrame
    df_full = CSVProcessor(folder=args.folder).run()

    # Apply ignore filters for totals/chart only
    df_filtered = df_full.copy()
    for ignore_str in args.ignore:
        df_filtered = df_filtered[~df_filtered['description'].str.contains(ignore_str, case=False, na=False)]

    # Filter by year
    if args.year:
        df_filtered = df_filtered[df_filtered['date'].dt.year == args.year]

    # Income or expense
    if args.income:
        df_filtered = df_filtered[df_filtered['amount'] > 0]
    else:
        df_filtered = df_filtered[df_filtered['amount'] < 0]

    # Compute totals using fuzzy logic
    km = KeywordManager(df_filtered, fuzzy_threshold=args.fuzzy)
    totals = km.run(reverse=args.all)

    # Add keyword column to df_filtered for interactive inspection
    df_filtered['keyword'] = df_filtered['description'].apply(km._extract_entity)
    mapping = km._fuzzy_group(df_filtered['keyword'])
    df_filtered['keyword'] = df_filtered['keyword'].map(mapping)

    # Reporter gets df_filtered with keyword column
    reporter = Reporter(totals, df=df_filtered, show_all=args.all, truncate=10, income_mode=args.income)
    reporter.run(no_chart=args.no_chart)

if __name__ == "__main__":
    main()