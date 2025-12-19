# ==============================================================================
# DATASETS METADATA ANALYTICS DASHBOARD
# ==============================================================================

# This Streamlit page provides an analytical overview of dataset metadata
# stored within the application database.

# Scope of responsibility:
# - loading dataset metadata from the database
# - presenting dataset size statistics
# - analysing dataset structure (rows vs columns)
# - visualising uploader activity
# - categorising datasets by size
# - enabling data inspection and export

# Access control:
# - page is accessible only to authenticated users
# - authentication is enforced before any data is loaded

# Architectural role:
# - UI analytics layer
# - read-only consumer of the datasets data access layer
# - no database write or mutation operations

# Design goals:
# - provide visibility into stored datasets
# - support data governance and auditing
# - help identify large or unusual datasets
# - enable exploratory analysis of dataset growth

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION AND NAVIGATION
# ==============================================================================

# Use wide layout to support multiple charts and tables.
st.set_page_config(layout="wide")

# IMPORTANT:
# Default Streamlit navigation must be hidden before
# rendering any page content.
from app.utils.navigation import hide_default_streamlit_menu, render_navigation_sidebar
hide_default_streamlit_menu()

# ==============================================================================
# DEPENDENCIES AND ACCESS CONTROL
# ==============================================================================

# Import read-only dataset metadata loader.
from app.data.datasets import read_all_datasets

# Import authentication guard.
from app.utils.auth import require_login

# Enforce authentication before any UI logic.
user = require_login()

# Render custom application navigation sidebar.
render_navigation_sidebar()

# ==============================================================================
# PAGE HEADER AND USER CONTEXT
# ==============================================================================

st.title("📊 Datasets Metadata")

# Display information about the currently logged-in user.
st.caption(f"Logged in as: **{user['username']}** ({user['role']})")

# ==============================================================================
# DATA LOADING AND VALIDATION
# ==============================================================================

# Load dataset metadata from the database.
# All subsequent analytics operate on this DataFrame.
try:
    df = read_all_datasets()

    if df.empty:
        st.info("No datasets found in the database.")
    else:
        st.subheader(f"Total Datasets: {len(df)}")

        # ==============================================================================
        # VISUAL ANALYTICS SECTION
        # ==============================================================================

        # This section provides multiple visual perspectives
        # on dataset metadata to support analysis and auditing.
        st.markdown("---")
        st.subheader("📊 Visualizations")

        # ==============================================================================
        # FIRST ROW OF CHARTS
        # ==============================================================================

        chart_col1, chart_col2 = st.columns(2)

        # ----------------------------------------------------------------------
        # LINE CHART: DATASET SIZE DISTRIBUTION BY ROWS
        # ----------------------------------------------------------------------

        # Purpose:
        # - identify largest datasets
        # - highlight potential storage or performance risks
        # - visualize size distribution and trends across all datasets
        with chart_col1:
            if 'rows' in df.columns:
                df_sorted = df.sort_values('rows', ascending=False)

                fig_rows = px.line(
                    df_sorted,
                    x=range(len(df_sorted)),
                    y='rows',
                    title="Dataset Size Distribution (Rows)",
                    labels={'x': 'Dataset Rank', 'y': 'Number of Rows'},
                    markers=True
                )
                fig_rows.update_traces(
                    line_shape='linear',
                    line=dict(width=3, color='#1f77b4'),
                    marker=dict(size=10, color='#1f77b4')
                )
                fig_rows.update_layout(
                    showlegend=False,
                    hovermode='x unified',
                    xaxis_title="Dataset Rank (sorted by size)",
                    yaxis_title="Number of Rows"
                )
                fig_rows.update_yaxes(tickformat=",d")
                st.plotly_chart(fig_rows, width='stretch')

        # ----------------------------------------------------------------------
        # SCATTER PLOT: ROWS VS COLUMNS
        # ----------------------------------------------------------------------

        # Purpose:
        # - analyse dataset dimensionality
        # - detect wide vs tall datasets
        # - classify dataset size visually
        with chart_col2:
            if 'rows' in df.columns and 'columns' in df.columns:
                df['size_category'] = pd.cut(
                    df['rows'],
                    bins=[0, 1000, 10000, 100000, float('inf')],
                    labels=[
                        'Small (<1K)',
                        'Medium (1K-10K)',
                        'Large (10K-100K)',
                        'Very Large (>100K)'
                    ]
                )

                fig_scatter = px.scatter(
                    df,
                    x='rows',
                    y='columns',
                    title="Dataset Size: Rows vs Columns",
                    labels={
                        'rows': 'Number of Rows',
                        'columns': 'Number of Columns'
                    },
                    size='rows',
                    color='size_category',
                    hover_data=['name'] if 'name' in df.columns else [],
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_scatter, width='stretch')

        # ==============================================================================
        # SECOND ROW OF CHARTS
        # ==============================================================================

        chart_col3, chart_col4 = st.columns(2)

        # ----------------------------------------------------------------------
        # BAR CHART: DATASETS BY UPLOADER
        # ----------------------------------------------------------------------

        # Purpose:
        # - analyse user contribution patterns
        # - identify most active dataset contributors
        with chart_col3:
            if 'uploaded_by' in df.columns and not df['uploaded_by'].isna().all():
                uploader_counts = df['uploaded_by'].value_counts().head(10)

                if len(uploader_counts) > 0:
                    uploader_df = pd.DataFrame({
                        'User': uploader_counts.index,
                        'Count': uploader_counts.values
                    })

                    fig_uploader = px.bar(
                        uploader_df,
                        x='User',
                        y='Count',
                        title="Top Uploaders",
                        color='Count',
                        color_continuous_scale='Greens'
                    )
                    fig_uploader.update_layout(showlegend=False)
                    fig_uploader.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_uploader, width='stretch')
                else:
                    st.info("No uploader data available")
            else:
                st.info("Uploaded By column not available")

        # ----------------------------------------------------------------------
        # PIE CHART: DATASET SIZE CATEGORIES
        # ----------------------------------------------------------------------

        # Purpose:
        # - understand overall dataset size distribution
        # - support capacity planning decisions
        with chart_col4:
            if 'rows' in df.columns:
                df['size_category'] = pd.cut(
                    df['rows'],
                    bins=[0, 1000, 10000, 100000, float('inf')],
                    labels=[
                        'Small (<1K)',
                        'Medium (1K-10K)',
                        'Large (10K-100K)',
                        'Very Large (>100K)'
                    ]
                )

                size_counts = df['size_category'].value_counts()

                fig_size = px.pie(
                    values=size_counts.values,
                    names=size_counts.index,
                    title="Datasets by Size Category",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig_size.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig_size, width='stretch')

        # ==============================================================================
        # STACKED BAR CHART: UPLOADERS VS DATASET SIZE
        # ==============================================================================

        # Purpose:
        # - correlate uploader activity with dataset sizes
        # - detect users producing disproportionately large datasets
        if 'uploaded_by' in df.columns and 'rows' in df.columns:
            try:
                if 'size_category' not in df.columns:
                    df['size_category'] = pd.cut(
                        df['rows'],
                        bins=[0, 1000, 10000, 100000, float('inf')],
                        labels=[
                            'Small (<1K)',
                            'Medium (1K-10K)',
                            'Large (10K-100K)',
                            'Very Large (>100K)'
                        ]
                    )

                df_uploader = df[df['uploaded_by'].notna()].copy()

                if not df_uploader.empty:
                    top_uploaders = (
                        df_uploader['uploaded_by']
                        .value_counts()
                        .head(5)
                        .index
                    )

                    df_uploader_filtered = df_uploader[
                        df_uploader['uploaded_by'].isin(top_uploaders)
                    ]

                    uploader_size = pd.crosstab(
                        df_uploader_filtered['uploaded_by'],
                        df_uploader_filtered['size_category']
                    )

                    fig_stacked = go.Figure()
                    for size_cat in uploader_size.columns:
                        fig_stacked.add_trace(go.Bar(
                            name=str(size_cat),
                            x=uploader_size.index,
                            y=uploader_size[size_cat]
                        ))

                    fig_stacked.update_layout(
                        title="Top Uploaders by Dataset Size Category",
                        xaxis_title="Uploader",
                        yaxis_title="Number of Datasets",
                        barmode='stack',
                        xaxis={'tickangle': 45}
                    )
                    st.plotly_chart(fig_stacked, width='stretch')
                else:
                    st.info("No uploader data available for stacked chart")
            except Exception as e:
                st.warning(f"Could not create stacked chart: {e}")

        # ==============================================================================
        # KEY METRICS SUMMARY
        # ==============================================================================

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Datasets", len(df))
        with col2:
            st.metric(
                "Total Rows",
                f"{df['rows'].sum():,}" if 'rows' in df.columns else "N/A"
            )
        with col3:
            st.metric(
                "Avg Columns",
                f"{df['columns'].mean():.1f}" if 'columns' in df.columns else "N/A"
            )

        # ==============================================================================
        # DATA TABLE AND EXPORT
        # ==============================================================================

        st.subheader("All Datasets")

        st.dataframe(df, width='stretch', height=600)

        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download data as CSV",
            data=csv,
            file_name="datasets_metadata.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.exception(e)
