"""Transformation: execute a validated cleaning plan."""
import pandas as pd

EMAIL_RE = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"


def apply_plan(df: pd.DataFrame, plan: list[dict]) -> pd.DataFrame:
    df = df.copy()
    for step in plan:
        op, col, params = step["op"], step.get("column"), step.get("params", {})
        if op == "drop_duplicates":
            subset = None
            if params.get("ignore_id"):
                subset = [c for c in df.columns if c.lower() != "id" and not c.lower().endswith("_id")] or None
            df = df.drop_duplicates(subset=subset).reset_index(drop=True)
        elif op == "strip_whitespace":
            df[col] = df[col].astype("string").str.strip()
        elif op == "lowercase":
            df[col] = df[col].astype("string").str.lower()
        elif op == "title_case":
            df[col] = df[col].astype("string").str.title()
        elif op == "fill_null_median":
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].fillna(df[col].median())
        elif op == "fill_null_mode":
            mode = df[col].mode(dropna=True)
            if not mode.empty:
                df[col] = df[col].fillna(mode.iloc[0])
        elif op == "parse_date":
            s = df[col].astype("string").str.strip()
            iso = pd.to_datetime(s, errors="coerce", format="%Y-%m-%d")
            other = pd.to_datetime(s.where(iso.isna()), errors="coerce", format="mixed", dayfirst=True)
            df[col] = iso.fillna(other).dt.strftime("%Y-%m-%d")
        elif op == "validate_email":
            s = df[col].astype("string")
            df[col] = s.where(s.str.match(EMAIL_RE, na=False))
        elif op == "clip_range":
            df[col] = pd.to_numeric(df[col], errors="coerce").clip(params.get("min"), params.get("max"))
    return df
