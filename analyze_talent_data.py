import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

TALENT_FILE = "1 Talent Management (2019-2025).xlsx"
HR_MAIN_FILE = "HR_Main_DO_NOT_EDIT.xlsx"

print("=" * 80)
print("TALENT MANAGEMENT DATA ANALYSIS & CLEANING")
print("=" * 80)

# Load the Excel file to see all sheets
print(f"\n📋 Loading {TALENT_FILE}...")
xls = pd.ExcelFile(TALENT_FILE)
all_sheets = xls.sheet_names
print(f"✓ Found {len(all_sheets)} sheets: {all_sheets}")

# Load main talent data
talent_df = pd.read_excel(TALENT_FILE, sheet_name=0)
print(f"\n📊 Main Sheet (Sheet 1):")
print(f"  Rows: {len(talent_df)}")
print(f"  Columns: {list(talent_df.columns)}")
print(f"  Data types:\n{talent_df.dtypes}")

# Check for resigned and joined employees
print(f"\n📋 CHECKING EMPLOYEE STATUS...")

# Load resigned employees from HR_Main
resigned_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Resigned Employees")
resigned_names = set(resigned_df['Employee'].unique())
print(f"✓ Found {len(resigned_names)} resigned employees")

# Load joined employees from HR_Main
joined_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Joined Employees")
joined_names = set(joined_df['Employee'].unique())
print(f"✓ Found {len(joined_names)} joined employees")

# Check talent data
talent_names = set(talent_df['Full Name'].unique())
print(f"✓ Found {len(talent_names)} unique employees in Talent Management")

# Check for employees in talent data who have resigned
resigned_in_talent = resigned_names.intersection(talent_names)
print(f"\n⚠️  Resigned employees still in Talent data: {len(resigned_in_talent)}")
if resigned_in_talent:
    print("  Sample:", list(resigned_in_talent)[:5])

# Check for joined employees in talent data
joined_in_talent = joined_names.intersection(talent_names)
print(f"✓ Joined employees in Talent data: {len(joined_in_talent)}")

# Data quality checks
print(f"\n🔍 DATA QUALITY CHECKS:")

# Check for nulls
print(f"\nNull values in Talent Management:")
null_counts = talent_df.isnull().sum()
null_cols = null_counts[null_counts > 0]
if len(null_cols) > 0:
    for col, count in null_cols.items():
        pct = (count / len(talent_df)) * 100
        print(f"  {col}: {count} ({pct:.1f}%)")
else:
    print("  None found ✓")

# Check for duplicates
print(f"\nDuplicate employees per Fiscal Year:")
duplicates = talent_df.groupby(['Fiscal Year', 'Full Name']).size()
duplicates = duplicates[duplicates > 1]
if len(duplicates) > 0:
    print(f"  Found {len(duplicates)} duplicate records")
    print("  Sample:")
    for (year, name), count in duplicates.head().items():
        print(f"    {name} (FY{year}): {count} records")
else:
    print("  None found ✓")

# Check data consistency
print(f"\nData consistency checks:")
print(f"  Fiscal Year range: {talent_df['Fiscal Year'].min()} - {talent_df['Fiscal Year'].max()}")
print(f"  Position/Level values: {sorted(talent_df['Position/Level'].unique())}")
print(f"  Generation values: {sorted(talent_df['Generation'].unique())}")
print(f"  Age range: {talent_df['Age'].min()} - {talent_df['Age'].max()}")
print(f"  Tenure range: {talent_df['Tenured Years'].min()} - {talent_df['Tenured Years'].max()}")

# Check for unusual values
print(f"\n⚠️  UNUSUAL VALUES:")
negative_age = talent_df[talent_df['Age'] < 0]
if len(negative_age) > 0:
    print(f"  Negative ages: {len(negative_age)} records")
else:
    print(f"  Negative ages: None ✓")

negative_tenure = talent_df[talent_df['Tenured Years'] < 0]
if len(negative_tenure) > 0:
    print(f"  Negative tenure: {len(negative_tenure)} records")
else:
    print(f"  Negative tenure: None ✓")

extreme_age = talent_df[talent_df['Age'] > 70]
if len(extreme_age) > 0:
    print(f"  Age > 70: {len(extreme_age)} records")
    print(f"    Max age: {extreme_age['Age'].max()}")

# Summary statistics
print(f"\n📈 SUMMARY STATISTICS:")
print(f"  Total records: {len(talent_df)}")
print(f"  Fiscal Years: {len(talent_df['Fiscal Year'].unique())}")
print(f"  Unique employees: {len(talent_names)}")
print(f"  Average age: {talent_df['Age'].mean():.1f}")
print(f"  Average tenure: {talent_df['Tenured Years'].mean():.2f} years")

# Position distribution
print(f"\nPosition distribution:")
pos_dist = talent_df['Position/Level'].value_counts()
for pos, count in pos_dist.items():
    pct = (count / len(talent_df)) * 100
    print(f"  {pos}: {count} ({pct:.1f}%)")

# Generation distribution
print(f"\nGeneration distribution:")
gen_dist = talent_df['Generation'].value_counts()
for gen, count in gen_dist.items():
    pct = (count / len(talent_df)) * 100
    print(f"  {gen}: {count} ({pct:.1f}%)")

print(f"\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
if len(resigned_in_talent) > 0:
    print(f"⚠️  CLEAN: Remove {len(resigned_in_talent)} resigned employees from Talent Management")
if len(null_cols) > 0:
    print(f"⚠️  CLEAN: Handle {len(null_cols)} columns with null values")
if len(negative_age) > 0 or len(negative_tenure) > 0:
    print(f"⚠️  VERIFY: Check records with negative values")
print(f"✓ Overall data quality appears good")
print("=" * 80)
