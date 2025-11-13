
import streamlit as st
import pandas as pd
from typing import Dict, Any, List

#def render_data_inputs(default_path: str, default_sep: str) -> Dict[str, Any]:
def render_data_inputs(default_path: str, default_sep: str, try_detect_separator: bool = False) -> Dict[str, Any]:
    path = st.sidebar.text_input("CSV file path", value=default_path or "")
    sep = st.sidebar.selectbox("Separator", options=[",", ";", "\t", "|"], index=[",", ";", "\t", "|"].index(default_sep) if default_sep in [",", ";", "\t", "|"] else 0)
    uploaded_file = st.sidebar.file_uploader("Or upload CSV", type=["csv"])
        # Automatyczne wykrywanie separatora na podstawie pierwszej linii
    if try_detect_separator and uploaded_file is not None:
        first_line = uploaded_file.getvalue().decode("utf-8", errors="ignore").split("\n")[0]
        if ";" in first_line:
            sep = ";"
        elif "\t" in first_line:
            sep = "\t"
        elif "|" in first_line:
            sep = "|"
        else:
            sep = ","
    do_load = st.sidebar.button("Load data")
    return {"path": path.strip(), "sep": sep, "uploaded_file": uploaded_file, "do_load": do_load}

def _safe_unique(series: pd.Series, max_items: int = 200) -> List[Any]:
    vals = series.dropna().unique()
    if len(vals) > max_items:
        top = series.value_counts().head(max_items).index.tolist()
        return top
    return list(vals)

def render_sidebar_filters(types: Dict[str, List[str]], df: pd.DataFrame) -> Dict[str, Any]:
    filters: Dict[str, Any] = {"numeric": {}, "categorical": {}, "datetime": {}, "binary": {}, "drop_na": False}
    with st.sidebar.expander("Filters by type", expanded=False):
        for col in types.get("binary", []):
            choice = st.radio(f"{col}", options=["Filter off", "Only 1", "Only 0"], index=0, horizontal=True)
            filters["binary"][col] = choice
        for col in types.get("numeric", []):
            s = df[col].dropna()
            if s.empty: continue
            lo, hi = float(s.min()), float(s.max())
            sel = st.slider(f"{col} range", min_value=lo, max_value=hi, value=(lo, hi))
            filters["numeric"][col] = sel
        for col in types.get("categorical", []):
            options = _safe_unique(df[col])
            if len(options) == 0: continue
            selected = st.multiselect(f"{col} values", options=options, default=[])
            if selected:
                filters["categorical"][col] = selected
        filters["drop_na"] = st.checkbox("Drop rows with NaN in filtered columns", value=False)
    return filters
