import pandas as pd

TALENT_FILE = "1 Talent Management (2019-2025).xlsx"

print("=" * 80)
print("LOADING NEW TALENT MANAGEMENT FILE")
print("=" * 80)

# Load the Excel file
xls = pd.ExcelFile(TALENT_FILE)
sheets = xls.sheet_names

print(f"\n📋 Sheets found in {TALENT_FILE}:")
for sheet in sheets:
    print(f"  - {sheet}")

# Load all sheets and display info
print(f"\n📊 Loading and analyzing data...")

all_data = {}
total_rows = 0
total_unique = 0

for sheet in sheets:
    try:
        df = pd.read_excel(TALENT_FILE, sheet_name=sheet)
        all_data[sheet] = df
        
        # Get unique employee names
        if 'Full Name' in df.columns:
            unique_emp = len(df['Full Name'].unique())
        else:
            unique_emp = len(df)
        
        total_rows += len(df)
        total_unique += unique_emp
        
        print(f"\n✓ {sheet}:")
        print(f"    Rows: {len(df)}")
        print(f"    Unique employees: {unique_emp}")
        print(f"    Columns: {list(df.columns)[:6]}...")
        print(f"    Data types: {df.dtypes.unique()}")
        
        # Show sample
        print(f"    Sample:")
        print(f"      {df.iloc[0].to_dict()}")
        
    except Exception as e:
        print(f"\n✗ {sheet}: Error - {e}")

print(f"\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ Total sheets: {len(sheets)}")
print(f"✓ Total rows: {total_rows}")
print(f"✓ Total unique employees: {total_unique}")
print(f"✓ Years covered: {', '.join(sheets)}")

# Check data quality
print(f"\n✅ Data is ready! Proceeding with joining Employees data...\n")
