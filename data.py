import pandas as pd
 
file_path_1 = "Extraction File.xlsx"
file_path_2 = "Customer Supplied RM List.xlsx"
file_path_3 = "Raw Materials Template (Hiring).xlsx"
 
# Read all sheets into a dictionary
all_sheets = pd.read_excel(file_path_1, sheet_name=None)
 
# Store and print each sheet
data = {}
for sheet_name, df in all_sheets.items():
    data[sheet_name] = df
    Products = df.to_dict(orient = "records")

    print(f"\n{'='*60}")
    print(f"Sheet: {sheet_name}  |  Rows: {df.shape[0]}  |  Columns: {df.shape[1]}")
    print('='*60)
    # print(df.to_string(index=True))
    for i, product in enumerate(Products):
        print(f"Products[{i}] = {product}")
 
print(f"\nTotal sheets loaded: {len(data)}")



# Save to a new .xlsx file
# with pd.ExcelWriter("Extraction_File_copy.xlsx", engine="openpyxl") as writer:
#     for sheet_name, df in data.items():
#         df.to_excel(writer, sheet_name=sheet_name, index=False)
 
# print("Saved to Extraction_File_copy.xlsx")
 

