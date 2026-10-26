"""Load: write clean data to a SQLite warehouse."""
import sqlite3

import pandas as pd


def load_to_sqlite(df: pd.DataFrame, db_path: str, table: str) -> int:
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table, conn, if_exists="replace", index=False)
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
