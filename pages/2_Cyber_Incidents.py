import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

from app.data.cyber_incidents import read_all_cyber_incidents
from app.utils.auth import require_login

# Check if user is logged in
user = require_login()

st.title("🛡️ Cyber Incidents")

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
    df = read_all_cyber_incidents()
    
    if df.empty:
        st.info("No cyber incidents found in the database.")
    else:
        st.subheader(f"Total Incidents: {len(df)}")
        
        # =======================
        # CHARTS SECTION
        # =======================
        st.markdown("---")
        st.subheader("📊 Visualizations")
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Chart 1: Pie chart - Severity distribution
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
                fig_severity.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_severity, use_container_width=True)
        
        with chart_col2:
            # Chart 2: Bar chart - Incidents by Category
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
                    title="Top 10 Incident Categories",
                    color='Count',
                    color_continuous_scale='Reds'
                )
                fig_category.update_layout(showlegend=False)
                fig_category.update_xaxes(tickangle=45)
                st.plotly_chart(fig_category, use_container_width=True)
        
        # Second row of charts
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            # Chart 3: Bar chart - Status distribution
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
                st.plotly_chart(fig_status, use_container_width=True)
        
        with chart_col4:
            # Chart 4: Grouped bar chart - Severity vs Status
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
                st.plotly_chart(fig_grouped, use_container_width=True)
        
        # Chart 5: Scatter plot - Severity vs Status (with aggregation)
        if 'severity' in df.columns and 'status' in df.columns:
            # Create numeric mapping for scatter plot
            severity_order = ['Low', 'Medium', 'High', 'Critical']
            status_order = ['Open', 'In Progress', 'Resolved', 'Closed']
            
            # Aggregate data to show count at each intersection
            df_scatter = df.copy()
            df_scatter['severity_num'] = df_scatter['severity'].map({s: i for i, s in enumerate(severity_order)})
            df_scatter['status_num'] = df_scatter['status'].map({s: i for i, s in enumerate(status_order)})
            
            # Group by severity and status to get counts and most common category
            scatter_agg = df_scatter.groupby(['severity_num', 'status_num']).agg({
                'incident_id': 'count',
                'category' if 'category' in df.columns else 'severity': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
            }).reset_index()
            scatter_agg.columns = ['severity_num', 'status_num', 'count', 'most_common_category']
            
            # Add jitter for better visibility
            scatter_agg['severity_jitter'] = scatter_agg['severity_num'] + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            scatter_agg['status_jitter'] = scatter_agg['status_num'] + np.random.uniform(-0.15, 0.15, len(scatter_agg))
            
            fig_scatter = px.scatter(
                scatter_agg,
                x='severity_jitter',
                y='status_jitter',
                size='count',
                color='count',
                title="Incidents: Severity vs Status Distribution (Size = Count)",
                labels={'severity_jitter': 'Severity', 'status_jitter': 'Status', 'count': 'Number of Incidents'},
                hover_data=['most_common_category', 'count'],
                size_max=30,
                color_continuous_scale='Reds'
            )
            fig_scatter.update_xaxes(tickvals=list(range(len(severity_order))), ticktext=severity_order)
            fig_scatter.update_yaxes(tickvals=list(range(len(status_order))), ticktext=status_order)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Chart 6: Radar chart - Category profile
        if 'category' in df.columns and 'severity' in df.columns:
            try:
                # Get top categories
                top_categories = df['category'].value_counts().head(5).index
                
                # Create radar chart data
                radar_data = []
                for cat in top_categories:
                    cat_df = df[df['category'] == cat]
                    severity_dist = cat_df['severity'].value_counts(normalize=True) * 100
                    
                    radar_data.append({
                        'Category': cat,
                        'Low': severity_dist.get('Low', 0),
                        'Medium': severity_dist.get('Medium', 0),
                        'High': severity_dist.get('High', 0),
                        'Critical': severity_dist.get('Critical', 0)
                    })
                
                if radar_data:
                    radar_df = pd.DataFrame(radar_data)
                    
                    fig_radar = go.Figure()
                    
                    for idx, row in radar_df.iterrows():
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[row['Low'], row['Medium'], row['High'], row['Critical']],
                            theta=['Low', 'Medium', 'High', 'Critical'],
                            fill='toself',
                            name=row['Category']
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        showlegend=True,
                        title="Severity Distribution by Category (Radar Chart)"
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
            if 'severity' in df.columns:
                critical = len(df[df['severity'] == 'Critical']) if 'severity' in df.columns else 0
                st.metric("Critical", critical, delta=None)
        with col3:
            if 'status' in df.columns:
                open_count = len(df[df['status'] == 'Open']) if 'status' in df.columns else 0
                st.metric("Open", open_count)
        with col4:
            if 'category' in df.columns:
                unique_categories = df['category'].nunique() if 'category' in df.columns else 0
                st.metric("Categories", unique_categories)
        
        # Filters
        st.subheader("Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            if 'severity' in df.columns:
                severity_filter = st.multiselect(
                    "Filter by Severity",
                    options=df['severity'].unique() if 'severity' in df.columns else [],
                    default=[]
                )
            else:
                severity_filter = []
        
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
            if 'category' in df.columns:
                category_filter = st.multiselect(
                    "Filter by Category",
                    options=df['category'].unique() if 'category' in df.columns else [],
                    default=[]
                )
            else:
                category_filter = []
        
        # Apply filters
        filtered_df = df.copy()
        if severity_filter and 'severity' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['severity'].isin(severity_filter)]
        if status_filter and 'status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if category_filter and 'category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
        
        st.subheader(f"Filtered Results: {len(filtered_df)} incidents")
        
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
            file_name="cyber_incidents_filtered.csv",
            mime="text/csv"
        )
        
except Exception as e:
    st.error(f"Error loading cyber incidents: {e}")
    st.exception(e)

