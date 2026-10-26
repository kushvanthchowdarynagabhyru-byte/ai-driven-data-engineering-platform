"""CLI entry point.

Usage:
    python main.py sample_data/customers.csv
    python main.py data.csv --no-ai --db my.db --table my_table
"""
import argparse

from aidep.pipeline import run_pipeline


def main():
    ap = argparse.ArgumentParser(description="AI-Driven Data Engineering Platform")
    ap.add_argument("input", help="Path to CSV / JSON / Excel file")
    ap.add_argument("--db", default="warehouse.db", help="SQLite database path")
    ap.add_argument("--table", default=None, help="Target table (default: file name)")
    ap.add_argument("--no-ai", action="store_true", help="Skip Claude, use rule-based plan")
    ap.add_argument("--out", default="output", help="Folder for plan/profile/clean CSV")
    a = ap.parse_args()
    run_pipeline(a.input, a.db, a.table, use_ai=not a.no_ai, out_dir=a.out)


if __name__ == "__main__":
    main()
