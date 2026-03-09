import pandas as pd

print("=" * 80)
print("SITUATION REPORT")
print("=" * 80)

# The cleaning script accidentally replaced the entire file with only 2019 data
# We need to restore the multi-year structure

print("\n⚠️  ISSUE FOUND:")
print("  The 1 Talent Management (2019-2025).xlsx file now only contains 2019 data")
print("  Other year sheets (2020-2025) were lost during the cleaning process")

print("\n📋 To properly track resignations across all years, we need:")
print("  1. The original file with sheets for 2019, 2020, 2021, 2022, 2023, 2024, 2025")
print("  2. Each sheet should contain that year's active employees")

print("\n💡 CURRENT STATUS:")
HR_MAIN = pd.read_excel("HR_Main_DO_NOT_EDIT.xlsx", sheet_name="Resigned Employees")
print(f"  ✓ Resigned Employees sheet: {len(HR_MAIN)} employees")
print(f"    These employees resigned between 2019-2025")

TALENT = pd.read_excel("1 Talent Management (2019-2025).xlsx")
print(f"  ✓ Talent Management file: {len(TALENT)} employees (2019 only)")
print(f"    These are active employees at end of 2019")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("""
Option 1: RESTORE FROM BACKUP
  - Check if you have a backup of the original file
  - Restore it to recover the 2020-2025 sheets

Option 2: USE EXISTING DATA
  - Use the Resigned Employees sheet to identify when each person left
  - Cross-reference with Joined Employees to track movements
  - Build year-by-year snapshots from this data

Option 3: RECREATE FROM HR SHEETS
  - Extract Resignation Dates to determine departure year
  - Extract Joining Dates to determine hiring year
  - Rebuild multi-year employee roster
""")

# Let's use Option 3 - analyze what we can from HR_Main
print("\n" + "=" * 80)
print("ANALYSIS FROM EXISTING DATA")
print("=" * 80)

resigned_df = pd.read_excel("HR_Main_DO_NOT_EDIT.xlsx", sheet_name="Resigned Employees")
joined_df = pd.read_excel("HR_Main_DO_NOT_EDIT.xlsx", sheet_name="Joined Employees")

print(f"\n📊 From HR_Main_DO_NOT_EDIT.xlsx:")
print(f"  Resigned Employees: {len(resigned_df)}")
if 'Resigned Year' in resigned_df.columns:
    resign_years = resigned_df['Resigned Year'].value_counts().sort_index()
    print(f"  Resignations by year:")
    for year, count in resign_years.items():
        print(f"    {year}: {count} employees")

print(f"\n  Joined Employees: {len(joined_df)}")
if 'Year Joined' in joined_df.columns:
    join_years = joined_df['Year Joined'].value_counts().sort_index()
    print(f"  Joins by year:")
    for year, count in join_years.items():
        print(f"    {year}: {count} employees")

print("\n" + "=" * 80)
