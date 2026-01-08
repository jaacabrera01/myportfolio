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
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        background: linear-gradient(90deg, #003366 0%, #0066CC 100%);
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
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        border-left: 4px solid #0066CC;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    /* Dashboard card styling */
    .dashboard-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    /* Chart container styling */
    [data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    /* Dataframe styling */
    [data-testid="dataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    /* Info/Alert boxes */
    [data-testid="stAlert"] {
        background-color: #F5F5F5;
        border: 1px solid #0066CC;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    /* Section header styling */
    h3 {
        background: linear-gradient(90deg, #003366 0%, #0066CC 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        margin-top: 20px;
        margin-bottom: 15px;
        font-weight: 700;
    }
    /* Metric container */
    [data-testid="stMetricDelta"] {
        color: #0066CC;
    }
    /* Style multiselect dropdown */
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-color: #0066CC !important;
        border-radius: 6px !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
        box-shadow: 0 1px 3px rgba(0, 51, 102, 0.1) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    div[data-baseweb="select"] > div:hover {
        background-color: #E8F4FF !important;
    }
    /* Style dropdown options */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    [data-baseweb="menu"] li {
        color: #003366 !important;
        font-family: 'Helvetica', 'Helvetica Neue', Arial, sans-serif !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #D6EAF8 !important;
        color: #003366 !important;
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
    </style>
""", unsafe_allow_html=True)

# Dummy data setup
years = list(range(2019, 2026))
levels = ['Associate', 'Manager & Up']
generations = ['Baby Boomer', 'Gen X', 'Millennial', 'Gen Z']

# Sidebar configuration
st.sidebar.title("📊 Dashboard Controls")
st.sidebar.markdown("---")
st.sidebar.markdown("**Filter Data by Year**")
selected_years = st.sidebar.multiselect(
    "Select Years to Display:",
    years,
    default=years,
    help="Choose one or more years to analyze workforce trends"
)
st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Select multiple years to compare trends across time periods")

# Filter logic
def filter_years(df):
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
    latest_year = max(selected_years)
    year_data = headcount_data[headcount_data['Year'] == latest_year]
    total_hc = year_data['Count'].sum()
    managers_up = year_data[year_data['Level'] == 'Manager & Up']['Count'].sum()
    associates = year_data[year_data['Level'] == 'Associate']['Count'].sum()
else:
    latest_year = 2025
    total_hc, managers_up, associates = 920, 184, 736

# Key Metrics Section
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5, gap="medium")

with col1:
    st.metric(
        label="Total Headcount",
        value=f"{total_hc:,}",
        delta=f"as of {latest_year}",
        help="Total employee count"
    )

with col2:
    st.metric(
        label="Managers & Up",
        value=f"{managers_up:,}",
        delta=f"{(managers_up/total_hc*100):.1f}% of workforce" if total_hc > 0 else "0%",
        help="Management and above positions"
    )

with col3:
    st.metric(
        label="Associates",
        value=f"{associates:,}",
        delta=f"{(associates/total_hc*100):.1f}% of workforce" if total_hc > 0 else "0%",
        help="Individual contributor level"
    )

with col4:
    st.metric(
        label="Avg Tenure",
        value="3.25 yrs",
        delta="Stable",
        help="Average years of service"
    )

with col5:
    st.metric(
        label="Retention Rate",
        value="91%",
        delta="+2% YoY",
        help="Employee retention rate"
    )

st.markdown("---")

# Charts Section
st.markdown("### 📊 Workforce Analysis")

# Row 1: Headcount and Service Years
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("#### Headcount Distribution by Level")
    fig1 = px.bar(
        filter_years(headcount_data),
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
    service_years = pd.DataFrame({
        'Tenure': [i for i in range(1, 11) for _ in range(100)],
        'Count': [1000 - i*50 for i in range(1, 11) for _ in range(100)]
    })
    fig2 = px.histogram(
        service_years,
        x='Tenure',
        y='Count',
        nbins=10,
        labels={'Tenure': 'Years of Service', 'Count': 'Number of Employees'},
        color_discrete_sequence=['#0066CC']
    )
    fig2.update_layout(
        height=400,
        hovermode='x unified',
        template='plotly_white'
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
