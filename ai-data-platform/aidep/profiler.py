"""Profiling: summarise each column so an AI (or rules) can reason about it."""
import pandas as pd


def profile(df: pd.DataFrame) -> dict:
    cols = {}
    for c in df.columns:
        s = df[c]
        info = {
            "dtype": str(s.dtype),
            "null_count": int(s.isna().sum()),
            "null_pct": round(float(s.isna().mean()) * 100, 1),
            "unique": int(s.nunique(dropna=True)),
            "sample": [str(v) for v in s.dropna().head(3).tolist()],
        }
        if pd.api.types.is_numeric_dtype(s):
            info.update(min=float(s.min()), max=float(s.max()), mean=round(float(s.mean()), 2))
        cols[c] = info
    return {
        "rows": int(len(df)),
        "columns": cols,
        "duplicate_rows": int(df.duplicated().sum()),
    }
