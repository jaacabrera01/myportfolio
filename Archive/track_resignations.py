import pandas as pd
import openpyxl

TALENT_FILE = "1 Talent Management (2019-2025).xlsx"
HR_MAIN_FILE = "HR_Main_DO_NOT_EDIT.xlsx"

print("=" * 80)
print("TRACKING EMPLOYEES ACROSS ALL YEARS (2019-2025)")
print("=" * 80)

# Load the Excel file
xls = pd.ExcelFile(TALENT_FILE)
sheets = xls.sheet_names
print(f"\n📋 Sheets found: {sheets}")

# Load all sheets
all_data = {}
for sheet in sheets:
    df = pd.read_excel(TALENT_FILE, sheet_name=sheet)
    all_data[sheet] = df
    print(f"✓ {sheet}: {len(df)} employees")

# Convert sheet names to years
years = sorted([int(s) for s in sheets if s.isdigit()])
print(f"\n📅 Years available: {years}")

# Get employee names for each year
employees_by_year = {}
for sheet in sheets:
    if sheet in all_data:
        # Get unique employee names
        if 'Full Name' in all_data[sheet].columns:
            employees = set(all_data[sheet]['Full Name'].unique())
        else:
            # Try alternative column names
            name_cols = [col for col in all_data[sheet].columns if 'name' in col.lower()]
            if name_cols:
                employees = set(all_data[sheet][name_cols[0]].unique())
            else:
                employees = set()
        employees_by_year[sheet] = employees
        print(f"  {sheet}: {len(employees)} unique employees")

print(f"\n" + "=" * 80)
print("EMPLOYEE MOVEMENT ANALYSIS")
print("=" * 80)

# Track who resigned (disappeared in subsequent years)
resignations = {}

for i in range(len(sheets) - 1):
    current_year = sheets[i]
    next_year = sheets[i + 1]
    
    current_employees = employees_by_year.get(current_year, set())
    next_employees = employees_by_year.get(next_year, set())
    
    # Employees who were there but are gone (resigned)
    resigned = current_employees - next_employees
    resignations[f"{current_year}->{next_year}"] = resigned
    
    print(f"\n{current_year} → {next_year}:")
    print(f"  Current year employees: {len(current_employees)}")
    print(f"  Next year employees: {len(next_employees)}")
    print(f"  ⚠️  RESIGNED (in {current_year} but not in {next_year}): {len(resigned)}")
    
    if len(resigned) > 0:
        print(f"     Sample resignations:")
        for emp in sorted(list(resigned))[:10]:
            print(f"       - {emp}")

# Load existing resigned employees
resigned_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Resigned Employees")
existing_resigned = set(resigned_df['Employee'].unique())

print(f"\n" + "=" * 80)
print("VERIFICATION AGAINST RESIGNED EMPLOYEES SHEET")
print("=" * 80)
print(f"✓ Resigned Employees sheet has: {len(existing_resigned)} employees")

# Check if all tracked resignations are in the Resigned Employees sheet
all_tracked_resignations = set()
for period, resigned_set in resignations.items():
    all_tracked_resignations.update(resigned_set)

missing_from_resigned_sheet = all_tracked_resignations - existing_resigned
found_in_resigned_sheet = all_tracked_resignations & existing_resigned

print(f"\nFrom year-to-year tracking:")
print(f"  Total who resigned (not in next year): {len(all_tracked_resignations)}")
print(f"  ✓ Found in Resigned Employees sheet: {len(found_in_resigned_sheet)}")
print(f"  ⚠️  NOT in Resigned Employees sheet: {len(missing_from_resigned_sheet)}")

if len(missing_from_resigned_sheet) > 0:
    print(f"\n⚠️  EMPLOYEES MISSING FROM RESIGNED SHEET (should be added):")
    for emp in sorted(list(missing_from_resigned_sheet))[:20]:
        print(f"  - {emp}")
    if len(missing_from_resigned_sheet) > 20:
        print(f"  ... and {len(missing_from_resigned_sheet) - 20} more")

# Summary
print(f"\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ Analyzed {len(sheets)} years of data")
print(f"✓ Total employees tracked: {sum(len(e) for e in employees_by_year.values())}")
print(f"✓ Employees who resigned (disappeared in later years): {len(all_tracked_resignations)}")
print(f"✓ Data quality: {len(found_in_resigned_sheet)}/{len(all_tracked_resignations)} resignations accounted for")

if len(missing_from_resigned_sheet) > 0:
    print(f"\n🔧 RECOMMENDATION: Add {len(missing_from_resigned_sheet)} missing employees to Resigned Employees sheet")
else:
    print(f"\n✅ All tracked resignations are properly documented!")

print("=" * 80)
