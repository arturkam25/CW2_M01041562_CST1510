
import pandas as pd
import numpy as np
from typing import Dict, List, Any

def load_csv(path_or_buffer, sep=",") -> pd.DataFrame:
    try:
        df = pd.read_csv(path_or_buffer, sep=sep)
    except Exception as e:
        raise RuntimeError(f"CSV read error: {e}")
    return df

def detect_column_types(df: pd.DataFrame):
    types = {"numeric": [], "categorical": [], "datetime": [], "binary": []}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            unique_vals = set(df[col].dropna().unique())
            if unique_vals.issubset({0, 1}):
                types["binary"].append(col)
            else:
                types["numeric"].append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            types["datetime"].append(col)
        else:
            types["categorical"].append(col)
    return types

def get_basic_overview(df: pd.DataFrame) -> Dict[str, Any]:
    dtypes = pd.DataFrame({"column": df.columns, "dtype": [str(df[c].dtype) for c in df.columns]})
    return {"n_rows": len(df), "n_cols": df.shape[1], "dtypes": dtypes}

def get_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    nan_counts = df.isna().sum().rename("nan_count")
    nan_pct = (df.isna().mean() * 100).round(2).rename("nan_pct")
    nan_table = pd.concat([nan_counts, nan_pct], axis=1).reset_index().rename(columns={"index": "column"})
    dup_mask = df.duplicated()
    n_duplicates = int(dup_mask.sum())
    duplicates_preview = df[dup_mask].head(20) if n_duplicates > 0 else None
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    numeric_describe = df[numeric_cols].describe().T if numeric_cols else None
    return {
        "nan_table": nan_table,
        "n_duplicates": n_duplicates,
        "duplicates_preview": duplicates_preview,
        "numeric_describe": numeric_describe,
    }

def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    for col, rng in filters.get("numeric", {}).items():
        if rng is None: continue
        lo, hi = rng
        if pd.api.types.is_numeric_dtype(df[col]):
            mask &= df[col].between(lo, hi)
    for col, allowed in filters.get("categorical", {}).items():
        if allowed: mask &= df[col].isin(allowed)
    for col, choice in filters.get("binary", {}).items():
        if choice == "Only 1":
            mask &= df[col] == 1
        elif choice == "Only 0":
            mask &= df[col] == 0
    if filters.get("drop_na", False):
        all_cols = list(filters.get("numeric", {}).keys()) + list(filters.get("categorical", {}).keys()) + list(filters.get("binary", {}).keys())
        cols = [c for c in all_cols if c in df.columns]
        if cols: mask &= df[cols].notna().all(axis=1)
    return df[mask]

def classify_dataset_mode(df: pd.DataFrame) -> str:
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    dt_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    txt_cols = [c for c in df.columns if (pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_string_dtype(df[c]))]
    n_total = df.shape[1]
    if n_total == len(num_cols) + len(dt_cols) and len(num_cols) > 0:
        return "numeric-only"
    if n_total == len(txt_cols):
        return "text-only"
    return "mixed"

def add_experience_numeric(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {"0-1": 0.5, "1-2": 1.5, "0-2": 1, "2-5": 3.5, "5-10": 7.5, "10+": 12,
               "11-15": 13, "16+": 18, ">=16": 18, "20+": 25}
    if "years_of_experience" in df.columns:
        df["experience_estimate"] = df["years_of_experience"].map(mapping)
    return df

def add_age_numeric(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "18-25": 21.5, "26-35": 30.5, "36-45": 40.5, "46-60": 53, "60+": 65,
        "25-34": 29.5, "35-44": 39.5, "45-54": 49.5, "55-64": 59.5, "65+": 67.5, ">=60": 65
    }
    if "age" in df.columns:
        df["age_estimate"] = df["age"].map(mapping)
    return df

def bin_experience_group(val):
    if pd.isna(val): return None
    if val < 1: return "0-1"
    elif val < 3: return "1-2"
    elif val < 6: return "2-5"
    elif val < 10: return "5-10"
    elif val < 16: return "10-15"
    else: return "16+"

def bin_age_group(val):
    if pd.isna(val): return None
    if val < 18: return "<18"
    if val < 25: return "18-24"
    elif val < 35: return "25-34"
    elif val < 45: return "35-44"
    elif val < 60: return "45-59"
    return "60+"

age_order = ["<18","18-24", "25-34", "35-44", "45-59", "60+"]

def enforce_age_range_order(df: pd.DataFrame) -> pd.DataFrame:
    if "age_range" in df.columns:
        df["age_range"] = pd.Categorical(df["age_range"], categories=age_order, ordered=True)
    return df

