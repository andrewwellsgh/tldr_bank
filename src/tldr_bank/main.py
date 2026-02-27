import argparse

from .keyword_manager import KeywordManager
from .processor import CSVProcessor
from .reporter import Reporter
from .settings import load_group_patterns, load_spoof_adjustments


def _apply_patterns(entity: str, patterns: list[tuple[str, str]]) -> str:
    for pattern, label in patterns:
        if pattern in entity.upper():
            return label
    return entity


def main() -> None:
    parser = argparse.ArgumentParser(
        description="tldr_bank — terminal summary of your bank transactions"
    )
    parser.add_argument("--folder", default="csv_input", help="Folder containing CSV files")
    parser.add_argument("--all", action="store_true", help="Show all entries (not just top 10)")
    parser.add_argument("--ignore", action="append", default=[], metavar="STRING",
                        help="Exclude transactions whose description contains STRING (repeatable)")
    parser.add_argument("--currency", default="GBP", help="Currency code (display only)")
    parser.add_argument("--year", type=int, help="Filter to a specific year")
    parser.add_argument("--income", action="store_true", help="Show income instead of expenses")
    parser.add_argument("--no-chart", action="store_true", help="Disable terminal bar chart")
    parser.add_argument("--fuzzy", type=int, default=90,
                        help="Fuzzy grouping threshold 0-100 (default: 90)")
    parser.add_argument("--net", action="store_true",
                        help="Net mode: show income minus expenses per group")
    args = parser.parse_args()

    # --- Load & filter ---
    df_full = CSVProcessor(folder=args.folder).run()

    df_filtered = df_full.copy()
    for ignore_str in args.ignore:
        df_filtered = df_filtered[
            ~df_filtered["description"].str.contains(ignore_str, case=False, na=False)
        ]

    if args.year:
        df_filtered = df_filtered[df_filtered["date"].dt.year == args.year]

    if not args.net:
        if args.income:
            df_filtered = df_filtered[df_filtered["amount"] > 0]
        else:
            df_filtered = df_filtered[df_filtered["amount"] < 0]

    # --- Compute keyword totals ---
    km = KeywordManager(df_filtered, fuzzy_threshold=args.fuzzy)
    totals, df_labelled = km.run(
        reverse=args.all, income_mode=args.income, net_mode=args.net
    )

    # --- Apply spoof adjustments ---
    spoofs = load_spoof_adjustments()
    for group, adjustment in spoofs.items():
        if group in totals.index:
            totals.loc[group] += adjustment
        else:
            totals.loc[group] = adjustment  # allow spoofing a group with no real transactions

    # --- Filter near-zero totals if net mode ---
    if args.net:
        totals = totals[totals.abs() >= 0.01]

    # --- Re-sort totals according to display rules ---
    if args.net or args.income:
        totals = totals.sort_values(ascending=args.all)
    else:
        totals = totals.sort_values(ascending=not args.all)

    # --- Re-label the full DataFrame for drill-down inspection ---
    patterns = load_group_patterns()
    entity_to_keyword = dict(zip(df_labelled["entity"], df_labelled["keyword"]))

    df_full["entity"] = df_full["description"].apply(km._extract_entity)
    df_full["entity"] = df_full["entity"].apply(lambda e: _apply_patterns(e, patterns))
    df_full["keyword"] = df_full["entity"].map(entity_to_keyword).fillna(df_full["entity"])

    # --- Report ---
    reporter = Reporter(
        totals,
        df=df_full,
        show_all=args.all,
        truncate=10,
        income_mode=args.income,
        net_mode=args.net,
    )
    reporter.run(no_chart=args.no_chart)


if __name__ == "__main__":
    main()
