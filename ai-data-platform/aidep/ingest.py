"""Ingestion: read raw files into a DataFrame."""
from pathlib import Path

import pandas as pd


def ingest(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(p, skipinitialspace=True)
    if suffix == ".json":
        return pd.read_json(p)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(p)
    raise ValueError(f"Unsupported file type: {suffix}")
