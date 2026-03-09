import pandas as pd

HR_MAIN_FILE = "HR_Main_DO_NOT_EDIT.xlsx"
OUTPUT_FILE = "Resigned_Employees_Report.xlsx"

print("=" * 80)
print("CREATING RESIGNED EMPLOYEES REPORT")
print("=" * 80)

# Load resigned employees
print(f"\n📋 Loading Resigned Employees sheet...")
resigned_df = pd.read_excel(HR_MAIN_FILE, sheet_name="Resigned Employees")

print(f"✓ Loaded: {len(resigned_df)} employees")
print(f"  Available columns: {list(resigned_df.columns)}")

# Select required columns
required_columns = ['Employee', 'Year Joined', 'Resigned Between', 'Tenure', 'Age', 'Generation', 'Position/Level']

# Check which columns exist
existing_columns = [col for col in required_columns if col in resigned_df.columns]
missing_columns = [col for col in required_columns if col not in resigned_df.columns]

print(f"\n✓ Found columns: {existing_columns}")
if missing_columns:
    print(f"⚠️  Missing columns: {missing_columns}")

# Create report dataframe with available columns
report_df = resigned_df[existing_columns].copy()

print(f"\n📊 Report details:")
print(f"  Total employees: {len(report_df)}")
print(f"  Columns: {len(existing_columns)}")

# Display sample
print(f"\n📈 Sample data:")
print(report_df.head(10).to_string())

# Save to Excel
print(f"\n💾 Saving to {OUTPUT_FILE}...")
report_df.to_excel(OUTPUT_FILE, index=False, sheet_name="Resigned Employees")

print(f"✓ File saved successfully!")
print(f"\n" + "=" * 80)
print("FILE DETAILS")
print("=" * 80)
print(f"Filename: {OUTPUT_FILE}")
print(f"Sheet name: Resigned Employees")
print(f"Total rows: {len(report_df)}")
print(f"Columns: {len(existing_columns)}")
print(f"\nColumn summary:")
for col in existing_columns:
    print(f"  • {col}: {report_df[col].dtype}")

# Statistics
print(f"\n📊 STATISTICS:")
print(f"\nYear Joined:")
print(report_df['Year Joined'].value_counts().sort_index().to_string())

print(f"\nResigned Between:")
print(report_df['Resigned Between'].value_counts().to_string())

print(f"\nPosition/Level:")
print(report_df['Position/Level'].value_counts().to_string())

print(f"\nGeneration:")
print(report_df['Generation'].value_counts().to_string())

print(f"\nAge statistics:")
print(f"  Average: {report_df['Age'].mean():.1f}")
print(f"  Min: {report_df['Age'].min()}")
print(f"  Max: {report_df['Age'].max()}")

print(f"\nTenure statistics:")
print(f"  Average: {report_df['Tenure'].mean():.2f} years")
print(f"  Min: {report_df['Tenure'].min():.1f}")
print(f"  Max: {report_df['Tenure'].max():.1f}")

print("\n" + "=" * 80)
print("✅ REPORT COMPLETE")
print("=" * 80)
