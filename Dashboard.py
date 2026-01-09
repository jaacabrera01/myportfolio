import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Dashboard Layout ---
st.set_page_config(page_title="ABC Company - Key Metrics Dashboard", layout="wide")
st.title("ABC Company - Key Metrics Dashboard")

# Load data
headcount = pd.read_excel("Resigned_Tracker_2019_2025.xlsx", sheet_name="Resource Growth Tracker")
headcount.columns = headcount.columns.str.strip()

# Create year tabs for filtering
available_years = sorted(headcount["Year"].unique()) if "Year" in headcount.columns else [2019, 2020, 2021, 2022, 2023, 2024, 2025]

# Create tabs for each year
col_select = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
selected_year = None

for idx, year in enumerate(available_years):
    with col_select[idx % 8]:
        if st.button(str(year), key=f"year_{year}", use_container_width=True):
            st.session_state.selected_year = year

if "selected_year" not in st.session_state:
    st.session_state.selected_year = available_years[-1]

selected_year = st.session_state.selected_year

# Filter headcount data by selected year
headcount_filtered = headcount[headcount["Year"] <= selected_year]

# Load talent data
talent = pd.DataFrame()
for year in available_years:
    try:
        year_data = pd.read_excel("1 Talent Management (2019-2025).xlsx", sheet_name=str(year))
        year_data.columns = year_data.columns.str.strip()
        if not year_data.empty and "Manager & Up" in year_data.columns and "Associates" in year_data.columns:
            talent_summary = pd.DataFrame({
                "Year": [year],
                "Manager & Up": [pd.to_numeric(year_data["Manager & Up"].iloc[0], errors="coerce")],
                "Associates": [pd.to_numeric(year_data["Associates"].iloc[0], errors="coerce")]
            })
            talent = pd.concat([talent, talent_summary], ignore_index=True)
    except:
        continue

# Load additional data
try:
    generation = pd.read_excel("Resigned_Tracker_2019_2025.xlsx", sheet_name="Generation")
    generation.columns = generation.columns.str.strip()
except:
    generation = pd.DataFrame()

try:
    tenure_data = pd.read_excel("Resigned_Tracker_2019_2025.xlsx", sheet_name="Tenure")
    tenure_data.columns = tenure_data.columns.str.strip()
except:
    tenure_data = pd.DataFrame()

try:
    tenure = pd.read_excel("Avg Tenure.xlsx")
    tenure.columns = tenure.columns.str.strip()
    tenure.rename(columns={"Average Tenure": "Tenure"}, inplace=True)
except:
    tenure = pd.DataFrame()

try:
    retention = pd.read_excel("Yearly Retention Rate.xlsx")
    retention.columns = retention.columns.str.strip()
    retention.rename(columns={"Yearly Retention Rate": "Retention"}, inplace=True)
except:
    retention = pd.DataFrame()

# Calculate metrics
def safe_mean(series):
    return pd.to_numeric(series, errors="coerce").dropna().mean()

latest_hc = 0
if not headcount_filtered.empty and "Year" in headcount_filtered.columns:
    latest_row = headcount_filtered[headcount_filtered["Year"] == selected_year]
    if not latest_row.empty and "Ending Headcount" in latest_row.columns:
        latest_hc = int(pd.to_numeric(latest_row["Ending Headcount"].iloc[0], errors="coerce") or 0)

managers_count = 0
associates_count = 0
if not talent.empty:
    latest_talent = talent[talent["Year"] == selected_year]
    if not latest_talent.empty:
        mgr_val = pd.to_numeric(latest_talent["Manager & Up"].iloc[0], errors="coerce")
        managers_count = int(mgr_val) if not pd.isna(mgr_val) else 0
        assoc_val = pd.to_numeric(latest_talent["Associates"].iloc[0], errors="coerce")
        associates_count = int(assoc_val) if not pd.isna(assoc_val) else 0

avg_tenure = safe_mean(tenure["Tenure"]) if not tenure.empty else 0
avg_retention = safe_mean(retention[retention["Year"] > 2019]["Retention"]) if not retention.empty else 0

# Display metrics in key metric cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Headcount", f"{latest_hc:,}")
with col2:
    st.metric("Manager & Up", f"{managers_count:,}")
with col3:
    st.metric("Associates", f"{associates_count:,}")
with col4:
    st.metric("Avg Tenure", f"{avg_tenure:.2f}" if avg_tenure > 0 else "—")
with col5:
    st.metric("Avg Retention", f"{avg_retention:.0%}" if avg_retention > 0 else "—")

st.divider()

# Create a 2x2 grid layout for visualizations
col1, col2 = st.columns(2)

# Headcount by CY and Level
with col1:
    st.subheader("Headcount by CY and Level")
    if not talent.empty:
        talent_filtered = talent[talent["Year"] <= selected_year]
        fig = px.bar(talent_filtered, x="Year", y=["Associates", "Manager & Up"], 
                     title="Headcount by Year and Level", barmode="stack",
                     labels={"value": "Count", "variable": "Level"})
        fig.for_each_trace(lambda t: t.update(name = "Associates" if "Associates" in t.name else "Manager & Up"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available")

# Headcount Trend
with col2:
    st.subheader("Headcount Trend")
    if not headcount_filtered.empty:
        fig = px.line(headcount_filtered, x="Year", y="Ending Headcount", 
                      title="Headcount Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available")

col3, col4 = st.columns(2)

# Generation Distribution
with col3:
    st.subheader("Generation Distribution")
    if not generation.empty:
        gen_data = generation[generation["Fiscal Year"] == selected_year]
        if not gen_data.empty:
            gen_cols = [col for col in generation.columns if col not in ["Fiscal Year", "Total"]]
            gen_row = gen_data.iloc[0]
            gen_values = [gen_row[col] for col in gen_cols if col in gen_data.columns]
            fig = px.pie(names=gen_cols, values=gen_values, title="Generation Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data for selected year")
    else:
        st.write("No generation data available")

# Retention Rate Trend
with col4:
    st.subheader("Retention Rate Trend")
    if not retention.empty:
        retention_filtered = retention[retention["Year"] <= selected_year]
        fig = px.line(retention_filtered, x="Year", y="Retention", 
                      title="Retention Rate Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No retention data available")

st.divider()
st.caption("Data source: Excel files (2019–2025)")