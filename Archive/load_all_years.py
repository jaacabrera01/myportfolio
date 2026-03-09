import pandas as pd
import openpyxl

TALENT_FILE = "1 Talent Management (2019-2025).xlsx"
HR_MAIN_FILE = "HR_Main_DO_NOT_EDIT.xlsx"

print("=" * 80)
print("LOADING TALENT MANAGEMENT DATA - ALL YEARS (2019-2025)")
print("=" * 80)

# Load the Excel file
xls = pd.ExcelFile(TALENT_FILE)
sheets = xls.sheet_names
print(f"\n📋 Sheets found in {TALENT_FILE}:")
for sheet in sheets:
    print(f"  - {sheet}")

# Load all sheets
all_data = {}
employees_by_year = {}

print(f"\n📊 Loading data...")
for sheet in sheets:
    try:
        df = pd.read_excel(TALENT_FILE, sheet_name=sheet)
        all_data[sheet] = df
        
        # Get unique employee names
        if 'Full Name' in df.columns:
            employees = set(df['Full Name'].unique())
        else:
            # Try alternative column names
            name_cols = [col for col in df.columns if 'name' in col.lower()]
            if name_cols:
                employees = set(df[name_cols[0]].unique())
            else:
                employees = set()
        
        employees_by_year[sheet] = employees
        print(f"✓ {sheet}: {len(df)} rows, {len(employees)} unique employees")
        print(f"  Columns: {list(df.columns)[:5]}...")
    except Exception as e:
        print(f"✗ {sheet}: Error - {e}")

print(f"\n" + "=" * 80)
print("EMPLOYEE MOVEMENT ANALYSIS - TRACKING RESIGNATIONS")
print("=" * 80)

# Get all years in order
years = sorted([s for s in sheets if s.isdigit()])
print(f"\n📅 Years in order: {years}")

# Track resignations year by year
all_resignations = {}
all_new_hires = {}
total_resigned = set()
total_hired = set()

for i in range(len(years) - 1):
    current_year = years[i]
    next_year = years[i + 1]
    
    current_employees = employees_by_year.get(current_year, set())
    next_employees = employees_by_year.get(next_year, set())
    
    # Employees who were there but disappeared (RESIGNED)
    resigned_this_period = current_employees - next_employees
    all_resignations[f"{current_year}-{next_year}"] = resigned_this_period
    total_resigned.update(resigned_this_period)
    
    # Employees who are new (JOINED)
    new_hires_this_period = next_employees - current_employees
    all_new_hires[f"{current_year}-{next_year}"] = new_hires_this_period
    total_hired.update(new_hires_this_period)
    
    print(f"\n{current_year} → {next_year}:")
    print(f"  Employees in {current_year}: {len(current_employees)}")
    print(f"  Employees in {next_year}: {len(next_employees)}")
    print(f"  Net change: {len(next_employees) - len(current_employees):+d}")
    
    print(f"  ❌ RESIGNED (in {current_year} but NOT in {next_year}): {len(resigned_this_period)}")
    if len(resigned_this_period) > 0:
        print(f"     Examples:")
        for emp in sorted(list(resigned_this_period))[:5]:
            print(f"       - {emp}")
        if len(resigned_this_period) > 5:
            print(f"       ... and {len(resigned_this_period) - 5} more")
    
    print(f"  ✅ JOINED (NOT in {current_year} but in {next_year}): {len(new_hires_this_period)}")
    if len(new_hires_this_period) > 0:
        print(f"     Examples:")
        for emp in sorted(list(new_hires_this_period))[:5]:
            print(f"       - {emp}")
        if len(new_hires_this_period) > 5:
            print(f"       ... and {len(new_hires_this_period) - 5} more")

# Load existing resigned employees from HR_Main
print(f"\n" + "=" * 80)
print("VERIFICATION AGAINST HR_MAIN_DO_NOT_EDIT.xlsx")
print("=" * 80)

resigned_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Resigned Employees")
existing_resigned = set(resigned_df['Employee'].unique())

joined_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Joined Employees")
existing_joined = set(joined_df['Employee'].unique())

print(f"\n✓ Resigned Employees sheet: {len(existing_resigned)} employees")
print(f"✓ Joined Employees sheet: {len(existing_joined)} employees")

# Compare resignations
tracked_resignations = total_resigned
matched = tracked_resignations & existing_resigned
missing_from_sheet = tracked_resignations - existing_resigned
extra_in_sheet = existing_resigned - tracked_resignations

print(f"\n❌ RESIGNATIONS:")
print(f"  From year-to-year tracking: {len(tracked_resignations)} employees")
print(f"  ✓ Found in Resigned sheet: {len(matched)}")
print(f"  ⚠️  NOT in Resigned sheet: {len(missing_from_sheet)}")
print(f"  ⚠️  In Resigned sheet but not tracked: {len(extra_in_sheet)}")

# Compare new hires
tracked_hires = total_hired
matched_hired = tracked_hires & existing_joined
missing_hired = tracked_hires - existing_joined
extra_hired = existing_joined - tracked_hires

print(f"\n✅ NEW HIRES:")
print(f"  From year-to-year tracking: {len(tracked_hires)} employees")
print(f"  ✓ Found in Joined sheet: {len(matched_hired)}")
print(f"  ⚠️  NOT in Joined sheet: {len(missing_hired)}")
print(f"  ⚠️  In Joined sheet but not tracked: {len(extra_hired)}")

if len(missing_from_sheet) > 0:
    print(f"\n⚠️  EMPLOYEES MISSING FROM RESIGNED SHEET:")
    print(f"  (These disappeared in year-to-year tracking but not recorded as resigned)")
    for emp in sorted(list(missing_from_sheet))[:15]:
        print(f"  - {emp}")
    if len(missing_from_sheet) > 15:
        print(f"  ... and {len(missing_from_sheet) - 15} more")

if len(extra_in_sheet) > 0:
    print(f"\n⚠️  EXTRA EMPLOYEES IN RESIGNED SHEET:")
    print(f"  (May have rejoined or recorded differently)")
    for emp in sorted(list(extra_in_sheet))[:15]:
        print(f"  - {emp}")
    if len(extra_in_sheet) > 15:
        print(f"  ... and {len(extra_in_sheet) - 15} more")

# Year-by-year summary
print(f"\n" + "=" * 80)
print("YEAR-BY-YEAR SNAPSHOT")
print("=" * 80)

for year in years:
    if year in employees_by_year:
        count = len(employees_by_year[year])
        print(f"{year}: {count} employees")

# Final summary
print(f"\n" + "=" * 80)
print("FINAL ANALYSIS - RESIGNATIONS & NEW HIRES")
print("=" * 80)
print(f"✓ Total years analyzed: {len(years)}")
print(f"❌ Total employees who RESIGNED: {len(total_resigned)}")
print(f"✅ Total employees who JOINED: {len(total_hired)}")
print(f"📊 Net growth: {len(employees_by_year.get(years[-1], set())) - len(employees_by_year.get(years[0], set()))} employees")

# Compare with HR_Main data
print(f"\n📋 Comparison with HR_Main_DO_NOT_EDIT.xlsx:")
print(f"  Resignations tracked: {len(total_resigned)}")
print(f"  Resigned Employees sheet: {len(existing_resigned)}")
print(f"  Match: {len(total_resigned & existing_resigned)}/{len(total_resigned)} ✓")

if len(total_hired) > 0:
    print(f"\n  New hires tracked: {len(total_hired)}")
    print(f"  Joined Employees sheet: {len(joined_df)}")
    joined_names = set(joined_df['Employee'].unique())
    joined_match = len(total_hired & joined_names)
    print(f"  Match: {joined_match}/{len(total_hired)}")

if len(missing_from_sheet) == 0 and len(extra_in_sheet) == 0:
    print(f"\n✅ Perfect match! All resignations are properly documented.")
else:
    print(f"\n🔍 Data discrepancies found:")
    if len(missing_from_sheet) > 0:
        print(f"  - {len(missing_from_sheet)} resignations not in Resigned Employees sheet")
    if len(extra_in_sheet) > 0:
        print(f"  - {len(extra_in_sheet)} employees in Resigned sheet not tracked in year-to-year")

print("=" * 80)
