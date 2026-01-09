import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="ACJ Company",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    * {
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    body, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    .main {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #FFFFFF !important;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        background-color: #004080;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 51, 102, 0.15);
    }
    .sub-header {
        font-size: 1rem;
        color: #003366;
        margin-bottom: 2rem;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    .metric-card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #333333;
        border-left: 4px solid #0066CC;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        color: #FFFFFF;
    }
    /* Dashboard card styling */
    .dashboard-card {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        color: #FFFFFF;
    }
    /* Chart container styling */
    [data-testid="stPlotlyChart"] {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
    }
    /* Dataframe styling */
    [data-testid="dataFrame"] {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
    }
    /* Info/Alert boxes */
    [data-testid="stAlert"] {
        background-color: #1a1a1a;
        border: 1px solid #0066CC;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        color: #FFFFFF;
    }
    /* Section header styling */
    h3 {
        background-color: #004080 !important;
        color: white !important;
        padding: 12px 20px !important;
        border-radius: 6px !important;
        margin-top: 0px !important;
        margin-bottom: 15px !important;
        font-weight: 700 !important;
    }
    /* Metric container */
    [data-testid="stMetricDelta"] {
        color: #0066CC !important;
    }
    [data-testid="stMetricDelta"] * {
        color: #0066CC !important;
    }
    /* Override inline styles for metric delta */
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #0066CC !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] > * {
        color: #0066CC !important;
    }
    /* Style multiselect dropdown */
    div[data-baseweb="select"] {
        background-color: #1a1a1a !important;
        border-color: #0066CC !important;
        border-radius: 6px !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        box-shadow: 0 1px 3px rgba(0, 51, 102, 0.1) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] > div:hover {
        background-color: #333333 !important;
    }
    /* Style dropdown options */
    [data-baseweb="popover"] {
        background-color: #1a1a1a !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    [data-baseweb="menu"] {
        background-color: #1a1a1a !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    [data-baseweb="menu"] li {
        color: #FFFFFF !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #333333 !important;
        color: #FFFFFF !important;
    }
    /* Style selected items */
    [data-baseweb="tag"] {
        background-color: #0066CC !important;
        color: white !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    /* Style all text elements */
    h1, h2, h3, h4, h5, h6, p, span, div, button, input, select {
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    /* Sidebar toggle button styling */
    [data-testid="stSidebarCollapseButton"] {
        background-color: #0066CC !important;
        color: white !important;
        border: 2px solid #003366 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 6px rgba(0, 51, 102, 0.2) !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover {
        background-color: #003366 !important;
        box-shadow: 0 3px 8px rgba(0, 51, 102, 0.3) !important;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
        background-color: #000000 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }
    /* Metrics styling */
    [data-testid="stMetric"] {
        background-color: transparent !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] {
        background-color: transparent !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricValue"] {
        background-color: transparent !important;
        color: #FFFFFF !important;
    }
    /* Custom metric boxes */
    .metric-box {
        border: 2px solid #0066CC;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        background-color: transparent;
        color: #FFFFFF;
    }
    .metric-box-value {
        font-size: 32px;
        font-weight: bold;
        color: #0066CC;
        margin-bottom: 8px;
    }
    .metric-box-label {
        font-size: 14px;
        color: #FFFFFF;
    }
    /* Override delta text color specifically */
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #0066CC !important;
        background-color: transparent !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] * {
        color: #0066CC !important;
        background-color: transparent !important;
    }
    /* Column styling */
    [data-testid="stColumn"] {
        background-color: #000000 !important;
    }
    /* All containers */
    [data-testid="stContainer"] {
        background-color: #000000 !important;
    }
    /* Expander styling */
    [data-testid="stExpander"] {
        background-color: #1a1a1a !important;
    }
    [data-testid="stExpander"] * {
        color: #FFFFFF !important;
    }

    </style>
""", unsafe_allow_html=True)

# Dummy data setup
years = list(range(2019, 2026))
levels = ['Associate', 'Manager & Up']
generations = ['Baby Boomer', 'Gen X', 'Millennial', 'Gen Z']

# Initialize sidebar state
if 'sidebar_expanded' not in st.session_state:
    st.session_state.sidebar_expanded = True

# Sidebar configuration
st.sidebar.title("📊 Dashboard Controls")
st.sidebar.markdown("---")
st.sidebar.markdown("**Filter Data by Year**")

# Initialize selected years in session state
if 'selected_years_set' not in st.session_state:
    st.session_state.selected_years_set = set(years)  # Start with all years selected
    st.session_state.last_clicked_year = None  # Track the last clicked year

# Add CSS for button styling
st.markdown("""
    <style>
    .year-selected {
        background-color: #FF6B6B !important;
        color: white !important;
        border: 2px solid #FF6B6B !important;
        font-weight: bold !important;
    }
    .year-unselected {
        background-color: #0066CC !important;
        color: white !important;
        border: 2px solid #0066CC !important;
    }
    .year-unselected:hover {
        background-color: #003366 !important;
        border-color: #003366 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create buttons for year selection
cols = st.sidebar.columns(3)
for idx, year in enumerate(years):
    col = cols[idx % 3]
    with col:
        is_selected = year in st.session_state.selected_years_set
        # Use HTML/CSS to style based on selection state
        button_class = "year-selected" if is_selected else "year-unselected"
        
        # Create a custom button with dynamic styling
        if st.button(str(year), use_container_width=True, key=f"year_{year}"):
            st.session_state.last_clicked_year = year  # Store the clicked year
            if year in st.session_state.selected_years_set:
                st.session_state.selected_years_set.discard(year)
            else:
                st.session_state.selected_years_set.add(year)
            st.rerun()

selected_years = sorted(list(st.session_state.selected_years_set))
last_clicked_year = st.session_state.last_clicked_year if st.session_state.last_clicked_year else (max(selected_years) if selected_years else 2025)

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Click years to toggle selection")

# Filter logic
def filter_years(df):
    if not selected_years:
        return df
    return df[df['Year'].isin(selected_years)]

# Headcount data
headcount_data = pd.DataFrame({
    'Year': [2019, 2019, 2020, 2020, 2021, 2021, 2022, 2022, 2023, 2023, 2024, 2024, 2025, 2025],
    'Level': ['Associate', 'Manager & Up', 'Associate', 'Manager & Up', 'Associate', 'Manager & Up', 'Associate', 'Manager & Up', 'Associate', 'Manager & Up', 'Associate', 'Manager & Up', 'Associate', 'Manager & Up'],
    'Count': [736, 184, 708, 182, 738, 192, 875, 225, 940, 240, 1039, 261, 1118, 282]
})

# Header section
st.markdown('<div class="main-header">👥 ACJ Company</div>', unsafe_allow_html=True)

# Get the aggregated metrics for selected years
if selected_years:
    display_year = last_clicked_year
    # Get all data for selected years
    filtered_data = headcount_data[headcount_data['Year'].isin(selected_years)]
    year_data = filtered_data[filtered_data['Year'] == display_year]
    total_hc = year_data['Count'].sum()
    managers_up = year_data[year_data['Level'] == 'Manager & Up']['Count'].sum()
    associates = year_data[year_data['Level'] == 'Associate']['Count'].sum()
    avg_tenure = 3.25
    retention_rate = 0 if display_year == 2019 else 88 + display_year % 6
else:
    display_year = 2025
    total_hc = 1118 + 282
    managers_up = 282
    associates = 1118
    avg_tenure = 3.25
    retention_rate = 91

# Key Metrics Section
st.markdown("### 📈 Key Metrics")
st.markdown("")
col1, col2, col3, col4, col5 = st.columns(5, gap="medium")

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-value">{total_hc:,}</div>
        <div class="metric-box-label">Total Headcount</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-value">{managers_up:,}</div>
        <div class="metric-box-label">Managers & Up</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-value">{associates:,}</div>
        <div class="metric-box-label">Associates</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-value">3.25 yrs</div>
        <div class="metric-box-label">Avg Tenure</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-box-value">{retention_rate}%</div>
        <div class="metric-box-label">Retention Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# Charts Section
st.markdown("### 📊 Workforce Analysis")

# Row 1: Headcount and Service Years
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("#### Headcount Distribution by Level")
    if total_hc == 0:
        pass
    else:
        # Filter data for the display year only
        display_year_data = headcount_data[headcount_data['Year'] == display_year]
        fig1 = px.bar(
            display_year_data,
            x='Year',
            y='Count',
            color='Level',
            barmode='group',
            labels={'Count': 'Number of Employees', 'Year': 'Fiscal Year'},
            color_discrete_map={'Associate': '#003366', 'Manager & Up': '#0066CC'}
        )
        fig1.update_layout(
            height=400,
            hovermode='x unified',
            showlegend=True,
            template='plotly_white'
        )
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### Service Years Distribution")
    # Tenure distribution data
    tenure_data_by_year = {
        2019: {0: 215, 1: 215, 2: 164, 3: 156, 4: 170, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0},
        2020: {0: 50, 1: 197, 2: 193, 3: 149, 4: 153, 5: 148, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0},
        2021: {0: 120, 1: 45, 2: 182, 3: 173, 4: 154, 5: 141, 6: 141, 7: 0, 8: 0, 9: 0, 10: 0},
        2022: {0: 230, 1: 119, 2: 44, 3: 175, 4: 159, 5: 127, 6: 122, 7: 124, 8: 0, 9: 0, 10: 0},
        2023: {0: 180, 1: 211, 2: 113, 3: 44, 4: 162, 5: 143, 6: 112, 7: 108, 8: 107, 9: 0, 10: 0},
        2024: {0: 240, 1: 169, 2: 191, 3: 101, 4: 43, 5: 169, 6: 124, 7: 99, 8: 95, 9: 93, 10: 0},
        2025: {0: 220, 1: 231, 2: 162, 3: 172, 4: 91, 5: 40, 6: 127, 7: 104, 8: 90, 9: 79, 10: 0}
    }
    
    # Get data for display year
    if display_year in tenure_data_by_year:
        year_tenure = tenure_data_by_year[display_year]
        service_years = pd.DataFrame({
            'Years': list(year_tenure.keys()),
            'Count': list(year_tenure.values())
        })
    else:
        service_years = pd.DataFrame({
            'Years': list(range(11)),
            'Count': [0] * 11
        })
    
    fig2 = px.bar(
        service_years,
        x='Years',
        y='Count',
        labels={'Years': 'Years of Service', 'Count': 'Number of Employees'},
        color_discrete_sequence=['#0066CC']
    )
    fig2.update_layout(
        height=400,
        hovermode='x unified',
        template='plotly_white',
        xaxis=dict(
            tickvals=[0, 5, 10],
            ticktext=['0', '5', '10'],
            range=[-0.5, 10.5]
        ),
        yaxis=dict(
            tickvals=[0, 500, 1500],
            ticktext=['0', '500', '1500'],
            range=[0, 1500]
        )
    )
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Promotions and Retention
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("#### Promotion & Transfer Opportunities")
    promo_data = pd.DataFrame({
        'Year': years,
        'Opportunities': [100, 150, 200, 250, 300, 350, 400]
    })
    fig3 = px.line(
        filter_years(promo_data),
        x='Year',
        y='Opportunities',
        markers=True,
        labels={'Opportunities': 'Number of Opportunities', 'Year': 'Fiscal Year'},
        line_shape='linear'
    )
    fig3.update_traces(
        line=dict(color='#0066CC', width=3),
        marker=dict(size=10)
    )
    fig3.update_layout(
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("#### Employee Retention Rate")
    retention_data = pd.DataFrame({
        'Year': years,
        'Retention': [0 if y == 2019 else 88 + y % 6 for y in years]
    })
    fig4 = px.line(
        filter_years(retention_data),
        x='Year',
        y='Retention',
        markers=True,
        labels={'Retention': 'Retention Rate (%)', 'Year': 'Fiscal Year'},
        line_shape='linear'
    )
    fig4.update_traces(
        line=dict(color='#4A90E2', width=3),
        marker=dict(size=10)
    )
    fig4.update_layout(
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Row 3: Demographics
st.markdown("### 👥 Workforce Demographics")

col1, col2, col3 = st.columns([1, 1, 1.2], gap="medium")

with col1:
    st.markdown("#### Gender Distribution")
    gender_data = pd.DataFrame({
        'Gender': ['Male', 'Female'],
        'Percentage': [52.37, 47.63]
    })
    fig5 = px.pie(
        gender_data,
        names='Gender',
        values='Percentage',
        hole=0.4,
        color_discrete_map={'Male': '#003366', 'Female': '#0066CC'}
    )
    fig5.update_layout(height=350, showlegend=True, template='plotly_white')
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.markdown("#### Generation Breakdown")
    gen_data = pd.DataFrame({
        'Generation': generations,
        'Percentage': [1.65, 24.92, 53.83, 19.6]
    })
    fig6 = px.pie(
        gen_data,
        names='Generation',
        values='Percentage',
        color_discrete_sequence=['#003366', '#0066CC', '#4A90E2', '#7FB3D5']
    )
    fig6.update_layout(height=350, template='plotly_white')
    st.plotly_chart(fig6, use_container_width=True)

with col3:
    st.markdown("#### Employee Engagement Scores")
    engagement_data = pd.DataFrame({
        'Dimension': ['Leadership', 'Growth', 'Culture', 'Compensation'],
        'Score': [4.2, 3.8, 4.0, 3.5]
    })
    fig7 = px.bar(
        engagement_data,
        x='Score',
        y='Dimension',
        orientation='h',
        labels={'Score': 'Score (out of 5)', 'Dimension': ''},
        color='Score',
        color_continuous_scale='Blues'
    )
    fig7.update_layout(
        height=350,
        showlegend=False,
        template='plotly_white',
        xaxis=dict(range=[0, 5])
    )
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# Summary Statistics
st.markdown("### 📋 Detailed Metrics Summary")
summary_col1, summary_col2 = st.columns(2, gap="medium")

with summary_col1:
    st.info(
        f"""
        **Headcount Trend:** The organization has grown from {headcount_data[headcount_data['Year']==2019]['Count'].sum():,} employees in 2019 to {headcount_data[headcount_data['Year']==2025]['Count'].sum():,} in 2025.
        
        **Growth Rate:** {((headcount_data[headcount_data['Year']==2025]['Count'].sum() / headcount_data[headcount_data['Year']==2019]['Count'].sum() - 1) * 100):.1f}% total growth over 6 years.
        """
    )

with summary_col2:
    st.success(
        f"""
        **Management Representation:** Managers & Up represent approximately {(managers_up/total_hc*100):.1f}% of the current workforce.
        
        **Retention Focus:** Maintaining a 91% retention rate supports organizational stability and reduces recruitment costs.
        """
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #999; font-size: 0.9rem;'>"
    "📊 ACJ Company | Data as of 2025"
    "</div>",
    unsafe_allow_html=True
)
