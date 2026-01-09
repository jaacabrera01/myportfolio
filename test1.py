import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, callback_context
import dash
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Load Excel
# -----------------------------
EXCEL_PATH = "HR_Main_DO_NOT_EDIT.xlsx"
sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)

# For demo, we’ll just use the Resigned Employees sheet
df_resigned = sheets.get("Resigned Employees")
df_resigned.columns = [c.strip() for c in df_resigned.columns]

# Convert Excel serial dates to datetime
if np.issubdtype(df_resigned["Resignation Date"].dtype, np.number):
    df_resigned["Resignation Date"] = pd.to_datetime("1899-12-30") + pd.to_timedelta(df_resigned["Resignation Date"], unit="D")

df_resigned["Resigned Year"] = df_resigned["Resigned Year"].astype(int)
df_resigned["Resigned Month Name"] = df_resigned["Resigned Month Name"].astype(str)
if "Resigned Quarter" in df_resigned.columns:
    df_resigned["Resigned Quarter"] = df_resigned["Resigned Quarter"].astype(str)

# Include years from Resigned Employees data
YEARS = sorted([int(y) for y in df_resigned["Resigned Year"].dropna().unique()])
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# Print available years
print(f"YEARS: {YEARS}")
print(f"Min Year: {min(YEARS)}, Max Year: {max(YEARS)}")

# -----------------------------
# App
# -----------------------------
app = Dash(__name__)
app.title = "HR Analytics Dashboard"
server = app.server

app.layout = html.Div([
    html.H1("HR Analytics Dashboard (Cross-Linked)", style={"marginBottom":"1rem"}),

    html.Div([
        html.Label("Select Year:", style={"marginRight":"1rem"}),
        dcc.Dropdown(
            id="year-dropdown",
            options=[{"label": str(y), "value": y} for y in YEARS],
            value=min(YEARS),
            style={"width":"150px", "display":"inline-block"}
        ),
    ], style={"marginBottom":"1rem"}),

    html.Button("Reset filters", id="reset-btn", n_clicks=0, style={"marginLeft":"1rem"}),

    html.Div([
        dcc.Graph(id="headcount-chart"),
        dcc.Graph(id="resignations-chart"),
        dcc.Graph(id="joins-chart"),
    ], style={"display":"flex","flexWrap":"wrap"}),

    html.Div([
        dcc.Graph(id="generation-chart"),
        dcc.Graph(id="position-chart"),
        dcc.Graph(id="gender-chart"),
        dcc.Graph(id="retention-chart"),
    ], style={"display":"flex","flexWrap":"wrap"})
])

# -----------------------------
# Figures
# -----------------------------
def headcount_fig(df):
    data = df.groupby("Resigned Year").size().reset_index(name="Count")
    fig = px.bar(data, x="Resigned Year", y="Count", title="Headcount by Year")
    return fig

def resignations_fig(df):
    data = df.groupby(["Resigned Year","Resigned Month Name"]).size().reset_index(name="Count")
    fig = px.bar(data, x="Resigned Month Name", y="Count", color="Resigned Year",
                 category_orders={"Resigned Month Name":MONTHS},
                 title="Resignations by Month")
    return fig

def joins_fig(df):
    # Demo only: using same data, but you’d replace with actual Joins sheet
    data = df.groupby(["Resigned Year","Resigned Quarter"]).size().reset_index(name="Count")
    fig = px.bar(data, x="Resigned Quarter", y="Count", color="Resigned Year", barmode="group",
                 title="Joins by Quarter (demo)")
    return fig

def generation_fig(df, year=None):
    # Demo only: fake generation split
    if year:
        vals = {"Gen X":40,"Millennial":50,"Gen Z":30}
        fig = px.pie(values=list(vals.values()), names=list(vals.keys()), title=f"Generation split {year}")
    else:
        fig = go.Figure()
    return fig

def position_fig(df, year=None):
    # Demo only: fake position split
    if year:
        vals = {"Associate":70,"Manager & Up":30}
        fig = px.pie(values=list(vals.values()), names=list(vals.keys()), title=f"Position split {year}")
    else:
        fig = go.Figure()
    return fig

def gender_fig(df, year=None):
    # Demo only: fake gender split
    if year:
        vals = {"Female":55,"Male":45}
        fig = px.pie(values=list(vals.values()), names=list(vals.keys()), title=f"Gender split {year}")
    else:
        fig = go.Figure()
    return fig

def retention_fig(df, years):
    # Demo only: retention line
    data = pd.DataFrame({"Year":years,"Retention":[0 if y==2019 else 90 for y in years]})
    fig = px.line(data, x="Year", y="Retention", markers=True, title="Retention Rate")
    return fig

# -----------------------------
# Callbacks
# -----------------------------
@app.callback(
    Output("headcount-chart","figure"),
    Output("resignations-chart","figure"),
    Output("joins-chart","figure"),
    Output("generation-chart","figure"),
    Output("position-chart","figure"),
    Output("gender-chart","figure"),
    Output("retention-chart","figure"),
    Input("year-dropdown","value"),
    Input("reset-btn","n_clicks")
)
def update_all(selected_year, reset_clicks):
    ctx = callback_context
    
    # If reset button clicked, use first year
    if ctx.triggered and ctx.triggered[0]["prop_id"].split(".")[0] == "reset-btn":
        selected_year = min(YEARS)
    
    # Filter data for selected year
    df_filtered = df_resigned[df_resigned["Resigned Year"] == selected_year]
    
    # If no data for this year, return empty figures
    if df_filtered.empty:
        return (
            go.Figure().add_annotation(text=f"No data for {selected_year}"),
            go.Figure().add_annotation(text=f"No data for {selected_year}"),
            go.Figure().add_annotation(text=f"No data for {selected_year}"),
            go.Figure().add_annotation(text=f"No data for {selected_year}"),
            go.Figure().add_annotation(text=f"No data for {selected_year}"),
            go.Figure().add_annotation(text=f"No data for {selected_year}"),
            go.Figure().add_annotation(text=f"No data for {selected_year}")
        )

    return (
        headcount_fig(df_filtered),
        resignations_fig(df_filtered),
        joins_fig(df_filtered),
        generation_fig(df_filtered, selected_year),
        position_fig(df_filtered, selected_year),
        gender_fig(df_filtered, selected_year),
        retention_fig(df_filtered, [selected_year])
    )

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
