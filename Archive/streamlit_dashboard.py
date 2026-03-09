import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="HR Dashboard 2019-2025", layout="wide")

# Title
st.title("ABC Company")

# Read source file
hr_main_file = "HR_Main.xlsx"

try:
    # Read all data
    df_headcount = pd.read_excel(hr_main_file, sheet_name='Resource Growth Tracker')
    headcount_data = df_headcount[['Year', 'Ending Headcount']].copy()
    headcount_data.rename(columns={'Year': 'Fiscal Year'}, inplace=True)
    
    df_position = pd.read_excel(hr_main_file, sheet_name='Position-Level')
    position_data = df_position[['Fiscal Year', 'Manager & Up', 'Associate']].copy()
    position_data.rename(columns={'Manager & Up': 'Managers and Up', 'Associate': 'Associates'}, inplace=True)
    
    df_tenure = pd.read_excel(hr_main_file, sheet_name='Avg Tenure')
    tenure_data = df_tenure[['Year', 'Average Tenure']].copy()
    tenure_data.rename(columns={'Year': 'Fiscal Year', 'Average Tenure': 'Avg Tenure'}, inplace=True)
    
    df_retention = pd.read_excel(hr_main_file, sheet_name='Avg Retention Rate')
    rate_col = [col for col in df_retention.columns if 'retention' in col.lower() and 'rate' in col.lower()][0]
    retention_data = df_retention[['Year', rate_col]].copy()
    retention_data.rename(columns={'Year': 'Fiscal Year', rate_col: 'Avg Retention Rate'}, inplace=True)
    
    # Try to read additional sheets
    try:
        df_service_years = pd.read_excel(hr_main_file, sheet_name='Tenure')
    except:
        df_service_years = None
    
    try:
        df_promotions = pd.read_excel(hr_main_file, sheet_name='Promotions and Transfers')
    except:
        df_promotions = None
    
    try:
        df_generation = pd.read_excel(hr_main_file, sheet_name='Generation')
    except:
        df_generation = None
    
    try:
        df_distribution = pd.read_excel(hr_main_file, sheet_name='Distribution-Overall')
    except:
        df_distribution = None
    
    try:
        df_engagement = pd.read_excel(hr_main_file, sheet_name='Engagement Score')
    except:
        df_engagement = None
    
    try:
        df_ee_count = pd.read_excel(hr_main_file, sheet_name='EE Count')
    except:
        df_ee_count = None
    
    try:
        df_ee_percentage = pd.read_excel(hr_main_file, sheet_name='EE Percentage')
    except:
        df_ee_percentage = None
    
    # Merge all data
    dashboard = headcount_data.merge(position_data, on='Fiscal Year', how='left')
    dashboard = dashboard.merge(tenure_data, on='Fiscal Year', how='left')
    dashboard = dashboard.merge(retention_data, on='Fiscal Year', how='left')
    
    # Set 2019 retention rate to blank
    dashboard.loc[dashboard['Fiscal Year'] == 2019, 'Avg Retention Rate'] = '--'
    
    # Filter by year
    years = sorted(dashboard['Fiscal Year'].unique())
    selected_years = st.multiselect("Filter by Year", [int(year) for year in years], default=[int(year) for year in years])
    
    # Display selected years
    if selected_years:
        st.write(f"📅 **Selected Years:** {', '.join(map(str, sorted(selected_years)))}")
    else:
        st.warning("Please select at least one year")
        selected_years = [int(year) for year in years]  # Reset to all if empty
    
    # Apply year filter to dashboard
    if selected_years:
        dashboard_filtered = dashboard[dashboard['Fiscal Year'].isin(selected_years)].copy()
    else:
        dashboard_filtered = dashboard.copy()
    
    # Apply year filter to additional dataframes
    year_col_service = 'Fiscal Year' if df_service_years is not None and 'Fiscal Year' in df_service_years.columns else 'Year'
    df_service_years_filtered = df_service_years[df_service_years[year_col_service].isin(selected_years)].copy() if df_service_years is not None else None
    
    year_col_promo = 'Fiscal Year' if df_promotions is not None and 'Fiscal Year' in df_promotions.columns else 'Year'
    df_promotions_filtered = df_promotions[df_promotions[year_col_promo].isin(selected_years)].copy() if df_promotions is not None else None
    
    year_col_dist = 'Fiscal Year' if df_distribution is not None and 'Fiscal Year' in df_distribution.columns else 'Year'
    df_distribution_filtered = df_distribution[df_distribution[year_col_dist].isin(selected_years)].copy() if df_distribution is not None else None
    
    year_col_gen = 'Fiscal Year' if df_generation is not None and 'Fiscal Year' in df_generation.columns else 'Year'
    df_generation_filtered = df_generation[df_generation[year_col_gen].isin(selected_years)].copy() if df_generation is not None else None
    
    year_col_ee_count = 'Fiscal Year' if df_ee_count is not None and 'Fiscal Year' in df_ee_count.columns else 'Year'
    df_ee_count_filtered = df_ee_count[df_ee_count[year_col_ee_count].isin(selected_years)].copy() if df_ee_count is not None else None
    
    year_col_ee_pct = 'Fiscal Year' if df_ee_percentage is not None and 'Fiscal Year' in df_ee_percentage.columns else 'Year'
    df_ee_percentage_filtered = df_ee_percentage[df_ee_percentage[year_col_ee_pct].isin(selected_years)].copy() if df_ee_percentage is not None else None
    
    # Get latest data for metrics from filtered data
    latest_year = dashboard_filtered['Fiscal Year'].max()
    latest_data = dashboard_filtered[dashboard_filtered['Fiscal Year'] == latest_year].iloc[0]
    
    # Display Key Metrics
    st.header("📈 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get position_levels from session state
    if 'position_levels' not in st.session_state:
        st.session_state.position_levels = ["Associates", "Managers and Up"]
    position_levels = st.session_state.position_levels
    
    # Use filtered data directly (no scaling)
    df_service_years_scaled = df_service_years_filtered
    df_promotions_scaled = df_promotions_filtered
    df_distribution_scaled = df_distribution_filtered
    df_generation_scaled = df_generation_filtered
    df_ee_count_scaled = df_ee_count_filtered
    df_ee_percentage_scaled = df_ee_percentage_filtered
    
    with col1:
        total_headcount = 0
        if "Associates" in position_levels:
            total_headcount += int(latest_data['Associates'])
        if "Managers and Up" in position_levels:
            total_headcount += int(latest_data['Managers and Up'])
        st.metric("Headcount", f"{total_headcount:,}")
    
    with col2:
        manager_count = int(latest_data['Managers and Up']) if "Managers and Up" in position_levels else 0
        st.metric("Manager and up", f"{manager_count:,}")
    
    with col3:
        assoc_count = int(latest_data['Associates']) if "Associates" in position_levels else 0
        st.metric("Associates", f"{assoc_count:,}")
    
    with col4:
        st.metric("Avg Tenure", f"{latest_data['Avg Tenure']:.2f}")
    
    with col5:
        retention_value = latest_data['Avg Retention Rate']
        if retention_value == '--':
            st.metric("Avg Retention Rate", "--")
        else:
            st.metric("Avg Retention Rate", f"{retention_value:.0f}%")
    
    # Main visualizations in 2x3 grid
    st.header("📊 Dashboard Visualizations")
    
    # Calculate position level ratio for proportional filtering
    if len(dashboard_filtered) > 0:
        total_hc = dashboard_filtered['Associates'].sum() + dashboard_filtered['Managers and Up'].sum()
        assoc_ratio = dashboard_filtered['Associates'].sum() / total_hc if total_hc > 0 else 0.5
        manager_ratio = dashboard_filtered['Managers and Up'].sum() / total_hc if total_hc > 0 else 0.5
    else:
        assoc_ratio = 0.5
        manager_ratio = 0.5
    
    # Initialize selected position filter
    if 'selected_position' not in st.session_state:
        st.session_state.selected_position = None
    
    # Apply filtering based on selection
    if st.session_state.selected_position == "Associates":
        scale_ratio = assoc_ratio
    elif st.session_state.selected_position == "Managers and Up":
        scale_ratio = manager_ratio
    else:
        scale_ratio = 1.0
    
    # Apply scaling to all dataframes
    df_service_years_scaled = df_service_years_filtered.copy() if df_service_years_filtered is not None else None
    df_promotions_scaled = df_promotions_filtered.copy() if df_promotions_filtered is not None else None
    df_distribution_scaled = df_distribution_filtered.copy() if df_distribution_filtered is not None else None
    df_generation_scaled = df_generation_filtered.copy() if df_generation_filtered is not None else None
    df_ee_count_scaled = df_ee_count_filtered.copy() if df_ee_count_filtered is not None else None
    df_ee_percentage_scaled = df_ee_percentage_filtered.copy() if df_ee_percentage_filtered is not None else None
    
    # Scale numeric columns if a position is selected
    if scale_ratio != 1.0:
        if df_service_years_scaled is not None:
            year_col = 'Fiscal Year' if 'Fiscal Year' in df_service_years_scaled.columns else 'Year'
            numeric_cols = [col for col in df_service_years_scaled.columns if col != year_col]
            for col in numeric_cols:
                df_service_years_scaled[col] = (df_service_years_scaled[col] * scale_ratio).astype(int)
        
        if df_promotions_scaled is not None:
            promo_year_col = 'Fiscal Year' if 'Fiscal Year' in df_promotions_scaled.columns else 'Year'
            numeric_cols = [col for col in df_promotions_scaled.columns if col != promo_year_col]
            for col in numeric_cols:
                df_promotions_scaled[col] = (df_promotions_scaled[col] * scale_ratio).astype(int)
        
        if df_distribution_scaled is not None:
            dist_year_col = 'Fiscal Year' if 'Fiscal Year' in df_distribution_scaled.columns else 'Year'
            numeric_cols = [col for col in df_distribution_scaled.columns if col != dist_year_col]
            for col in numeric_cols:
                df_distribution_scaled[col] = (df_distribution_scaled[col] * scale_ratio).astype(int)
        
        if df_generation_scaled is not None:
            gen_year_col = 'Fiscal Year' if 'Fiscal Year' in df_generation_scaled.columns else 'Year'
            numeric_cols = [col for col in df_generation_scaled.columns if col != gen_year_col]
            for col in numeric_cols:
                df_generation_scaled[col] = (df_generation_scaled[col] * scale_ratio).astype(int)
        
        if df_ee_count_scaled is not None:
            ee_count_year_col = 'Fiscal Year' if 'Fiscal Year' in df_ee_count_scaled.columns else 'Year'
            numeric_cols = [col for col in df_ee_count_scaled.columns if col != ee_count_year_col]
            for col in numeric_cols:
                df_ee_count_scaled[col] = (df_ee_count_scaled[col] * scale_ratio).astype(int)
    
    # Row 1: Headcount by CY and Level, Service Years, Engagement Score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Headcount by CY and Level (Stacked Bar)
        st.subheader("Headcount by calendar year and level")
        
        position_levels = ["Associates", "Managers and Up"]
        hc_display_cols = ['Associates', 'Managers and Up']
        fig_headcount_level = px.bar(dashboard_filtered, x='Fiscal Year',
                                     y=hc_display_cols,
                                     title='',
                                     barmode='stack',
                                     labels={'Fiscal Year': 'Calendar Year', 'value': 'Headcount'},
                                     color_discrete_map={'Associates': '#87CEEB', 'Managers and Up': '#1f77b4'})
        fig_headcount_level.update_layout(height=400, hovermode='x unified')
        fig_headcount_level.update_traces(hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Count: %{y}<extra></extra>')
        st.plotly_chart(fig_headcount_level, use_container_width=True)
    
    with col2:
        # Service Years Distribution
        if df_service_years_scaled is not None and not df_service_years_scaled.empty:
            year_col = 'Fiscal Year' if 'Fiscal Year' in df_service_years_scaled.columns else 'Year'
            service_cols = [col for col in df_service_years_scaled.columns if col not in [year_col]]
            # Filter to only years 0-5
            service_cols = [col for col in service_cols if any(str(i) in str(col) for i in range(6))]
            latest_service = df_service_years_scaled[df_service_years_scaled[year_col] == df_service_years_scaled[year_col].max()]
            
            if not latest_service.empty and service_cols:
                service_values = latest_service[service_cols].iloc[0]
                fig_service = px.bar(x=service_values, y=service_cols,
                                     orientation='h',
                                     title='Service Years',
                                     labels={'x': 'Employees', 'y': 'Years'})
                fig_service.update_xaxes(tickvals=[0, 50, 100, 150, 200])
                fig_service.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_service, use_container_width=True)
        else:
            st.info("Service Years data not available")
    
    with col3:
        # Engagement Score - Top level with drill-down
        st.info("📊 Engagement Score")
        
        with st.expander("Click to see granular insights", expanded=False):
            # Tabs for Count vs Percentage
            count_tab, pct_tab = st.tabs(["EE Count", "EE Percentage"])
            
            with count_tab:
                if df_ee_count_scaled is not None and not df_ee_count_scaled.empty:
                    year_col = 'Fiscal Year' if 'Fiscal Year' in df_ee_count_scaled.columns else 'Year'
                    ee_count_cols = [col for col in df_ee_count_scaled.columns if col not in [year_col]]
                    
                    if ee_count_cols:
                        fig_ee_count = px.bar(df_ee_count_scaled, x=year_col, y=ee_count_cols,
                                            title='Employee Engagement - Count by Dimension',
                                            barmode='group',
                                            labels={'value': 'Count'})
                        fig_ee_count.update_layout(height=400, hovermode='x unified')
                        st.plotly_chart(fig_ee_count, use_container_width=True)
                else:
                    st.info("EE Count data not available for selected position level")
            
            with pct_tab:
                if df_ee_percentage_scaled is not None and not df_ee_percentage_scaled.empty:
                    year_col = 'Fiscal Year' if 'Fiscal Year' in df_ee_percentage_scaled.columns else 'Year'
                    ee_pct_cols = [col for col in df_ee_percentage_scaled.columns if col not in [year_col]]
                    
                    if ee_pct_cols:
                        fig_ee_pct = px.bar(df_ee_percentage_scaled, x=year_col, y=ee_pct_cols,
                                          title='Employee Engagement - Percentage by Dimension',
                                          barmode='group',
                                          labels={'value': 'Percentage (%)'})
                        fig_ee_pct.update_layout(height=400, hovermode='x unified')
                        st.plotly_chart(fig_ee_pct, use_container_width=True)
                else:
                    st.info("EE Percentage data not available for selected position level")
    
    # Row 2: Promotions & Transfers, Retention Rate, Distribution
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Promotions & Transfers
        if df_promotions_scaled is not None and not df_promotions_scaled.empty:
            promo_year_col = 'Fiscal Year' if 'Fiscal Year' in df_promotions_scaled.columns else 'Year'
            promo_cols = [col for col in df_promotions_scaled.columns if col not in [promo_year_col]]
            
            if promo_cols:
                fig_promo = px.bar(df_promotions_scaled, x=promo_year_col, y=promo_cols,
                                  title='Promotions & Transfers',
                                  barmode='stack',
                                  labels={'value': 'opportunities'})
                fig_promo.update_layout(height=400, hovermode='x unified')
                st.plotly_chart(fig_promo, use_container_width=True)
        else:
            st.info("Promotions & Transfers data not available")
    
    with col2:
        # Retention Rate Trend
        retention_chart_data = dashboard_filtered[dashboard_filtered['Avg Retention Rate'] != '--'].copy()
        retention_chart_data['Avg Retention Rate'] = pd.to_numeric(retention_chart_data['Avg Retention Rate'], errors='coerce')
        
        if len(retention_chart_data) > 0:
            fig_retention = px.line(retention_chart_data, x='Fiscal Year', y='Avg Retention Rate',
                                   title='Retention Rate',
                                   markers=True)
            fig_retention.update_yaxes(tickformat=".0%")
            fig_retention.add_annotation(text="Industry Leading", x=0.5, y=0.95,
                                        xref="paper", yref="paper", showarrow=False,
                                        font=dict(size=12, color="green"))
            fig_retention.update_layout(height=400, hovermode='x unified')
            st.plotly_chart(fig_retention, use_container_width=True)
    
    with col3:
        # Distribution (Gender/Diversity) - Top level with drill-down
        if df_distribution_scaled is not None and not df_distribution_scaled.empty:
            dist_year_col = 'Fiscal Year' if 'Fiscal Year' in df_distribution_scaled.columns else 'Year'
            dist_cols = [col for col in df_distribution_scaled.columns if col not in [dist_year_col]]
            
            latest_dist = df_distribution_scaled[df_distribution_scaled[dist_year_col] == df_distribution_scaled[dist_year_col].max()]
            if not latest_dist.empty and dist_cols:
                dist_values = latest_dist[dist_cols].iloc[0]
                fig_dist = px.pie(values=dist_values, names=dist_cols,
                                 title='Distribution\nInclusion & Diversity')
                fig_dist.update_layout(height=400)
                st.plotly_chart(fig_dist, use_container_width=True)
                
                with st.expander("Click to see granular insights", expanded=False):
                    # Show trend over time
                    fig_dist_trend = px.bar(df_distribution_scaled, x=dist_year_col, y=dist_cols,
                                           title='Distribution Trend Over Time',
                                           barmode='stack',
                                           labels={'value': 'Count'})
                    fig_dist_trend.update_layout(height=400, hovermode='x unified')
                    st.plotly_chart(fig_dist_trend, use_container_width=True)
        else:
            st.info("Distribution data not available")
    
    # Row 3: Generation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Generation Demographics (Donut Chart)
        if df_generation_scaled is not None and not df_generation_scaled.empty:
            gen_year_col = 'Fiscal Year' if 'Fiscal Year' in df_generation_scaled.columns else 'Year'
            gen_cols = [col for col in df_generation_scaled.columns if col not in [gen_year_col]]
            
            latest_gen = df_generation_scaled[df_generation_scaled[gen_year_col] == df_generation_scaled[gen_year_col].max()]
            if not latest_gen.empty and gen_cols:
                gen_values = latest_gen[gen_cols].iloc[0]
                fig_gen = px.pie(values=gen_values, names=gen_cols,
                                hole=0.3,
                                title='Generation')
                fig_gen.update_layout(height=400)
                st.plotly_chart(fig_gen, use_container_width=True)
        else:
            st.info("Generation data not available")


except Exception as e:
    st.error(f"Error loading data: {e}")
    st.exception(e)
