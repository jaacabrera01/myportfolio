import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Read source file
hr_main_file = "HR_Main.xlsx"
output_file = "Dashboard_2019_2025.xlsx"

try:
    # Read Headcount data from Resource Growth Tracker
    print("Reading Resource Growth Tracker...")
    df_headcount = pd.read_excel(hr_main_file, sheet_name='Resource Growth Tracker')
    print(f"Columns: {df_headcount.columns.tolist()}")
    
    # Use 'Year' column and rename it to 'Fiscal Year'
    if 'Year' in df_headcount.columns and 'Ending Headcount' in df_headcount.columns:
        headcount_data = df_headcount[['Year', 'Ending Headcount']].copy()
        headcount_data.rename(columns={'Year': 'Fiscal Year'}, inplace=True)
    else:
        print(f"Available columns in Resource Growth Tracker: {df_headcount.columns.tolist()}")
        raise KeyError("Required columns not found in Resource Growth Tracker")
    
    # Read Position-Level data
    print("\nReading Position-Level...")
    df_position = pd.read_excel(hr_main_file, sheet_name='Position-Level')
    print(f"Columns: {df_position.columns.tolist()}")
    
    # Use 'Manager & Up' instead of calculating
    if 'Fiscal Year' in df_position.columns:
        position_data = df_position[['Fiscal Year']].copy()
        position_data['Managers and Up'] = df_position['Manager & Up'] if 'Manager & Up' in df_position.columns else 0
        position_data['Associates'] = df_position['Associate'] if 'Associate' in df_position.columns else 0
    else:
        print(f"Available columns in Position-Level: {df_position.columns.tolist()}")
        raise KeyError("Required columns not found in Position-Level")
    
    # Read Avg Tenure data
    print("\nReading Avg Tenure...")
    df_tenure = pd.read_excel(hr_main_file, sheet_name='Avg Tenure')
    print(f"Columns: {df_tenure.columns.tolist()}")
    
    # Use 'Year' and 'Average Tenure' columns
    if 'Year' in df_tenure.columns and 'Average Tenure' in df_tenure.columns:
        tenure_data = df_tenure[['Year', 'Average Tenure']].copy()
        tenure_data.rename(columns={'Year': 'Fiscal Year', 'Average Tenure': 'Avg Tenure'}, inplace=True)
    else:
        print(f"Available columns in Avg Tenure: {df_tenure.columns.tolist()}")
        raise KeyError("Required columns not found in Avg Tenure")
    
    # Read Avg Retention Rate data
    print("\nReading Avg Retention Rate...")
    df_retention = pd.read_excel(hr_main_file, sheet_name='Avg Retention Rate')
    print(f"Columns: {df_retention.columns.tolist()}")
    
    # Handle different possible column names - use 'Yearly Retention Rate '
    if 'Fiscal Year' in df_retention.columns or 'Year' in df_retention.columns:
        year_col = 'Fiscal Year' if 'Fiscal Year' in df_retention.columns else 'Year'
        
        # Check for actual retention rate column name
        rate_col = None
        for col in df_retention.columns:
            if 'retention' in col.lower() and 'rate' in col.lower():
                rate_col = col
                break
        
        if rate_col is None:
            print(f"Available columns in Avg Retention Rate: {df_retention.columns.tolist()}")
            raise KeyError("Retention rate column not found in Avg Retention Rate")
        
        retention_data = df_retention[[year_col, rate_col]].copy()
        if year_col == 'Year':
            retention_data.rename(columns={'Year': 'Fiscal Year'}, inplace=True)
        retention_data.rename(columns={rate_col: 'Avg Retention Rate'}, inplace=True)
    else:
        print(f"Available columns in Avg Retention Rate: {df_retention.columns.tolist()}")
        raise KeyError("Required columns not found in Avg Retention Rate")
    
    # Merge all data into dashboard
    print("\nMerging data into dashboard...")
    dashboard = headcount_data.merge(position_data, on='Fiscal Year', how='left')
    dashboard = dashboard.merge(tenure_data, on='Fiscal Year', how='left')
    dashboard = dashboard.merge(retention_data, on='Fiscal Year', how='left')
    
    # Create new workbook and write dashboard
    print("\nCreating workbook and writing dashboard...")
    wb = Workbook()
    ws = wb.active
    ws.title = 'Dashboard'
    
    # Write dashboard data to sheet
    for r_idx, row in enumerate(dataframe_to_rows(dashboard, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)
    
    wb.save(output_file)
    print(f"Dashboard created successfully: {output_file}")
    print(f"\nDashboard Summary:\n{dashboard}")
    
except Exception as e:
    print(f"Error creating dashboard: {e}")
    import traceback
    traceback.print_exc()
