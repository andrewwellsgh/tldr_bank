import argparse
from src.tldr_bank.keyword_manager import KeywordManager
from src.tldr_bank.processor import CSVProcessor
from src.tldr_bank.reporter import Reporter
from src.tldr_bank.settings import (
    load_group_patterns,
    load_spoof_adjustments,
    load_hidden_groups,
)


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

    # --- Load & filter CSVs ---
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
        income_mode=args.income,
        net_mode=args.net
    )

    # --- Map entities to keywords for later filtering ---
    patterns = load_group_patterns()
    entity_to_keyword = (
        df_labelled[["entity", "keyword"]]
        .drop_duplicates()
        .set_index("entity")["keyword"]
        .to_dict()
    )
    df_full["entity"] = df_full["description"].apply(km._extract_entity)
    df_full["entity"] = df_full["entity"].apply(lambda e: _apply_patterns(e, patterns))
    df_full["keyword"] = df_full["entity"].map(entity_to_keyword).fillna(df_full["entity"])

    # --- Load hidden groups ---
    hidden_groups = load_hidden_groups()  # set of uppercase names

    # --- Apply spoof adjustments, skipping hidden groups ---
    spoofs = load_spoof_adjustments()
    for group, adjustment in spoofs.items():
        if group.upper() in hidden_groups:
            continue
        if group in totals.index:
            totals.loc[group] += adjustment
        else:
            totals.loc[group] = adjustment

    # Re-sort totals after spoof adjustments
    if args.income or args.net:
        totals = totals.sort_values(ascending=False) if args.income else totals.sort_values()
    else:
        totals = totals.sort_values()

    # --- Filter totals and df_full for hidden groups ---
    if hidden_groups:
        totals = totals.loc[~totals.index.map(str).str.upper().isin(hidden_groups)] if not totals.empty else totals
        df_full = df_full.loc[~df_full["keyword"].astype(str).str.upper().isin(hidden_groups)] if not df_full.empty else df_full
        

    # --- Filter near-zero totals if net mode ---
    if args.net:
        totals = totals[totals.abs() >= 0.01]

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