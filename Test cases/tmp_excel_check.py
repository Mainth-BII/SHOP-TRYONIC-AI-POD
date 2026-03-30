import pandas as pd
import openpyxl

file_name = 'TC_POD-TShirt-Platform_ExecutionSummary_v18_2026-03-16.xlsx'

print(f"Reading '{file_name}'...")
try:
    df = pd.read_excel(file_name, sheet_name='Editor', skiprows=2)
    # the Editor sheet has rows, header might be row 2 (0-indexed = 2 for pandas? Actually row 2 in Excel is row index 1)
    
    # check first column which should be TC_ID
    # find row which contains 029a anywhere
    zoom_cases = df[df.apply(lambda row: row.astype(str).str.contains('029a', case=False).any(), axis=1)]
    print('Found 029a:', len(zoom_cases))
    
    # let's write out first 10 TC_IDs just to see what got loaded
    print(df.iloc[:10, 0].values)
except Exception as e:
    print('Error:', e)
