import argparse
from .processor import CSVProcessor
from .keyword_manager import KeywordManager
from .reporter import Reporter
from .settings import load_group_patterns

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
    parser.add_argument('--net', action='store_true', help='Net mode: income minus expenses per keyword')
    args = parser.parse_args()

    # Load full DataFrame
    df_full = CSVProcessor(folder=args.folder).run()

    # Apply ignore filters
    df_filtered = df_full.copy()
    for ignore_str in args.ignore:
        df_filtered = df_filtered[~df_filtered['description'].str.contains(ignore_str, case=False, na=False)]

    # Filter by year
    if args.year:
        df_filtered = df_filtered[df_filtered['date'].dt.year == args.year]

    # Income or expense (skip if net mode)
    if args.net:
        pass
    elif args.income:
        df_filtered = df_filtered[df_filtered['amount'] > 0]
    else:
        df_filtered = df_filtered[df_filtered['amount'] < 0]

    # Compute totals using fuzzy logic
    km = KeywordManager(df_filtered, fuzzy_threshold=args.fuzzy)
    totals, df_labelled = km.run(reverse=args.all, income_mode=args.income, net_mode=args.net)
    if args.net:
        totals = totals[totals >= 0.01]

    # Apply same keyword mapping to full df for inspection
    patterns = load_group_patterns()
    def apply_patterns(entity):
        for pattern, label in patterns:
            if pattern in entity.upper():
                return label
        return entity

    entity_to_keyword = dict(zip(df_labelled['entity'], df_labelled['keyword']))
    df_full['entity'] = df_full['description'].apply(km._extract_entity)
    df_full['entity'] = df_full['entity'].apply(apply_patterns)
    df_full['keyword'] = df_full['entity'].map(entity_to_keyword).fillna(df_full['entity'])

    # Reporter gets full df with keyword column for inspection
    reporter = Reporter(totals, df=df_full, show_all=args.all, truncate=10, income_mode=args.income, net_mode=args.net)
    reporter.run(no_chart=args.no_chart)

if __name__ == "__main__":
    main()