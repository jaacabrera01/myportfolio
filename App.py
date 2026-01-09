# App.py
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ABC Company - Workforce Analytics", layout="wide")

# -----------------------------
# Helper: load, clean, filter
# -----------------------------
def load_and_clean(path, rename_map=None, sheet_name=0):
    df = pd.read_excel(path, sheet_name=sheet_name)
    df.columns = df.columns.str.strip()  # remove spaces
    if rename_map:
        df = df.rename(columns=rename_map)
    # 🔑 keep only 2019–2025
    if "Year" in df.columns:
        df = df[(df["Year"] >= 2019) & (df["Year"] <= 2025)]
    return df

# -----------------------------
# Load datasets
# -----------------------------
headcount = load_and_clean("Resigned_Tracker_2019_2025.xlsx", {"Headcount": "HC"}, sheet_name="Resource Growth Tracker")
tenure = load_and_clean("Avg Tenure.xlsx", {"Average Tenure": "Tenure"})
ees = load_and_clean("EES.xlsx", {"Employee Engagement": "Engagement"})
retention = load_and_clean("Yearly Retention Rate.xlsx", {"Yearly Retention Rate": "Retention"})
promotions = load_and_clean("Promotion & Transfer.xlsx", {"Promotion & Transfer": "Promotions"})
id_overall = load_and_clean("Inclusion & Diversity - Overall.xlsx")
id_leaders = load_and_clean("Inclusion & Diversity - Leaders.xlsx")
social = load_and_clean("Social Impact.xlsx", {"Volunteerism - Participation Rate": "Volunteerism"})

# Load talent data - combine all year sheets
talent = pd.DataFrame()
for year in [2019, 2020, 2021, 2022, 2023, 2024, 2025]:
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

# -----------------------------
# Force year range 2019–2025
# -----------------------------
all_years = list(range(2019, 2026))

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.markdown("### Filters")
selected_years = st.sidebar.multiselect(
    "Select years",
    options=all_years,
    default=all_years,
)

def filter_years(df):
    return df[df["Year"].isin(selected_years)] if "Year" in df.columns else df

hc_f = filter_years(headcount)
tenure_f = filter_years(tenure)
ees_f = filter_years(ees)
rr_f = filter_years(retention)
pt_f = filter_years(promotions)
ido_f = filter_years(id_overall)
idl_f = filter_years(id_leaders)
si_f = filter_years(social)
talent_f = filter_years(talent)

# -----------------------------
# Summary metrics
# -----------------------------
def safe_mean(series):
    return pd.to_numeric(series, errors="coerce").dropna().mean()

def pct_fmt(x):
    return f"{x:.0%}" if not pd.isna(x) else "—"

latest_hc = 0
if not hc_f.empty:
    if "Year" in hc_f.columns:
        latest_year = hc_f["Year"].max()
        latest_row = hc_f[hc_f["Year"] == latest_year]
        if "Ending Headcount" in latest_row.columns:
            latest_hc = int(pd.to_numeric(latest_row["Ending Headcount"].iloc[0], errors="coerce") or 0)
    else:
        latest_hc = len(hc_f)

avg_tenure = safe_mean(tenure_f["Tenure"]) if not tenure_f.empty else np.nan
avg_retention = safe_mean(rr_f[rr_f["Year"] > 2019]["Retention"]) if not rr_f.empty else np.nan
avg_ees = safe_mean(ees_f["Engagement"]) if not ees_f.empty else np.nan
female_overall = safe_mean(ido_f["Female"]) if not ido_f.empty else np.nan

managers_count = 0
associates_count = 0
if not talent.empty:
    # Get the latest year's data from unfiltered talent
    latest_year = talent["Year"].max()
    latest_talent = talent[talent["Year"] == latest_year]
    if not latest_talent.empty:
        mgr_val = pd.to_numeric(latest_talent["Manager & Up"].iloc[0], errors="coerce")
        managers_count = int(mgr_val) if not pd.isna(mgr_val) else 0
        assoc_val = pd.to_numeric(latest_talent["Associates"].iloc[0], errors="coerce")
        associates_count = int(assoc_val) if not pd.isna(assoc_val) else 0

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
c1.metric("Headcount", f"{latest_hc:,}")
c2.metric("Managers and up", f"{managers_count:,}")
c3.metric("Associates", f"{associates_count:,}")
c4.metric("Avg tenure (years)", f"{avg_tenure:.2f}" if not pd.isna(avg_tenure) else "—")
c5.metric("Avg retention rate", pct_fmt(avg_retention))
c6.metric("Avg engagement score", f"{avg_ees:.2f}" if not pd.isna(avg_ees) else "—")
c7.metric("Female share (overall)", pct_fmt(female_overall))

st.divider()

# -----------------------------
# Charts
# -----------------------------
if not tenure_f.empty:
    st.plotly_chart(px.line(tenure_f, x="Year", y="Tenure", markers=True, title="Average tenure"), use_container_width=True)

if not pt_f.empty:
    st.plotly_chart(px.bar(pt_f, x="Year", y="Promotions", text="Promotions", title="Promotions & transfers"), use_container_width=True)

if not rr_f.empty:
    fig_rr = px.line(rr_f, x="Year", y="Retention", markers=True, title="Retention rate")
    fig_rr.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_rr, use_container_width=True)

if not ees_f.empty:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(avg_ees) if not pd.isna(avg_ees) else 0,
        number={"valueformat": ".2f"},
        title={"text": "Engagement"},
        gauge={"axis": {"range": [0, 1]}, "bar": {"color": "#ff7f0e"}}
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

if not ido_f.empty:
    df_pie_overall = pd.DataFrame({"Group": ["Female", "Male"], "Share": [safe_mean(ido_f["Female"]), safe_mean(ido_f["Male"])]})
    fig_pie_overall = px.pie(df_pie_overall, names="Group", values="Share", title="Gender distribution (overall)")
    st.plotly_chart(fig_pie_overall, use_container_width=True)

if not idl_f.empty:
    df_pie_leaders = pd.DataFrame({"Group": ["Female", "Male"], "Share": [safe_mean(idl_f["Female"]), safe_mean(idl_f["Male"])]})
    fig_pie_leaders = px.pie(df_pie_leaders, names="Group", values="Share", title="Gender distribution (leaders)")
    st.plotly_chart(fig_pie_leaders, use_container_width=True)

if not si_f.empty:
    fig_si = px.line(si_f, x="Year", y="Volunteerism", markers=True, title="Volunteerism - participation rate")
    fig_si.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_si, use_container_width=True)

# Talent Management chart
if not talent.empty:
    fig_talent = px.bar(talent, x="Year", y=["Manager & Up", "Associates"], barmode="group", title="Manager & Up and Associates by Year")
    st.plotly_chart(fig_talent, use_container_width=True)

st.caption("Data source: Excel files (filtered to 2019–2025).")
