import openpyxl
f = r'E:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\TC_POD-TShirt-Platform_ExecutionSummary_v22_2026-03-19.xlsx'
wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
for sn in ['HOME PAGE', 'DESIGN STUDIO']:
    ws = wb[sn]
    print(f'\n{"="*100}')
    print(f'SHEET: {sn}')
    print(f'{"="*100}')
    for i, row in enumerate(ws.iter_rows(max_col=11, values_only=True)):
        if i == 0: 
            print('[Row 1: Round headers]')
            continue
        if i == 1:
            print(f'[Row 2: Column headers] {[str(x)[:20] for x in row[:7]]}')
            continue
        tc_id = str(row[0] or '')
        if tc_id.startswith('\U0001f4cc'):
            print(f'\n  {tc_id}')
            continue
        if not tc_id.strip():
            continue
        us = str(row[1] or '')[:10]
        module = str(row[3] or '')[:20]
        title = str(row[4] or '')[:50]
        tc_type = str(row[5] or '')[:10]
        priority = str(row[6] or '')[:5]
        print(f'  {tc_id:<18} {us:<10} {module:<22} {priority:<5} {tc_type:<10} {title}')
wb.close()
