import streamlit as st
import pandas as pd
import time
import uuid
import plotly.express as px

from eda import (
    load_csv,
    detect_column_types,
    get_basic_overview,
    get_quality_report,
    apply_filters,
    classify_dataset_mode,
    add_experience_numeric,
    add_age_numeric,
    bin_age_group,
    bin_experience_group,
    enforce_age_range_order,
)

from ui import (
    render_data_inputs,
    render_sidebar_filters,
)

from charts import (
    show_histogram,
    show_stacked_bar_chart,
    pie_chart,
    bar_chart_grouped_mean,
    box_plot,
)

st.set_page_config(page_title="Welcome Survey EDA", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

col1, col2 = st.columns([1, 20])
with col1:
    st.image("01.jpeg", use_container_width=True)
with col2:
    st.markdown(
        "<div style='margin-left: 250px; font-size: 3em; font-weight: bold; color: #2196F3; font-family: Georgia, serif;'>WELCOME SURVEY ANALYSIS</div>",
        unsafe_allow_html=True
    )

st.title("Mini EDA")

if "data_path" not in st.session_state:
    st.session_state.data_path = "35__welcome_survey_cleaned.csv"
if "sep" not in st.session_state:
    st.session_state.sep = ","
if "df_raw" not in st.session_state:
    st.session_state.df_raw = None
if "is_data_loaded" not in st.session_state:
    st.session_state.is_data_loaded = False

data_cfg = render_data_inputs(
    default_path=st.session_state.data_path,
    default_sep=st.session_state.sep,
    try_detect_separator=True
)

load_error = None
if data_cfg.get("do_load"):
    progress_text = "Loading data - please wait..."
    bar = st.sidebar.progress(0, text=progress_text)
    try:
        for p in (10, 25, 40):
            time.sleep(0.1); bar.progress(p, text=progress_text)

        if data_cfg.get("uploaded_file") is not None:
            df_raw = load_csv(data_cfg["uploaded_file"], data_cfg["sep"])
            st.session_state.data_path = "(uploaded)"
        elif data_cfg.get("path"):
            df_raw = load_csv(data_cfg["path"], data_cfg["sep"])
            st.session_state.data_path = data_cfg["path"]
        else:
            raise RuntimeError("No file selected or path provided.")

        df_raw = add_experience_numeric(df_raw)
        df_raw = add_age_numeric(df_raw)
        df_raw["age_range"] = df_raw["age_estimate"].apply(bin_age_group)
        df_raw["experience_range"] = df_raw["experience_estimate"].apply(bin_experience_group)
        df_raw = enforce_age_range_order(df_raw)
        
        st.session_state.df_raw = df_raw
        st.session_state.sep = data_cfg["sep"]
        st.session_state.is_data_loaded = True

        for p in (70, 85, 100):
            time.sleep(0.1); bar.progress(p, text=progress_text)
        time.sleep(0.1)
    except Exception as e:
        load_error = str(e)
    finally:
        bar.empty()

if st.sidebar.button("Clear data"):
    st.session_state.df_raw = None
    st.session_state.is_data_loaded = False

if load_error:
    st.sidebar.error(f"Failed to load file: {load_error}")

df_raw = st.session_state.df_raw

if not st.session_state.is_data_loaded or df_raw is None:
    st.info("Upload a CSV and click Load data.")
    st.stop()

mode = classify_dataset_mode(df_raw)
types = detect_column_types(df_raw)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Numeric columns", len(types.get("numeric", [])))
c2.metric("Categorical columns", len(types.get("categorical", [])))
c3.metric("Binary columns", len(types.get("binary", [])))
c4.metric("Total columns", df_raw.shape[1])

tab_data, tab_quality, tab_analysis = st.tabs([
    "Data Overview & Dynamic Tables Filtering",
    "Data Quality Report",
    "Exploratory Analysis"
])

with tab_data:
    st.markdown("<h2 style='color:#2196F3;'> Overview</h2>", unsafe_allow_html=True)
    overview = get_basic_overview(df_raw)
    cc1, cc2, cc3 = st.columns(3)
    cc1.metric("Rows", f"{overview['n_rows']:,}")
    cc2.metric("Columns", f"{overview['n_cols']:,}")
    cc3.metric("Detected separator", repr(st.session_state.sep))
    st.write("**Column names**")
    st.write(list(df_raw.columns))
    st.write("**Dtypes**")
    st.dataframe(overview["dtypes"], use_container_width=True, hide_index=True)
    st.write("**Head (5 rows)**")
    
    st.markdown("### Data (full table with scrolling)")
    st.dataframe(df_raw, use_container_width=True, hide_index=True)
    
    st.markdown("### Dynamic table for text values")

    with st.expander("Filtering one text column", expanded=False):
        cat_cols = types.get("categorical", [])
        if cat_cols:
            selected_cat_col = st.selectbox("Select text column", cat_cols, key="dyn_cat_col")
            if selected_cat_col:
                values = df_raw[selected_cat_col].dropna().unique().tolist()
                selected_values = st.multiselect(f"Select values from column: {selected_cat_col}", values)

                if selected_values:
                    filtered_df = df_raw[df_raw[selected_cat_col].isin(selected_values)]
                    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Please select at least one value to display data..")
        else:
            st.warning("There are no text columns in the data.")

    with st.expander("Filtering multiple text columns + charts", expanded=False):
        cat_cols = types.get("categorical", [])
        if cat_cols:
            selected_cols = st.multiselect("Select text columns to filter", cat_cols, key="multi_text_cols")

            filters = {}
            for col in selected_cols:
                values = df_raw[col].dropna().unique().tolist()
                selected_vals = st.multiselect(f"Select values for {col}", values, key=f"vals_{col}")
                if selected_vals:
                    filters[col] = selected_vals

            if filters:
                df_filtered = df_raw.copy()
                for col, vals in filters.items():
                    df_filtered = df_filtered[df_filtered[col].isin(vals)]

                st.dataframe(df_filtered, use_container_width=True, hide_index=True)
                st.success(f"Shown {len(df_filtered)} lines.")

                st.markdown("#### Counts of selected values")
                for col in filters:
                    counts = df_filtered[col].value_counts()
                    st.write(f"**{col}**")
                    st.bar_chart(counts)
            else:
                st.info("Please select at least one value to display data..")
        else:
            st.warning("There are no text columns in the data.")

with tab_quality:
    st.markdown("<h2 style='color:#2196F3;'> Data Quality</h2>", unsafe_allow_html=True)
    quality = get_quality_report(df_raw)
    qc1, qc2 = st.columns(2)
    with qc1:
        st.write("**Missing values (NaN)**")
        st.dataframe(quality["nan_table"], use_container_width=True, hide_index=True)
    with qc2:
        st.write("**Duplicates**")
        st.write(f"Duplicate rows: {quality['n_duplicates']}")
        if quality["n_duplicates"] > 0 and quality["duplicates_preview"] is not None:
            st.dataframe(quality["duplicates_preview"], use_container_width=True, hide_index=True)
    st.write("**Descriptive stats (numeric)**")
    if quality["numeric_describe"] is not None:
        st.dataframe(quality["numeric_describe"], use_container_width=True)
    else:
        st.info("No numeric columns.")

with tab_analysis:
    st.markdown("<h2 style='color:#2196F3;'> Analysis and charts</h2>", unsafe_allow_html=True)
    st.sidebar.header("Exploratory Filters Only")
    filters = render_sidebar_filters(types, df_raw)
    df = apply_filters(df_raw, filters)
    st.caption(f"Rows after filters: {len(df):,}")
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    if df.empty:
        st.warning("No data after filters.")
        st.stop()

with row1_col1:
    show_hist = st.checkbox("Show Histogram", key="show_hist")
    if show_hist:
        hist_col = st.selectbox("Histogram column", types.get("numeric", []), key="hist")
        fig1 = show_histogram(df, hist_col)
        if fig1 is not None:
            st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    show_stack = st.checkbox("Show Stacked Bar", key="show_stack")
    if show_stack:
        bar_x = st.selectbox("X (category)", types.get("categorical", []), key="bar_x")
        bar_color_options = [col for col in types.get("categorical", []) + types.get("binary", []) if col != bar_x]
        bar_color = st.selectbox("Color (binary/categorical)", bar_color_options, key="bar_color")
        fig2 = show_stacked_bar_chart(df, bar_x, bar_color)
        if fig2 is not None:
            st.plotly_chart(fig2, use_container_width=True)

with row1_col3:
    show_pie = st.checkbox("Show Pie", key="show_pie")
    if show_pie:
        pie_col = st.selectbox("Pie column", types.get("categorical", []), key="pie")
        fig3 = pie_chart(df, pie_col)
        if fig3 is not None:
            st.plotly_chart(fig3, use_container_width=True)

with row2_col1:
    show_avg = st.checkbox("Show Avg Bar", key="show_avg")
    if show_avg:
        bar_group = st.selectbox("Group by (category)", types.get("categorical", []), key="avg_group")
        bar_val_options = [col for col in types.get("numeric", []) if col != bar_group]
        bar_val = st.selectbox("Value (numeric)", bar_val_options, key="avg_val")
        fig4 = bar_chart_grouped_mean(df, bar_group, bar_val)
        if fig4 is not None:
            st.plotly_chart(fig4, use_container_width=True)

with row2_col2:
    show_box = st.checkbox("Show Box Plot", key="show_box")
    if show_box:
        box_x = st.selectbox("X (category)", types.get("categorical", []), key="box_x")
        box_y_options = [col for col in types.get("numeric", []) if col != box_x]
        box_y = st.selectbox("Y (numeric)", box_y_options, key="box_y")
        fig5 = box_plot(df, box_x, box_y)
        if fig5 is not None:
            st.plotly_chart(fig5, use_container_width=True)

with row2_col3:
    show_binary = st.checkbox("Show Binary Value Counts", key="show_binary_counts")
    if show_binary:
        bin_col = st.selectbox("Binary column (0/1)", types.get("binary", []), key="binary_col_count")
        if bin_col:
            bin_counts = df[bin_col].value_counts().sort_index()
            bin_df = bin_counts.reset_index()
            bin_df.columns = ['value', 'count']
            bin_df['value'] = bin_df['value'].astype(str)
            
            fig = px.bar(bin_df, x='value', y='count', title=f"Binary distribution: {bin_col}")
            fig.update_layout(xaxis_tickangle=-90)
            st.plotly_chart(fig, use_container_width=True)
