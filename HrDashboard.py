import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback_context, ALL
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Config
# -----------------------------
EXCEL_PATH = "HR_Main_DO_NOT_EDIT.xlsx"
APP_TITLE = "HR Analytics Dashboard (2019–2025)"

# -----------------------------
# Helpers: sheet detection
# -----------------------------
def identify_sheet(df: pd.DataFrame):
    cols = set([c.strip().lower() for c in df.columns])
    if {"employee", "resignation date", "resigned year"}.issubset(cols):
        return "resigned"
    if {"employee", "joining date", "joined year"}.issubset(cols):
        return "joined"
    if {"resigned year", "resigned month name", "number of resignations"}.issubset(cols):
        return "resignation_summary"
    if {"joined year", "joined month name", "number of joins"}.issubset(cols):
        return "join_summary"
    if {"year", "starting headcount", "ending headcount"}.issubset(cols):
        return "resource_growth"
    if {"year", "promotion & transfer"}.issubset(cols):
        return "promotions_transfers"
    if {"fiscal year", "baby boomer", "gen x", "gen z", "millennial", "total"}.issubset(cols):
        return "generation"
    if {"fiscal year", "total"}.issubset(cols) and set([str(i) for i in range(0, 11)]) <= cols:
        return "tenure"
    if {"fiscal year", "total"}.issubset(cols) and "43" in cols and "37" in cols:
        return "age"
    if {"fiscal year", "corporate culture", "total"}.issubset(cols):
        return "ee_count"
    if {"fiscal year", "corporate culture"}.issubset(cols) and "appraisals" in cols:
        return "ee_percentage"
    if {"fiscal year", "associate", "manager & up", "total"}.issubset(cols):
        return "position_level"
    if {"year", "female", "male"}.issubset(cols):
        # Could be overall or leaders; distinguish by sheet name later
        return "distribution_generic"
    if {"year", "average tenure"}.issubset(cols):
        return "avg_tenure"
    if {"year", "yearly retention rate"}.issubset(cols):
        return "avg_retention"
    return "unknown"

def standardize_columns(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

# -----------------------------
# Load all sheets
# -----------------------------
sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)
catalog = {}

# Attempt to classify each sheet
for name, df in sheets.items():
    df = standardize_columns(df)
    key = identify_sheet(df)
    catalog.setdefault(key, []).append((name, df))

# Pick primary sheet per type (if multiple, take the first)
def pick_first(key):
    return catalog[key][0][1] if key in catalog and len(catalog[key]) > 0 else None

df_resigned = pick_first("resigned")
df_joined = pick_first("joined")
df_resign_summary = pick_first("resignation_summary")
df_join_summary = pick_first("join_summary")
df_growth = pick_first("resource_growth")
df_promotions = pick_first("promotions_transfers")
df_generation = pick_first("generation")
df_tenure = pick_first("tenure")
df_age = pick_first("age")
df_ee_count = pick_first("ee_count")
df_ee_pct = pick_first("ee_percentage")
df_position = pick_first("position_level")
df_avg_tenure = pick_first("avg_tenure")
df_avg_retention = pick_first("avg_retention")

# Identify distribution sheets (leaders vs overall) by sheet names as fallback
df_dist_overall = None
df_dist_leaders = None
if "distribution_generic" in catalog:
    # Heuristics: sheet name contains "Overall" or "Leaders"
    for nm, df in catalog["distribution_generic"]:
        lname = nm.lower()
        if "leader" in lname:
            df_dist_leaders = df
        elif "overall" in lname:
            df_dist_overall = df
    # If not found by name, assign first to overall, second to leaders
    if df_dist_overall is None and df_dist_leaders is None:
        if len(catalog["distribution_generic"]) >= 1:
            df_dist_overall = catalog["distribution_generic"][0][1]
        if len(catalog["distribution_generic"]) >= 2:
            df_dist_leaders = catalog["distribution_generic"][1][1]

# -----------------------------
# Cleaning & normalization
# -----------------------------
def as_int_series(s):
    return pd.to_numeric(s, errors="coerce").astype("Int64")

def ensure_year_bounds(df, year_col="Year", min_y=2019, max_y=2025):
    if df is None or year_col not in df.columns:
        return df
    df = df[(pd.to_numeric(df[year_col], errors="coerce") >= min_y) &
            (pd.to_numeric(df[year_col], errors="coerce") <= max_y)]
    return df

# Normalize growth
if df_growth is not None:
    df_growth["Year"] = pd.to_numeric(df_growth["Year"], errors="coerce")
    df_growth = df_growth.dropna(subset=["Year"])
    df_growth = df_growth[(df_growth["Year"] >= 2019) & (df_growth["Year"] <= 2025)]
    # Ensure numeric
    for col in ["Starting Headcount", "Joins", "Resignations", "Net Change", "Ending Headcount", "Growth Rate (%)"]:
        df_growth[col] = pd.to_numeric(df_growth[col], errors="coerce")

# Normalize resign/join detail
if df_resigned is not None:
    # Convert excel serial dates if they are numeric
    if np.issubdtype(df_resigned["Resignation Date"].dtype, np.number):
        df_resigned["Resignation Date"] = pd.to_datetime("1899-12-30") + pd.to_timedelta(df_resigned["Resignation Date"], unit="D")
    df_resigned["Resigned Year"] = pd.to_numeric(df_resigned["Resigned Year"], errors="coerce")
    df_resigned["Resigned Month"] = pd.to_numeric(df_resigned.get("Resigned Month", np.nan), errors="coerce")
    df_resigned["Resigned Quarter"] = df_resigned.get("Resigned Quarter", "Unknown")
    df_resigned["Resigned Month Name"] = df_resigned.get("Resigned Month Name", "Unknown")
    df_resigned = df_resigned[(df_resigned["Resigned Year"] >= 2019) & (df_resigned["Resigned Year"] <= 2025)]

if df_joined is not None:
    if np.issubdtype(df_joined["Joining Date"].dtype, np.number):
        df_joined["Joining Date"] = pd.to_datetime("1899-12-30") + pd.to_timedelta(df_joined["Joining Date"], unit="D")
    df_joined["Joined Year"] = pd.to_numeric(df_joined["Joined Year"], errors="coerce")
    df_joined["Joined Month"] = pd.to_numeric(df_joined.get("Joined Month", np.nan), errors="coerce")
    df_joined["Joined Quarter"] = df_joined.get("Joined Quarter", "Unknown")
    df_joined["Joined Month Name"] = df_joined.get("Joined Month Name", "Unknown")
    df_joined = df_joined[(df_joined["Joined Year"] >= 2019) & (df_joined["Joined Year"] <= 2025)]

# Normalize summaries
def normalize_summary(df, year_col, month_name_col, count_col):
    if df is None:
        return None
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df = df.dropna(subset=[year_col])
    df = df[(df[year_col] >= 2019) & (df[year_col] <= 2025)]
    df[count_col] = pd.to_numeric(df[count_col], errors="coerce")
    df[month_name_col] = df[month_name_col].astype(str)
    return df

df_resign_summary = normalize_summary(df_resign_summary, "Resigned Year", "Resigned Month Name", "Number of Resignations")
df_join_summary = normalize_summary(df_join_summary, "Joined Year", "Joined Month Name", "Number of Joins")

# Normalize generation
if df_generation is not None:
    df_generation["Fiscal Year"] = pd.to_numeric(df_generation["Fiscal Year"], errors="coerce")
    df_generation = df_generation[(df_generation["Fiscal Year"] >= 2019) & (df_generation["Fiscal Year"] <= 2025)]
    for col in ["Baby Boomer", "Gen X", "Gen Z", "Millennial", "Total"]:
        df_generation[col] = pd.to_numeric(df_generation[col], errors="coerce")

# Normalize position level
if df_position is not None:
    df_position["Fiscal Year"] = pd.to_numeric(df_position["Fiscal Year"], errors="coerce")
    df_position = df_position[(df_position["Fiscal Year"] >= 2019) & (df_position["Fiscal Year"] <= 2025)]
    for col in ["Associate", "Manager & Up", "Total"]:
        df_position[col] = pd.to_numeric(df_position[col], errors="coerce")

# Normalize distributions
for dist_df in [df_dist_overall, df_dist_leaders]:
    if dist_df is not None:
        dist_df["Year"] = pd.to_numeric(dist_df["Year"], errors="coerce")
        dist_df["Female"] = pd.to_numeric(dist_df["Female"], errors="coerce")
        dist_df["Male"] = pd.to_numeric(dist_df["Male"], errors="coerce")

# Normalize retention
if df_avg_retention is not None:
    df_avg_retention["Year"] = pd.to_numeric(df_avg_retention["Year"], errors="coerce")
    df_avg_retention["Yearly Retention Rate"] = pd.to_numeric(df_avg_retention["Yearly Retention Rate"], errors="coerce")
    df_avg_retention = df_avg_retention[(df_avg_retention["Year"] >= 2019) & (df_avg_retention["Year"] <= 2025)]

# Retention rule: 2019 shown as 0%; avg blank if only 2019 selected will be handled in callback

# -----------------------------
# App
# -----------------------------
app = Dash(__name__)
app.title = APP_TITLE
server = app.server

YEARS = list(range(2019, 2026))
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
MONTHS = [
    "January","February","March","April","May","June","July","August","September","October","November","December"
]

def headcount_figure(selected_years=None):
    if df_growth is None or df_growth.empty:
        return go.Figure()
    data = df_growth.copy()
    if selected_years:
        data = data[data["Year"].isin(selected_years)]
    fig = px.bar(
        data,
        x="Year",
        y="Ending Headcount",
        text="Ending Headcount",
        title="Ending Headcount by Year",
        color="Growth Rate (%)",
        color_continuous_scale="Blues"
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(yaxis_title="Headcount", hovermode="x unified")
    return fig

def resignations_by_month_figure(selected_years=None, selected_quarters=None, selected_months=None, click_year=None):
    if df_resign_summary is None or df_resign_summary.empty:
        return go.Figure()
    data = df_resign_summary.copy()
    if click_year is not None:
        data = data[data["Resigned Year"] == click_year]
    elif selected_years:
        data = data[data["Resigned Year"].isin(selected_years)]
    if selected_quarters and "Resigned Quarter" in data.columns:
        data = data[data["Resigned Quarter"].isin(selected_quarters)]
    if selected_months:
        data = data[data["Resigned Month Name"].isin(selected_months)]
    fig = px.bar(
        data,
        x="Resigned Month Name",
        y="Number of Resignations",
        color="Resigned Year",
        barmode="group",
        title="Resignations by Month",
        category_orders={"Resigned Month Name": MONTHS}
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Resignations", hovermode="x unified")
    return fig

def joins_by_month_figure(selected_years=None, selected_quarters=None, selected_months=None, click_year=None):
    if df_join_summary is None or df_join_summary.empty:
        return go.Figure()
    data = df_join_summary.copy()
    if click_year is not None:
        data = data[data["Joined Year"] == click_year]
    elif selected_years:
        data = data[data["Joined Year"].isin(selected_years)]
    if selected_quarters and "Joined Quarter" in data.columns:
        data = data[data["Joined Quarter"].isin(selected_quarters)]
    if selected_months:
        data = data[data["Joined Month Name"].isin(selected_months)]
    fig = px.bar(
        data,
        x="Joined Month Name",
        y="Number of Joins",
        color="Joined Year",
        barmode="group",
        title="Joins by Month",
        category_orders={"Joined Month Name": MONTHS}
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Joins", hovermode="x unified")
    return fig

def generation_stack_figure(selected_years=None, click_year=None):
    if df_generation is None or df_generation.empty:
        return go.Figure()
    data = df_generation.copy()
    if click_year is not None:
        data = data[data["Fiscal Year"] == click_year]
    elif selected_years:
        data = data[data["Fiscal Year"].isin(selected_years)]
    data_m = data.melt(id_vars=["Fiscal Year", "Total"], value_vars=["Baby Boomer","Gen X","Gen Z","Millennial"], var_name="Generation", value_name="Count")
    fig = px.bar(
        data_m,
        x="Fiscal Year",
        y="Count",
        color="Generation",
        title="Generation composition by fiscal year",
        barmode="stack"
    )
    fig.update_layout(hovermode="x unified")
    return fig

def position_level_figure(selected_years=None, click_year=None):
    if df_position is None or df_position.empty:
        return go.Figure()
    data = df_position.copy()
    if click_year is not None:
        data = data[data["Fiscal Year"] == click_year]
    elif selected_years:
        data = data[data["Fiscal Year"].isin(selected_years)]
    data_m = data.melt(id_vars=["Fiscal Year", "Total"], value_vars=["Associate","Manager & Up"], var_name="Level", value_name="Count")
    fig = px.bar(
        data_m,
        x="Fiscal Year",
        y="Count",
        color="Level",
        barmode="group",
        title="Position level mix"
    )
    fig.update_layout(hovermode="x unified")
    return fig

def gender_pie_figure(year=None, leaders=False):
    df_dist = df_dist_leaders if leaders else df_dist_overall
    title_prefix = "Leaders" if leaders else "Overall"
    if df_dist is None or df_dist.empty:
        return go.Figure()
    data = df_dist.copy()
    if year is not None:
        row = data[data["Year"] == year]
        if not row.empty:
            vals = row.iloc[0][["Female","Male"]]
            fig = px.pie(values=vals.values, names=["Female","Male"], title=f"Gender distribution ({title_prefix}) - {year}")
            return fig
    # fallback: latest year
    latest = int(data["Year"].max())
    row = data[data["Year"] == latest]
    vals = row.iloc[0][["Female","Male"]]
    fig = px.pie(values=vals.values, names=["Female","Male"], title=f"Gender distribution ({title_prefix}) - {latest}")
    return fig

def retention_figure(selected_years=None):
    if df_avg_retention is None or df_avg_retention.empty:
        return go.Figure()
    data = df_avg_retention.copy()
    if selected_years:
        data = data[data["Year"].isin(selected_years)]
    # Rule: show 2019 as 0%; if only 2019 selected, show blank avg
    data = data.copy()
    data.loc[data["Year"] == 2019, "Yearly Retention Rate"] = 0.0
    fig = px.line(
        data,
        x="Year",
        y="Yearly Retention Rate",
        markers=True,
        title="Yearly retention rate"
    )
    fig.update_yaxes(ticksuffix="")
    fig.update_layout(hovermode="x unified", yaxis_title="Retention rate")
    return fig

def kpi_cards(selected_years=None, click_year=None):
    # Headcount, joins, resignations, net change for year or range
    dfg = df_growth.copy() if df_growth is not None else pd.DataFrame()
    if dfg.empty:
        return "—", "—", "—", "—"
    if click_year is not None:
        dfg = dfg[dfg["Year"] == click_year]
    elif selected_years:
        dfg = dfg[dfg["Year"].isin(selected_years)]
    if dfg.empty:
        return "—", "—", "—", "—"
    # Aggregate over selected years
    ending = int(dfg["Ending Headcount"].iloc[-1]) if click_year is not None else int(dfg["Ending Headcount"].max())
    joins = int(dfg["Joins"].sum())
    resigns = int(dfg["Resignations"].sum())
    net = int(dfg["Net Change"].sum())
    return f"{ending:,}", f"{joins:,}", f"{resigns:,}", f"{net:,}"

# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div([
    html.Div([
        html.H1(APP_TITLE, style={"textAlign": "center", "color": "#003d82", "marginBottom": "1rem", "marginTop": "1rem"})
    ]),
    
    # Year tabs
    html.Div([
        html.Button("Select all", id="select-all-btn", n_clicks=0, style={"marginRight": "1rem", "padding": "0.5rem 1rem"}),
        *[
            html.Button(
                str(year),
                id={"type": "year-btn", "index": year},
                n_clicks=0,
                style={
                    "marginRight": "0.5rem",
                    "padding": "0.5rem 1rem",
                    "backgroundColor": "#003d82" if year == 2025 else "#e0e0e0",
                    "color": "white" if year == 2025 else "black",
                    "border": "none",
                    "borderRadius": "4px",
                    "cursor": "pointer",
                    "fontWeight": "bold" if year == 2025 else "normal"
                }
            )
            for year in YEARS
        ]
    ], style={"display": "flex", "justifyContent": "center", "marginBottom": "1.5rem", "gap": "0.5rem", "flexWrap": "wrap"}),

    # KPI Cards Row
    html.Div([
        html.Div([
            html.Div("1K", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": "#003d82"}),
            html.Div("Headcount", style={"fontSize": "0.9rem", "color": "#666"})
        ], style={
            "flex": 1, "textAlign": "center", "border": "2px solid #e0e0e0", "padding": "1.5rem",
            "borderRadius": "8px", "marginRight": "0.5rem"
        }),
        html.Div([
            html.Div(id="kpi-managers", children="224", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": "#003d82"}),
            html.Div("Manager and up", style={"fontSize": "0.9rem", "color": "#666"})
        ], style={
            "flex": 1, "textAlign": "center", "border": "2px solid #e0e0e0", "padding": "1.5rem",
            "borderRadius": "8px", "marginRight": "0.5rem"
        }),
        html.Div([
            html.Div(id="kpi-associates", children="879", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": "#003d82"}),
            html.Div("Associates", style={"fontSize": "0.9rem", "color": "#666"})
        ], style={
            "flex": 1, "textAlign": "center", "border": "2px solid #e0e0e0", "padding": "1.5rem",
            "borderRadius": "8px", "marginRight": "0.5rem"
        }),
        html.Div([
            html.Div(id="kpi-tenure", children="3.25", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": "#003d82"}),
            html.Div("Avg Tenure", style={"fontSize": "0.9rem", "color": "#666"})
        ], style={
            "flex": 1, "textAlign": "center", "border": "2px solid #e0e0e0", "padding": "1.5rem",
            "borderRadius": "8px", "marginRight": "0.5rem"
        }),
        html.Div([
            html.Div(id="kpi-retention", children="91%", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": "#003d82"}),
            html.Div("Avg Retention Rate", style={"fontSize": "0.9rem", "color": "#666"})
        ], style={
            "flex": 1, "textAlign": "center", "border": "2px solid #e0e0e0", "padding": "1.5rem",
            "borderRadius": "8px"
        })
    ], style={"display": "flex", "marginBottom": "1.5rem", "gap": "0.5rem"}),

    # Row 1: Headcount by Level + Service Years
    html.Div([
        html.Div([
            dcc.Graph(id="headcount-by-level-chart")
        ], style={"flex": 1, "paddingRight": "0.5rem"}),
        html.Div([
            dcc.Graph(id="service-years-chart")
        ], style={"flex": 1, "paddingLeft": "0.5rem"})
    ], style={"display": "flex", "marginBottom": "1.5rem"}),

    # Row 2: Promotions + Retention Rate
    html.Div([
        html.Div([
            dcc.Graph(id="promotions-chart")
        ], style={"flex": 1, "paddingRight": "0.5rem"}),
        html.Div([
            dcc.Graph(id="retention-rate-chart")
        ], style={"flex": 1, "paddingLeft": "0.5rem"})
    ], style={"display": "flex", "marginBottom": "1.5rem"}),

    # Row 3: Distribution + Generation
    html.Div([
        html.Div([
            dcc.Graph(id="distribution-chart")
        ], style={"flex": 1, "paddingRight": "0.5rem"}),
        html.Div([
            dcc.Graph(id="generation-chart")
        ], style={"flex": 1, "paddingLeft": "0.5rem"})
    ], style={"display": "flex"}),

    # Store for selected year
    dcc.Store(id="selected-years-store", data=[2025])
], style={"padding": "1rem", "fontFamily": "Arial, sans-serif", "backgroundColor": "#f5f5f5"})

# Callback to handle year button clicks
@app.callback(
    Output("selected-years-store", "data"),
    [Input({"type": "year-btn", "index": ALL}, "n_clicks"),
     Input("select-all-btn", "n_clicks")],
    prevent_initial_call=False
)
def update_selected_years(year_clicks, select_all_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return [2025]
    
    trigger_id = ctx.triggered[0]["prop_id"]
    
    if "select-all-btn" in trigger_id:
        return YEARS
    
    # Find which year button was clicked
    if "year-btn" in trigger_id:
        import json
        year_data = json.loads(trigger_id.split(".")[0])
        clicked_year = year_data["index"]
        
        current_selection = ctx.states.get("selected-years-store.data", [2025])
        if not isinstance(current_selection, list):
            current_selection = [current_selection]
        
        if clicked_year in current_selection:
            current_selection.remove(clicked_year)
        else:
            current_selection.append(clicked_year)
        
        if current_selection:
            return sorted(current_selection)
        else:
            return [2025]
    
    return [2025]

# Callback to update year button styles
@app.callback(
    [Output({"type": "year-btn", "index": ALL}, "style")],
    Input("selected-years-store", "data")
)
def update_button_styles(selected_years):
    if not selected_years:
        selected_years = [2025]
    
    styles = []
    for year in YEARS:
        if year in selected_years:
            styles.append({
                "marginRight": "0.5rem",
                "padding": "0.5rem 1rem",
                "backgroundColor": "#003d82",
                "color": "white",
                "border": "none",
                "borderRadius": "4px",
                "cursor": "pointer",
                "fontWeight": "bold"
            })
        else:
            styles.append({
                "marginRight": "0.5rem",
                "padding": "0.5rem 1rem",
                "backgroundColor": "#e0e0e0",
                "color": "black",
                "border": "none",
                "borderRadius": "4px",
                "cursor": "pointer",
                "fontWeight": "normal"
            })
    return [styles]

# Main callback to update all charts and KPIs
@app.callback(
    Output("headcount-by-level-chart", "figure"),
    Output("service-years-chart", "figure"),
    Output("promotions-chart", "figure"),
    Output("retention-rate-chart", "figure"),
    Output("distribution-chart", "figure"),
    Output("generation-chart", "figure"),
    Output("kpi-managers", "children"),
    Output("kpi-associates", "children"),
    Output("kpi-tenure", "children"),
    Output("kpi-retention", "children"),
    Input("selected-years-store", "data")
)
def update_all_charts(selected_years):
    if not selected_years:
        selected_years = [2025]
    
    try:
        # Generate figures
        headcount_fig = headcount_by_level_figure(selected_years)
        service_years_fig = service_years_figure(selected_years)
        promotions_fig = promotions_figure(selected_years)
        retention_fig = retention_figure(selected_years)
        dist_fig = distribution_figure(selected_years)
        gen_fig = generation_stack_figure(selected_years)
        
        # KPI values
        managers = get_manager_count(selected_years)
        associates = get_associates_count(selected_years)
        tenure = get_avg_tenure(selected_years)
        retention = get_avg_retention(selected_years)
        
        return (headcount_fig, service_years_fig, promotions_fig, retention_fig, 
                dist_fig, gen_fig, managers, associates, tenure, retention)
    except Exception as e:
        print(f"Error in update_all_charts: {e}")
        # Return empty figures if error
        empty_fig = go.Figure().update_layout(title="Error loading chart")
        return (empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "N/A", "N/A", "N/A", "N/A")

# Helper functions for KPI values
def get_manager_count(years):
    try:
        if df_position is None:
            return "0"
        filtered_df = df_position[df_position["Fiscal Year"].isin(years)]
        managers = filtered_df[filtered_df["Position"] == "Manager and above"]["Count"].sum()
        return str(int(managers)) if managers > 0 else "0"
    except:
        return "0"

def get_associates_count(years):
    try:
        if df_position is None:
            return "0"
        filtered_df = df_position[df_position["Fiscal Year"].isin(years)]
        associates = filtered_df[filtered_df["Position"] == "Associate"]["Count"].sum()
        return str(int(associates)) if associates > 0 else "0"
    except:
        return "0"

def get_avg_tenure(years):
    try:
        if df_avg_tenure is None:
            return "N/A"
        filtered_df = df_avg_tenure[df_avg_tenure["Year"].isin(years)]
        avg_tenure = filtered_df["Average Tenure"].mean()
        return f"{avg_tenure:.2f}" if avg_tenure > 0 else "N/A"
    except:
        return "N/A"

def get_avg_retention(years):
    try:
        if df_avg_retention is None:
            return "N/A"
        filtered_df = df_avg_retention[df_avg_retention["Year"].isin(years)]
        avg_ret = filtered_df["Average Retention Rate"].mean() * 100
        return f"{avg_ret:.0f}%" if avg_ret > 0 else "N/A"
    except:
        return "N/A"

# Figure generation functions
def headcount_by_level_figure(years):
    try:
        if df_position is None:
            return go.Figure().update_layout(title="Headcount by CY and Level")
        filtered_df = df_position[df_position["Fiscal Year"].isin(years)].copy()
        filtered_df.rename(columns={"Fiscal Year": "Year"}, inplace=True)
        fig = px.bar(filtered_df, x="Year", y="Count", color="Position", 
                     title="Headcount by CY and Level", barmode="stack",
                     color_discrete_map={"Manager and above": "#003d82", "Associate": "#0066cc"})
        return fig
    except:
        return go.Figure().update_layout(title="Headcount by CY and Level")

def service_years_figure(years):
    try:
        if df_tenure is None:
            return go.Figure().update_layout(title="Service Years")
        filtered_df = df_tenure[df_tenure["Year"].isin(years)]
        fig = px.bar(filtered_df, x="Count", y="Tenure", orientation="h",
                     title="Service Years", color="Tenure",
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        return fig
    except:
        return go.Figure().update_layout(title="Service Years")

def promotions_figure(years):
    try:
        if df_promotions is None:
            return go.Figure().update_layout(title="Promotions & Transfers")
        filtered_df = df_promotions[df_promotions["Year"].isin(years)]
        if filtered_df.empty:
            return go.Figure().update_layout(title="Promotions & Transfers")
        # Group by year if multiple rows
        grouped = filtered_df.groupby("Year")["Count"].sum().reset_index()
        fig = px.bar(grouped, x="Year", y="Count",
                     title="Promotions & Transfers",
                     color_discrete_sequence=["#003d82"])
        return fig
    except:
        return go.Figure().update_layout(title="Promotions & Transfers")

def retention_figure(years):
    try:
        if df_avg_retention is None:
            return go.Figure().update_layout(title="Retention Rate")
        filtered_df = df_avg_retention[df_avg_retention["Year"].isin(years)]
        if filtered_df.empty:
            return go.Figure().update_layout(title="Retention Rate")
        fig = px.line(filtered_df, x="Year", y="Average Retention Rate",
                      title="Retention Rate", markers=True, 
                      color_discrete_sequence=["#003d82"])
        fig.update_yaxes(tickformat=".0%")
        return fig
    except:
        return go.Figure().update_layout(title="Retention Rate")

def distribution_figure(years):
    try:
        if df_dist_overall is None:
            return go.Figure().update_layout(title="Distribution (Gender)")
        filtered_df = df_dist_overall[df_dist_overall["Year"].isin(years)]
        if filtered_df.empty:
            return go.Figure().update_layout(title="Distribution (Gender)")
        # Group by gender
        gender_dist = filtered_df.groupby("Gender")["Count"].sum()
        fig = px.pie(values=gender_dist.values, names=gender_dist.index,
                     title="Distribution (Gender) - Inclusion & Diversity",
                     color_discrete_sequence=["#003d82", "#0066cc"])
        return fig
    except:
        return go.Figure().update_layout(title="Distribution (Gender)")

def generation_stack_figure(years):
    try:
        if df_generation is None:
            return go.Figure().update_layout(title="Generation")
        filtered_df = df_generation[df_generation["Year"].isin(years)]
        if filtered_df.empty:
            return go.Figure().update_layout(title="Generation")
        # Group by generation if multiple rows per generation
        grouped = filtered_df.groupby("Generation")["Count"].sum().reset_index()
        fig = px.pie(grouped, names="Generation", values="Count",
                     title="Generation",
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        return fig
    except:
        return go.Figure().update_layout(title="Generation")

# Run
if __name__ == "__main__":
    app.run_server(debug=True)
