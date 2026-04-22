import pandas as pd
 
file_path = "Extraction_File.xlsx"
 
# Read all sheets into a dictionary
all_sheets = pd.read_excel(file_path, sheet_name=None)
 
# Store and print each sheet
data = {}
for sheet_name, df in all_sheets.items():
    data[sheet_name] = df
    print(f"\n{'='*60}")
    print(f"Sheet: {sheet_name}  |  Rows: {df.shape[0]}  |  Columns: {df.shape[1]}")
    print('='*60)
    print(df.to_string(index=True))
 
print(f"\nTotal sheets loaded: {len(data)}")