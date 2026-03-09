import pandas as pd
import openpyxl

TALENT_FILE = "1 Talent Management (2019-2025).xlsx"
HR_MAIN_FILE = "HR_Main_DO_NOT_EDIT.xlsx"

print("=" * 80)
print("CLEANING TALENT MANAGEMENT DATA")
print("=" * 80)

# Load data
print(f"\n📋 Loading data...")
talent_df = pd.read_excel(TALENT_FILE)
resigned_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Resigned Employees")
joined_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Joined Employees")

print(f"✓ Talent Management: {len(talent_df)} rows")
print(f"✓ Resigned Employees: {len(resigned_df)} rows")
print(f"✓ Joined Employees: {len(joined_df)} rows")

# Get unique names
resigned_names = set(resigned_df['Employee'].unique())
joined_names = set(joined_df['Employee'].unique())
talent_names = set(talent_df['Full Name'].unique())

print(f"\n🔍 Before cleaning:")
print(f"  Total employees in Talent: {len(talent_names)}")
print(f"  Resigned in Talent: {len(resigned_names.intersection(talent_names))}")
print(f"  Joined in Talent: {len(joined_names.intersection(talent_names))}")

# Remove resigned employees
talent_cleaned = talent_df[~talent_df['Full Name'].isin(resigned_names)].copy()

print(f"\n✓ After removing resigned employees:")
print(f"  Remaining employees: {len(talent_cleaned)} rows")
print(f"  Removed: {len(talent_df) - len(talent_cleaned)} rows")

# Display sample of removed employees
removed_employees = talent_df[talent_df['Full Name'].isin(resigned_names)]
if len(removed_employees) > 0:
    print(f"\nSample of removed employees:")
    for idx, (_, row) in enumerate(removed_employees.head(10).iterrows()):
        print(f"  {row['Full Name']} - {row['Position/Level']}, Age {row['Age']}")

# Save cleaned data
print(f"\n💾 Saving cleaned data to {TALENT_FILE}...")

# Method: Save as new Excel file, then replace
temp_file = "talent_cleaned_temp.xlsx"
talent_cleaned.to_excel(temp_file, index=False, sheet_name='2019')

# Replace original file
import shutil
shutil.move(temp_file, TALENT_FILE)

print(f"✓ File saved successfully!")

# Final verification
talent_check = pd.read_excel(TALENT_FILE)
print(f"\n✅ FINAL VERIFICATION:")
print(f"  Total rows: {len(talent_check)}")
print(f"  Columns: {list(talent_check.columns)}")

# Check if any resigned employees remain
resigned_in_cleaned = talent_check['Full Name'].isin(resigned_names)
if resigned_in_cleaned.sum() > 0:
    print(f"  ⚠️  Warning: {resigned_in_cleaned.sum()} resigned employees still in data")
else:
    print(f"  ✓ No resigned employees in data")

print("\n" + "=" * 80)
print(f"✅ CLEANING COMPLETE")
print("=" * 80)
