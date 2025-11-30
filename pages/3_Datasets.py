import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

from app.data.datasets import read_all_datasets
from app.utils.auth import require_login

# Check if user is logged in
user = require_login()

st.title("📊 Datasets Metadata")

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
    df = read_all_datasets()
    
    if df.empty:
        st.info("No datasets found in the database.")
    else:
        st.subheader(f"Total Datasets: {len(df)}")
        
        # =======================
        # CHARTS SECTION
        # =======================
        st.markdown("---")
        st.subheader("📊 Visualizations")
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Chart 1: Bar chart - Dataset sizes (rows)
            if 'rows' in df.columns:
                df_sorted = df.sort_values('rows', ascending=False).head(10)
                fig_rows = px.bar(
                    df_sorted,
                    x='name' if 'name' in df.columns else df_sorted.index,
                    y='rows',
                    title="Top 10 Datasets by Rows",
                    labels={'x': 'Dataset Name', 'y': 'Number of Rows'},
                    color='rows',
                    color_continuous_scale='Blues'
                )
                fig_rows.update_layout(showlegend=False)
                fig_rows.update_xaxes(tickangle=45)
                st.plotly_chart(fig_rows, use_container_width=True)
        
        with chart_col2:
            # Chart 2: Scatter plot - Rows vs Columns (with size categories)
            if 'rows' in df.columns and 'columns' in df.columns:
                # Categorize datasets by size for coloring
                df['size_category'] = pd.cut(
                    df['rows'],
                    bins=[0, 1000, 10000, 100000, float('inf')],
                    labels=['Small (<1K)', 'Medium (1K-10K)', 'Large (10K-100K)', 'Very Large (>100K)']
                )
                fig_scatter = px.scatter(
                    df,
                    x='rows',
                    y='columns',
                    title="Dataset Size: Rows vs Columns",
                    labels={'rows': 'Number of Rows', 'columns': 'Number of Columns'},
                    size='rows',
                    color='size_category',
                    hover_data=['name'] if 'name' in df.columns else [],
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Second row of charts
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            # Chart 3: Bar chart - Datasets by uploader
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
                        title="Top 10 Uploaders",
                        color='Count',
                        color_continuous_scale='Greens'
                    )
                    fig_uploader.update_layout(showlegend=False)
                    fig_uploader.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_uploader, use_container_width=True)
                else:
                    st.info("No uploader data available")
            else:
                st.info("Uploaded By column not available")
        
        with chart_col4:
            # Chart 4: Pie chart - Dataset size categories
            if 'rows' in df.columns:
                # Categorize datasets by size
                df['size_category'] = pd.cut(
                    df['rows'],
                    bins=[0, 1000, 10000, 100000, float('inf')],
                    labels=['Small (<1K)', 'Medium (1K-10K)', 'Large (10K-100K)', 'Very Large (>100K)']
                )
                size_counts = df['size_category'].value_counts()
                fig_size = px.pie(
                    values=size_counts.values,
                    names=size_counts.index,
                    title="Datasets by Size Category",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig_size.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_size, use_container_width=True)
        
        # Chart 5: Stacked bar chart - Datasets by uploader and size category
        if 'uploaded_by' in df.columns and 'rows' in df.columns:
            try:
                # Categorize datasets by size if not already done
                if 'size_category' not in df.columns:
                    df['size_category'] = pd.cut(
                        df['rows'],
                        bins=[0, 1000, 10000, 100000, float('inf')],
                        labels=['Small (<1K)', 'Medium (1K-10K)', 'Large (10K-100K)', 'Very Large (>100K)']
                    )
                
                # Filter out rows with missing uploaded_by
                df_uploader = df[df['uploaded_by'].notna()].copy()
                
                if not df_uploader.empty:
                    # Get top uploaders
                    top_uploaders = df_uploader['uploaded_by'].value_counts().head(5).index
                    df_uploader_filtered = df_uploader[df_uploader['uploaded_by'].isin(top_uploaders)]
                    
                    # Create crosstab
                    uploader_size = pd.crosstab(df_uploader_filtered['uploaded_by'], df_uploader_filtered['size_category'])
                    
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
                    st.plotly_chart(fig_stacked, use_container_width=True)
                else:
                    st.info("No uploader data available for stacked chart")
            except Exception as e:
                st.warning(f"Could not create stacked chart: {e}")
        
        st.markdown("---")
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Datasets", len(df))
        with col2:
            if 'rows' in df.columns:
                total_rows = df['rows'].sum() if 'rows' in df.columns else 0
                st.metric("Total Rows", f"{total_rows:,}")
        with col3:
            if 'columns' in df.columns:
                avg_columns = df['columns'].mean() if 'columns' in df.columns else 0
                st.metric("Avg Columns", f"{avg_columns:.1f}")
        
        # Display table
        st.subheader("All Datasets")
        st.dataframe(
            df,
            use_container_width=True,
            height=600
        )
        
        # Download button
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

