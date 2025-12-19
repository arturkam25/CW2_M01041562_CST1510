# ==============================================================================
# IT TICKETS ANALYTICS DASHBOARD
# ==============================================================================

# This Streamlit page provides an analytical dashboard for IT support tickets.
# It visualises operational workload, priorities, issue types, and ticket status.

# Scope of responsibility:
# - loading IT ticket data from the database
# - analysing ticket priorities and statuses
# - identifying common issue types
# - monitoring workload distribution among assignees
# - supporting exploratory data analysis (EDA)
# - enabling interactive filtering and data export

# Access control:
# - page is accessible only to authenticated users
# - authentication is enforced before any data is processed

# Architectural role:
# - UI analytics layer
# - read-only consumer of the IT tickets data access layer
# - contains no write operations or database mutations

# Design goals:
# - provide operational visibility for IT support
# - highlight bottlenecks and high-priority issues
# - support workload balancing and incident triage
# - present complex ticket data in an intuitive way

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION AND NAVIGATION
# ==============================================================================

# Use wide layout to accommodate multiple charts and dense tables.
st.set_page_config(layout="wide")

# IMPORTANT:
# Default Streamlit navigation must be hidden before rendering
# any UI components to maintain consistent application layout.
from app.utils.navigation import hide_default_streamlit_menu, render_navigation_sidebar
hide_default_streamlit_menu()

# ==============================================================================
# DEPENDENCIES AND ACCESS CONTROL
# ==============================================================================

# Import read-only data access function for IT tickets.
from app.data.it_tickets import read_all_tickets

# Import authentication guard.
from app.utils.auth import require_login

# Enforce authentication before any data is loaded.
user = require_login()

# Render custom application navigation sidebar.
render_navigation_sidebar()

# ==============================================================================
# PAGE HEADER AND USER CONTEXT
# ==============================================================================

st.title("🎫 IT Tickets")

# Display contextual information about the logged-in user.
st.caption(f"Logged in as: **{user['username']}** ({user['role']})")

# ==============================================================================
# DATA LOADING AND COLUMN NORMALISATION
# ==============================================================================

# Load all IT tickets from the database.
# All further analytics operate on this DataFrame.
try:
    df = read_all_tickets()

    if df.empty:
        st.info("No IT tickets found in the database.")
    else:
        st.subheader(f"Total Tickets: {len(df)}")

        # ------------------------------------------------------------------------------
        # COLUMN NAME NORMALISATION
        # ------------------------------------------------------------------------------

        # Some datasets may contain inconsistent column naming
        # (e.g. different casing or spaces). This logic attempts
        # to safely detect expected columns in a case-insensitive way.
        available_columns_lower = {col.lower(): col for col in df.columns}

        issue_type_col = None
        if 'issue_type' in df.columns:
            issue_type_col = 'issue_type'
        elif 'issue_type' in available_columns_lower:
            issue_type_col = available_columns_lower['issue_type']
        elif 'issue type' in available_columns_lower:
            issue_type_col = available_columns_lower['issue type']

        assigned_to_col = None
        if 'assigned_to' in df.columns:
            assigned_to_col = 'assigned_to'
        elif 'assigned_to' in available_columns_lower:
            assigned_to_col = available_columns_lower['assigned_to']
        elif 'assigned to' in available_columns_lower:
            assigned_to_col = available_columns_lower['assigned to']

        # ==============================================================================
        # VISUAL ANALYTICS SECTION
        # ==============================================================================

        st.markdown("---")
        st.subheader("📊 Visualizations")

        # ==============================================================================
        # FIRST ROW OF CHARTS
        # ==============================================================================

        chart_col1, chart_col2 = st.columns(2)

        # ----------------------------------------------------------------------
        # PIE CHART: TICKETS BY PRIORITY
        # ----------------------------------------------------------------------

        # Purpose:
        # - show overall urgency distribution
        # - highlight proportion of critical and high-priority tickets
        with chart_col1:
            if 'priority' in df.columns:
                priority_counts = df['priority'].value_counts()

                fig_priority = px.pie(
                    values=priority_counts.values,
                    names=priority_counts.index,
                    title="Tickets by Priority",
                    color_discrete_map={
                        'Critical': '#8B0000',
                        'High': '#FF4500',
                        'Medium': '#FFA500',
                        'Low': '#32CD32'
                    }
                )
                fig_priority.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig_priority, width='stretch')

        # ----------------------------------------------------------------------
        # BAR CHART: TOP ISSUE TYPES
        # ----------------------------------------------------------------------

        # Purpose:
        # - identify most common categories of IT problems
        # - support trend analysis and preventive action
        with chart_col2:
            if issue_type_col:
                df_issue_clean = df[issue_type_col].dropna()
                df_issue_clean = df_issue_clean[
                    (df_issue_clean != 'None') & (df_issue_clean != '')
                ]

                if len(df_issue_clean) > 0:
                    issue_type_counts = df_issue_clean.value_counts().head(10)

                    if len(issue_type_counts) > 0:
                        issue_df = pd.DataFrame({
                            'Issue Type': issue_type_counts.index,
                            'Count': issue_type_counts.values
                        })

                        fig_issue = px.bar(
                            issue_df,
                            x='Issue Type',
                            y='Count',
                            title="Top 10 Issue Types",
                            color='Count',
                            color_continuous_scale='Oranges'
                        )
                        fig_issue.update_layout(showlegend=False)
                        fig_issue.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_issue, width='stretch')
                    else:
                        st.info("Issue Type column exists but contains no usable values")
                else:
                    st.info("Issue Type column exists but all values are empty")
            else:
                st.info(
                    f"Issue Type column not found. Available columns: {', '.join(df.columns)}"
                )

        # ==============================================================================
        # SECOND ROW OF CHARTS
        # ==============================================================================

        chart_col3, chart_col4 = st.columns(2)

        # ----------------------------------------------------------------------
        # BAR CHART: TICKETS BY STATUS
        # ----------------------------------------------------------------------

        # Purpose:
        # - monitor ticket lifecycle
        # - identify backlog and unresolved issues
        with chart_col3:
            if 'status' in df.columns and not df['status'].isna().all():
                status_counts = df['status'].value_counts()

                if len(status_counts) > 0:
                    status_df = pd.DataFrame({
                        'Status': status_counts.index,
                        'Count': status_counts.values
                    })

                    fig_status = px.bar(
                        status_df,
                        x='Status',
                        y='Count',
                        title="Tickets by Status",
                        color='Count',
                        color_continuous_scale='Greens'
                    )
                    fig_status.update_layout(showlegend=False)
                    st.plotly_chart(fig_status, width='stretch')
                else:
                    st.info("No status data available")
            else:
                st.info("Status column not available in data")

        # ----------------------------------------------------------------------
        # BAR CHART: TICKETS BY ASSIGNED USER
        # ----------------------------------------------------------------------
        
        # Purpose:
        # - analyse workload distribution
        # - identify heavily loaded support agents
        with chart_col4:
            if assigned_to_col and not df[assigned_to_col].isna().all():
                assigned_counts = df[assigned_to_col].value_counts().head(10)

                if len(assigned_counts) > 0:
                    assigned_df = pd.DataFrame({
                        'User': assigned_counts.index,
                        'Ticket Count': assigned_counts.values
                    })

                    fig_assigned = px.bar(
                        assigned_df,
                        x='User',
                        y='Ticket Count',
                        title="Top 10 Assigned Users",
                        color='Ticket Count',
                        color_continuous_scale='Purples'
                    )
                    fig_assigned.update_layout(showlegend=False)
                    fig_assigned.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_assigned, width='stretch')
                else:
                    st.info("No assigned users data available")
            else:
                st.info(
                    f"Assigned To column not found. Available columns: {', '.join(df.columns)}"
                )

        # ==============================================================================
        # GROUPED BAR CHART: PRIORITY VS STATUS
        # ==============================================================================

        # Purpose:
        # - correlate ticket urgency with resolution progress
        if 'priority' in df.columns and 'status' in df.columns:
            priority_status = pd.crosstab(df['priority'], df['status'])

            fig_grouped = go.Figure()
            for status in priority_status.columns:
                fig_grouped.add_trace(go.Bar(
                    name=status,
                    x=priority_status.index,
                    y=priority_status[status]
                ))

            fig_grouped.update_layout(
                title="Priority vs Status",
                xaxis_title="Priority",
                yaxis_title="Count",
                barmode='group'
            )
            st.plotly_chart(fig_grouped, width='stretch')

        # ==============================================================================
        # SCATTER PLOT: PRIORITY VS STATUS (AGGREGATED)
        # ==============================================================================

        # Purpose:
        # - show density of tickets at priority/status intersections
        # - highlight problematic combinations
        if 'priority' in df.columns and 'status' in df.columns:
            priority_order = ['Low', 'Medium', 'High', 'Critical']
            status_order = ['Open', 'In Progress', 'Resolved', 'Closed']

            df_scatter = df.copy()
            df_scatter['priority_num'] = df_scatter['priority'].map(
                {p: i for i, p in enumerate(priority_order)}
            )
            df_scatter['status_num'] = df_scatter['status'].map(
                {s: i for i, s in enumerate(status_order)}
            )

            scatter_agg = df_scatter.groupby(
                ['priority_num', 'status_num']
            ).agg({
                'ticket_id': 'count',
                issue_type_col if issue_type_col else 'priority':
                    lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
            }).reset_index()

            scatter_agg.columns = [
                'priority_num',
                'status_num',
                'count',
                'most_common_type'
            ]

            scatter_agg['priority_jitter'] = (
                scatter_agg['priority_num']
                + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            )
            scatter_agg['status_jitter'] = (
                scatter_agg['status_num']
                + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            )

            fig_scatter = px.scatter(
                scatter_agg,
                x='priority_jitter',
                y='status_jitter',
                size='count',
                color='count',
                title="Tickets: Priority vs Status Distribution (Size = Count)",
                labels={
                    'priority_jitter': 'Priority',
                    'status_jitter': 'Status',
                    'count': 'Number of Tickets'
                },
                hover_data=['most_common_type', 'count'],
                size_max=30,
                color_continuous_scale='Viridis'
            )

            fig_scatter.update_xaxes(
                tickvals=list(range(len(priority_order))),
                ticktext=priority_order
            )
            fig_scatter.update_yaxes(
                tickvals=list(range(len(status_order))),
                ticktext=status_order
            )

            st.plotly_chart(fig_scatter, width='stretch')

        # ==============================================================================
        # RADAR CHART: ISSUE TYPE PRIORITY PROFILE
        # ==============================================================================

        # Purpose:
        # - compare priority distributions across issue types
        # - identify categories prone to critical tickets
        if issue_type_col and 'priority' in df.columns:
            try:
                top_issue_types = df[issue_type_col].value_counts().head(5).index
                radar_data = []

                for issue_type in top_issue_types:
                    issue_df = df[df[issue_type_col] == issue_type]
                    priority_dist = (
                        issue_df['priority']
                        .value_counts(normalize=True) * 100
                    )

                    radar_data.append({
                        'Issue Type': issue_type,
                        'Low': priority_dist.get('Low', 0),
                        'Medium': priority_dist.get('Medium', 0),
                        'High': priority_dist.get('High', 0),
                        'Critical': priority_dist.get('Critical', 0)
                    })

                radar_df = pd.DataFrame(radar_data)

                fig_radar = go.Figure()
                for _, row in radar_df.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[row['Low'], row['Medium'], row['High'], row['Critical']],
                        theta=['Low', 'Medium', 'High', 'Critical'],
                        fill='toself',
                        name=row['Issue Type']
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    showlegend=True,
                    title="Priority Distribution by Issue Type (Radar Chart)"
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
                "High Priority",
                len(df[df['priority'] == 'High']) if 'priority' in df.columns else 0
            )
        with col3:
            st.metric(
                "Open",
                len(df[df['status'] == 'Open']) if 'status' in df.columns else 0
            )
        with col4:
            st.metric(
                "Resolved",
                len(df[df['status'] == 'Resolved']) if 'status' in df.columns else 0
            )

        # ==============================================================================
        # FILTERING AND DATA EXPORT
        # ==============================================================================

        st.subheader("Filters")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            priority_filter = (
                st.multiselect(
                    "Filter by Priority",
                    options=df['priority'].unique()
                ) if 'priority' in df.columns else []
            )

        with filter_col2:
            status_filter = (
                st.multiselect(
                    "Filter by Status",
                    options=df['status'].unique()
                ) if 'status' in df.columns else []
            )

        with filter_col3:
            issue_type_filter = (
                st.multiselect(
                    "Filter by Issue Type",
                    options=df['issue_type'].unique()
                ) if 'issue_type' in df.columns else []
            )

        filtered_df = df.copy()

        if priority_filter:
            filtered_df = filtered_df[filtered_df['priority'].isin(priority_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if issue_type_filter and 'issue_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['issue_type'].isin(issue_type_filter)]

        st.subheader(f"Filtered Results: {len(filtered_df)} tickets")

        st.dataframe(filtered_df, width='stretch', height=600)

        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name="it_tickets_filtered.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Error loading IT tickets: {e}")
    st.exception(e)
