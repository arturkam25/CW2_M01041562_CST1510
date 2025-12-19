# ==============================================================================
# CYBER INCIDENTS ANALYTICS DASHBOARD
# ==============================================================================

# This Streamlit page provides an interactive analytics dashboard
# for cyber security incidents stored in the application database.

# Scope of responsibility:
# - loading cyber incident data from the database
# - presenting key metrics and statistics
# - visualising incidents across multiple dimensions
# - enabling interactive filtering and data exploration
# - allowing data export for offline analysis

# Access control:
# - page is accessible only to authenticated users
# - authentication is enforced before any data is loaded

# Architectural role:
# - UI analytics layer
# - read-only consumer of the data access layer
# - contains no data mutation or database write operations

# Design philosophy:
# - provide high-level situational awareness
# - support exploratory data analysis (EDA)
# - combine multiple visual perspectives on the same dataset

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION AND NAVIGATION
# ==============================================================================

# Use a wide layout to support multiple charts
# and dense analytical views.
st.set_page_config(layout="wide")

# IMPORTANT:
# Default Streamlit navigation must be hidden before
# rendering any page content to avoid UI conflicts.
from app.utils.navigation import hide_default_streamlit_menu, render_navigation_sidebar
hide_default_streamlit_menu()

# ==============================================================================
# DEPENDENCIES AND ACCESS CONTROL
# ==============================================================================

# Import read-only data access function for cyber incidents.
from app.data.cyber_incidents import read_all_cyber_incidents

# Import authentication guard.
from app.utils.auth import require_login

# Enforce authentication before proceeding.
user = require_login()

# Render custom application navigation sidebar.
render_navigation_sidebar()

# ==============================================================================
# PAGE HEADER AND USER CONTEXT
# ==============================================================================

st.title("🛡️ Cyber Incidents")
# Display contextual information about the current user.
st.caption(f"Logged in as: **{user['username']}** ({user['role']})")

# ==============================================================================
# DATA LOADING AND VALIDATION
# ==============================================================================

# Load all cyber incidents from the database.
# All further operations are performed on this DataFrame.
try:
    df = read_all_cyber_incidents()

    if df.empty:
        st.info("No cyber incidents found in the database.")
    else:
        st.subheader(f"Total Incidents: {len(df)}")

        # ==============================================================================
        # VISUAL ANALYTICS SECTION
        # ==============================================================================

        # This section contains multiple visualisations
        # presenting different analytical perspectives
        # on the same dataset.

        st.markdown("---")
        st.subheader("📊 Visualizations")

        # ==============================================================================
        # FIRST ROW OF CHARTS
        # ==============================================================================

        chart_col1, chart_col2 = st.columns(2)

        # ----------------------------------------------------------------------
        # PIE CHART: INCIDENTS BY SEVERITY
        # ----------------------------------------------------------------------

        # Purpose:
        # - show overall risk distribution
        # - highlight proportion of critical incidents
        with chart_col1:
            if 'severity' in df.columns:
                severity_counts = df['severity'].value_counts()

                fig_severity = px.pie(
                    values=severity_counts.values,
                    names=severity_counts.index,
                    title="Incidents by Severity",
                    color_discrete_map={
                        'Critical': '#FF0000',
                        'High': '#FF6B00',
                        'Medium': '#FFA500',
                        'Low': '#00FF00'
                    }
                )
                fig_severity.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig_severity, width='stretch')

        # ----------------------------------------------------------------------
        # BAR CHART: TOP INCIDENT CATEGORIES
        # ----------------------------------------------------------------------

        # Purpose:
        # - identify most frequent types of incidents
        # - support prioritisation of response efforts
        with chart_col2:
            if 'category' in df.columns:
                category_counts = df['category'].value_counts().head(10)

                category_df = pd.DataFrame({
                    'Category': category_counts.index,
                    'Count': category_counts.values
                })

                fig_category = px.bar(
                    category_df,
                    x='Category',
                    y='Count',
                    title="Top 5 Incident Categories",
                    color='Count',
                    color_continuous_scale='Reds'
                )
                fig_category.update_layout(showlegend=False)
                fig_category.update_xaxes(tickangle=45)
                st.plotly_chart(fig_category, width='stretch')

        # ==============================================================================
        # SECOND ROW OF CHARTS
        # ==============================================================================

        chart_col3, chart_col4 = st.columns(2)

        # ----------------------------------------------------------------------
        # BAR CHART: INCIDENT STATUS DISTRIBUTION
        # ----------------------------------------------------------------------
        # Purpose:
        # - monitor operational workload
        # - identify backlog of unresolved incidents
        with chart_col3:
            if 'status' in df.columns:
                status_counts = df['status'].value_counts()

                status_df = pd.DataFrame({
                    'Status': status_counts.index,
                    'Count': status_counts.values
                })

                fig_status = px.bar(
                    status_df,
                    x='Status',
                    y='Count',
                    title="Incidents by Status",
                    color='Count',
                    color_continuous_scale='Blues'
                )
                fig_status.update_layout(showlegend=False)
                st.plotly_chart(fig_status, width='stretch')

        # ----------------------------------------------------------------------
        # GROUPED BAR CHART: SEVERITY VS STATUS
        # ----------------------------------------------------------------------
        # Purpose:
        # - correlate severity levels with incident lifecycle stage
        with chart_col4:
            if 'severity' in df.columns and 'status' in df.columns:
                severity_status = pd.crosstab(df['severity'], df['status'])

                fig_grouped = go.Figure()
                for status in severity_status.columns:
                    fig_grouped.add_trace(go.Bar(
                        name=status,
                        x=severity_status.index,
                        y=severity_status[status]
                    ))

                fig_grouped.update_layout(
                    title="Severity vs Status",
                    xaxis_title="Severity",
                    yaxis_title="Count",
                    barmode='group'
                )
                st.plotly_chart(fig_grouped, width='stretch')

        # ==============================================================================
        # SCATTER PLOT: SEVERITY VS STATUS (AGGREGATED)
        # ==============================================================================

        # Purpose:
        # - visualise density of incidents
        # - highlight concentration points in the severity-status space
        if 'severity' in df.columns and 'status' in df.columns:
            severity_order = ['Low', 'Medium', 'High', 'Critical']
            status_order = ['Open', 'In Progress', 'Resolved', 'Closed']

            df_scatter = df.copy()
            df_scatter['severity_num'] = df_scatter['severity'].map(
                {s: i for i, s in enumerate(severity_order)}
            )
            df_scatter['status_num'] = df_scatter['status'].map(
                {s: i for i, s in enumerate(status_order)}
            )

            scatter_agg = df_scatter.groupby(
                ['severity_num', 'status_num']
            ).agg({
                'incident_id': 'count',
                'category' if 'category' in df.columns else 'severity':
                    lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
            }).reset_index()

            scatter_agg.columns = [
                'severity_num',
                'status_num',
                'count',
                'most_common_category'
            ]

            scatter_agg['severity_jitter'] = (
                scatter_agg['severity_num']
                + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            )
            scatter_agg['status_jitter'] = (
                scatter_agg['status_num']
                + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            )

            fig_scatter = px.scatter(
                scatter_agg,
                x='severity_jitter',
                y='status_jitter',
                size='count',
                color='count',
                title="Incidents: Severity vs Status Distribution (Size = Count)",
                labels={
                    'severity_jitter': 'Severity',
                    'status_jitter': 'Status',
                    'count': 'Number of Incidents'
                },
                hover_data=['most_common_category', 'count'],
                size_max=30,
                color_continuous_scale='Reds'
            )

            fig_scatter.update_xaxes(
                tickvals=list(range(len(severity_order))),
                ticktext=severity_order
            )
            fig_scatter.update_yaxes(
                tickvals=list(range(len(status_order))),
                ticktext=status_order
            )

            st.plotly_chart(fig_scatter, width='stretch')

        # ==============================================================================
        # RADAR CHART: SEVERITY PROFILE BY CATEGORY
        # ==============================================================================

        # Purpose:
        # - compare severity profiles across categories
        # - identify categories skewed towards critical incidents
        if 'category' in df.columns and 'severity' in df.columns:
            try:
                top_categories = df['category'].value_counts().head(5).index
                radar_data = []

                for cat in top_categories:
                    cat_df = df[df['category'] == cat]
                    severity_dist = (
                        cat_df['severity']
                        .value_counts(normalize=True) * 100
                    )

                    radar_data.append({
                        'Category': cat,
                        'Low': severity_dist.get('Low', 0),
                        'Medium': severity_dist.get('Medium', 0),
                        'High': severity_dist.get('High', 0),
                        'Critical': severity_dist.get('Critical', 0)
                    })

                radar_df = pd.DataFrame(radar_data)

                fig_radar = go.Figure()
                for _, row in radar_df.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[row['Low'], row['Medium'], row['High'], row['Critical']],
                        theta=['Low', 'Medium', 'High', 'Critical'],
                        fill='toself',
                        name=row['Category']
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    showlegend=True,
                    title="Severity Distribution by Category (Radar Chart)"
                )

                st.plotly_chart(fig_radar, width='stretch')
            except Exception as e:
                st.warning(f"Could not create radar chart: {e}")

        # ==============================================================================
        # KEY METRICS SUMMARY
        # ==============================================================================

        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(df))
        with col2:
            st.metric(
                "Critical",
                len(df[df['severity'] == 'Critical']) if 'severity' in df.columns else 0
            )
        with col3:
            st.metric(
                "Open",
                len(df[df['status'] == 'Open']) if 'status' in df.columns else 0
            )
        with col4:
            st.metric(
                "Categories",
                df['category'].nunique() if 'category' in df.columns else 0
            )

        # ==============================================================================
        # FILTERING AND DATA EXPORT
        # ==============================================================================

        st.subheader("Filters")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            severity_filter = (
                st.multiselect(
                    "Filter by Severity",
                    options=df['severity'].unique()
                ) if 'severity' in df.columns else []
            )

        with filter_col2:
            status_filter = (
                st.multiselect(
                    "Filter by Status",
                    options=df['status'].unique()
                ) if 'status' in df.columns else []
            )

        with filter_col3:
            category_filter = (
                st.multiselect(
                    "Filter by Category",
                    options=df['category'].unique()
                ) if 'category' in df.columns else []
            )

        filtered_df = df.copy()

        if severity_filter:
            filtered_df = filtered_df[filtered_df['severity'].isin(severity_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if category_filter:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]

        st.subheader(f"Filtered Results: {len(filtered_df)} incidents")

        st.dataframe(filtered_df, width='stretch', height=600)

        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name="cyber_incidents_filtered.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Error loading cyber incidents: {e}")
    st.exception(e)
