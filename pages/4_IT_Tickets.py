import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

from app.data.it_tickets import read_all_tickets
from app.utils.auth import require_login

# Check if user is logged in
user = require_login()

st.title("🎫 IT Tickets")

# Display current user info
col1, col2 = st.columns([3, 1])
with col1:
    st.caption(f"Logged in as: **{user['username']}** ({user['role']})")
with col2:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

# Load and display data
try:
    df = read_all_tickets()
    
    if df.empty:
        st.info("No IT tickets found in the database.")
    else:
        # Debug: Show available columns
        st.subheader(f"Total Tickets: {len(df)}")
        
        # Auto-detect column names (case-insensitive)
        available_columns_lower = {col.lower(): col for col in df.columns}
        
        # Map expected columns to actual column names
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
        
        # =======================
        # CHARTS SECTION
        # =======================
        st.markdown("---")
        st.subheader("📊 Visualizations")
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Chart 1: Pie chart - Priority distribution
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
                fig_priority.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_priority, use_container_width=True)
        
        with chart_col2:
            # Chart 2: Bar chart - Tickets by Issue Type
            if issue_type_col:
                # Remove None, NaN, and empty string values
                df_issue_clean = df[issue_type_col].dropna()
                df_issue_clean = df_issue_clean[df_issue_clean != 'None']
                df_issue_clean = df_issue_clean[df_issue_clean != '']
                
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
                        st.plotly_chart(fig_issue, use_container_width=True)
                    else:
                        st.info("⚠️ Issue Type column exists but all values are empty/None")
                else:
                    st.info("⚠️ Issue Type column exists but all values are empty/None")
            else:
                st.info(f"⚠️ Issue Type column not found. Available columns: {', '.join(df.columns)}")
        
        # Second row of charts
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            # Chart 3: Bar chart - Status distribution
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
                    st.plotly_chart(fig_status, use_container_width=True)
                else:
                    st.info("No status data available")
            else:
                st.info("Status column not available in data")
        
        with chart_col4:
            # Chart 4: Bar chart - Tickets assigned to users
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
                    st.plotly_chart(fig_assigned, use_container_width=True)
                else:
                    st.info("No assigned users data available")
            else:
                st.info(f"Assigned To column not found. Available columns: {', '.join(df.columns)}")
        
        # Third row - Grouped chart
        # Chart 5: Grouped bar chart - Priority vs Status
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
            st.plotly_chart(fig_grouped, use_container_width=True)
        
        # Chart 6: Scatter plot - Priority vs Status (with aggregation)
        if 'priority' in df.columns and 'status' in df.columns:
            # Create numeric mapping for scatter plot
            priority_order = ['Low', 'Medium', 'High', 'Critical']
            status_order = ['Open', 'In Progress', 'Resolved', 'Closed']
            
            # Aggregate data to show count at each intersection
            df_scatter = df.copy()
            df_scatter['priority_num'] = df_scatter['priority'].map({p: i for i, p in enumerate(priority_order)})
            df_scatter['status_num'] = df_scatter['status'].map({s: i for i, s in enumerate(status_order)})
            
            # Group by priority and status to get counts and most common issue_type
            scatter_agg = df_scatter.groupby(['priority_num', 'status_num']).agg({
                'ticket_id': 'count',
                issue_type_col if issue_type_col else 'priority': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
            }).reset_index()
            scatter_agg.columns = ['priority_num', 'status_num', 'count', 'most_common_type']
            
            # Add jitter for better visibility
            scatter_agg['priority_jitter'] = scatter_agg['priority_num'] + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            scatter_agg['status_jitter'] = scatter_agg['status_num'] + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            
            fig_scatter = px.scatter(
                scatter_agg,
                x='priority_jitter',
                y='status_jitter',
                size='count',
                color='count',
                title="Tickets: Priority vs Status Distribution (Size = Count)",
                labels={'priority_jitter': 'Priority', 'status_jitter': 'Status', 'count': 'Number of Tickets'},
                hover_data=['most_common_type', 'count'],
                size_max=30,
                color_continuous_scale='Viridis'
            )
            fig_scatter.update_xaxes(tickvals=list(range(len(priority_order))), ticktext=priority_order)
            fig_scatter.update_yaxes(tickvals=list(range(len(status_order))), ticktext=status_order)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Chart 7: Radar chart - Issue Type profile by Priority
        if issue_type_col and 'priority' in df.columns:
            try:
                # Get top issue types
                top_issue_types = df[issue_type_col].value_counts().head(5).index
                
                # Create radar chart data
                radar_data = []
                for issue_type in top_issue_types:
                    issue_df = df[df[issue_type_col] == issue_type]
                    priority_dist = issue_df['priority'].value_counts(normalize=True) * 100
                    
                    radar_data.append({
                        'Issue Type': issue_type,
                        'Low': priority_dist.get('Low', 0),
                        'Medium': priority_dist.get('Medium', 0),
                        'High': priority_dist.get('High', 0),
                        'Critical': priority_dist.get('Critical', 0)
                    })
                
                if radar_data:
                    radar_df = pd.DataFrame(radar_data)
                    
                    fig_radar = go.Figure()
                    
                    for idx, row in radar_df.iterrows():
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[row['Low'], row['Medium'], row['High'], row['Critical']],
                            theta=['Low', 'Medium', 'High', 'Critical'],
                            fill='toself',
                            name=row['Issue Type']
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        showlegend=True,
                        title="Priority Distribution by Issue Type (Radar Chart)"
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create radar chart: {e}")
        
        st.markdown("---")
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(df))
        with col2:
            if 'priority' in df.columns:
                high_priority = len(df[df['priority'] == 'High']) if 'priority' in df.columns else 0
                st.metric("High Priority", high_priority)
        with col3:
            if 'status' in df.columns:
                open_tickets = len(df[df['status'] == 'Open']) if 'status' in df.columns else 0
                st.metric("Open", open_tickets)
        with col4:
            if 'status' in df.columns:
                resolved = len(df[df['status'] == 'Resolved']) if 'status' in df.columns else 0
                st.metric("Resolved", resolved)
        
        # Filters
        st.subheader("Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            if 'priority' in df.columns:
                priority_filter = st.multiselect(
                    "Filter by Priority",
                    options=df['priority'].unique() if 'priority' in df.columns else [],
                    default=[]
                )
            else:
                priority_filter = []
        
        with filter_col2:
            if 'status' in df.columns:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=df['status'].unique() if 'status' in df.columns else [],
                    default=[]
                )
            else:
                status_filter = []
        
        with filter_col3:
            if 'issue_type' in df.columns:
                issue_type_filter = st.multiselect(
                    "Filter by Issue Type",
                    options=df['issue_type'].unique() if 'issue_type' in df.columns else [],
                    default=[]
                )
            else:
                issue_type_filter = []
        
        # Apply filters
        filtered_df = df.copy()
        if priority_filter and 'priority' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['priority'].isin(priority_filter)]
        if status_filter and 'status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if issue_type_filter and 'issue_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['issue_type'].isin(issue_type_filter)]
        
        st.subheader(f"Filtered Results: {len(filtered_df)} tickets")
        
        # Display table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600
        )
        
        # Download button
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

