"""Data quality checks, run before and after cleaning."""
import pandas as pd


def quality_report(df: pd.DataFrame) -> dict:
    total_cells = df.size or 1
    return {
        "rows": int(len(df)),
        "null_cells": int(df.isna().sum().sum()),
        "completeness_pct": round(100 * (1 - df.isna().sum().sum() / total_cells), 1),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def compare(before: dict, after: dict) -> str:
    lines = []
    for k in before:
        lines.append(f"  {k:<18} {before[k]:>8} -> {after[k]:>8}")
    return "\n".join(lines)
