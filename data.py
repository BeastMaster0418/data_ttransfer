import pandas as pd
 
file_path_1 = "Extraction File.xlsx"
file_path_2 = "Customer Supplied RM List.xlsx"
file_path_3 = "Raw Materials Template (Hiring).xlsx"
 
def read_excel_file(file_path):
    try:
        # Read all sheets into a dictionaryd
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        
        # Store and print each sheet
        data = {}
        for sheet_name, df in all_sheets.items():
            data[sheet_name] = df
            Products = df.to_dict(orient = "records")

            print(f"\n{'='*60}")
            print(f"Sheet: {sheet_name}  |  Rows: {df.shape[0]}  |  Columns: {df.shape[1]}")
            print('='*60)
            # print(df.to_string(index=True))
            keys = list(df.columns)
            # keys = list(Products[0].keys())
            print(keys)
            
            for i, product in enumerate(Products):
                print(f"Products[{i}] = {product[keys[0]]} | {product[keys[1]]} | {product[keys[2]]} | {product[keys[3]]} | {product[keys[4]]}")
        
        print(f"\nTotal sheets loaded: {len(data)}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


read_excel_file(file_path_1)
read_excel_file(file_path_2)
read_excel_file(file_path_3)

# Save to a new .xlsx file
# with pd.ExcelWriter("Extraction_File_copy.xlsx", engine="openpyxl") as writer:
#     for sheet_name, df in data.items():
#         df.to_excel(writer, sheet_name=sheet_name, index=False)
 
# print("Saved to Extraction_File_copy.xlsx")
 
