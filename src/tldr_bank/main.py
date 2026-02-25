import argparse
from .processor import CSVProcessor
from .keyword_manager import KeywordManager
from .reporter import Reporter

def main():
    parser = argparse.ArgumentParser(description="tldr_bank CLI")
    parser.add_argument('--folder', default='csv_examples', help='CSV folder')
    args = parser.parse_args()

    processor = CSVProcessor(folder=args.folder)
    df = processor.run()

    km = KeywordManager(df)
    totals = km.run()

    reporter = Reporter(totals)
    reporter.run()

if __name__ == "__main__":
    main()
