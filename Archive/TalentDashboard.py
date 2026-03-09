import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ABC Company - Talent Management Dashboard", layout="wide")
st.title("ABC Company - Talent Management Dashboard")

# Load talent data from latest year
talent_data = pd.DataFrame()
talent_year = None
for year in [2025, 2024, 2023, 2022, 2021, 2020, 2019]:
    try:
        talent_data = pd.read_excel("1 Talent Management (2019-2025).xlsx", sheet_name=str(year))
        talent_data.columns = talent_data.columns.str.strip()
        talent_year = year
        if not talent_data.empty:
            break
    except Exception:
        continue

# Add year selector (2019-2025) in sidebar, default to latest available year
years = list(range(2019, 2026))
default_year = talent_year if (talent_year in years) else 2025
selected_year = st.sidebar.selectbox("Select year", years, index=years.index(default_year))

# Reload data for the selected year (show empty if sheet not found)
try:
    talent_data = pd.read_excel("1 Talent Management (2019-2025).xlsx", sheet_name=str(selected_year))
    talent_data.columns = talent_data.columns.str.strip()
    talent_year = selected_year
except Exception:
    talent_data = pd.DataFrame()
    talent_year = selected_year

if talent_data.empty:
    st.error("No talent data found")
else:
    st.write(f"**Data loaded from year: {talent_year}**")
    
    # Display key counts (Position/Levels removed)
    col1 = st.columns(1)[0]
    
    with col1:
        employee_count = len(talent_data)
        st.metric("Total Employees", f"{employee_count:,}")
    
    st.divider()
    
    # categorize positions into two groups
    if "Position/Level" in talent_data.columns:
        def categorize_position(pos):
            if not isinstance(pos, str):
                return "Other"
            p = pos.lower()
            manager_keywords = ["manager", "director", "vp", "vice ", "chief", "head", "lead", "principal", "senior", "sr"]
            if any(k in p for k in manager_keywords):
                return "Managers and Up"
            if "associate" in p:
                return "Associate"
            # default fallback
            return "Associate"

        talent_data["PositionGroup"] = talent_data["Position/Level"].apply(categorize_position)

        # show aggregated metrics for the two groups
        mgr_count = int((talent_data["PositionGroup"] == "Managers and Up").sum())
        assoc_count = int((talent_data["PositionGroup"] == "Associate").sum())
        col_mgr, col_assoc = st.columns(2)
        with col_mgr:
            st.metric("Managers and Up", f"{mgr_count:,}")
        with col_assoc:
            st.metric("Associates", f"{assoc_count:,}")

        # aggregated bar chart (colored with legend)
        posgrp_counts = talent_data["PositionGroup"].value_counts()
        posgrp_df = posgrp_counts.rename_axis("PositionGroup").reset_index(name="Count")
        color_map = {"Managers and Up": "#1f77b4", "Associate": "#ff7f0e", "Other": "#7f7f7f"}
        fig_posgrp = px.bar(posgrp_df, x="PositionGroup", y="Count", color="PositionGroup",
                            color_discrete_map=color_map,
                            title="Employees: Managers and Up vs Associates",
                            labels={"PositionGroup": "Position Group", "Count": "Count"})
        fig_posgrp.update_layout(showlegend=True)
        st.plotly_chart(fig_posgrp, use_container_width=True)

    # Detailed Position/Level distribution removed
    
    # Generation distribution
    if "Generation" in talent_data.columns:
        gen_counts = talent_data["Generation"].value_counts()
        fig_gen = px.pie(names=gen_counts.index, values=gen_counts.values, title="Employee Distribution by Generation")
        st.plotly_chart(fig_gen, use_container_width=True)
    
    # Age distribution
    if "Age" in talent_data.columns:
        age_data = pd.to_numeric(talent_data["Age"], errors="coerce").dropna()
        fig_age = px.histogram(age_data, nbins=20, title="Age Distribution", labels={"value": "Age", "count": "Frequency"})
        st.plotly_chart(fig_age, use_container_width=True)
    
    # Tenure distribution
    if "Tenure" in talent_data.columns:
        tenure_data = pd.to_numeric(talent_data["Tenure"], errors="coerce").dropna()
        fig_tenure = px.histogram(tenure_data, nbins=20, title="Tenure Distribution", labels={"value": "Tenure (years)", "count": "Frequency"})
        st.plotly_chart(fig_tenure, use_container_width=True)
    
    st.divider()
    st.caption(f"Data source: 1 Talent Management (2019-2025).xlsx - Year {talent_year}")

# No code changes required to run. Ensure "1 Talent Management (2019-2025).xlsx" is in this folder
# or update the path inside the script.
