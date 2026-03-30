import pandas as pd

df = pd.read_csv('TC_POD-TShirt-Platform_v6_2026-03-16_Full.csv')
zoom_df = df[(df['Title'].str.contains('Zoom', na=False, case=False)) | (df['Title'].str.contains('Pan', na=False, case=False))]
with open('tmp_zoom_check.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total Zoom/Pan Cases: {len(zoom_df)}\n")
    for _, row in zoom_df.iterrows():
        f.write(f"{row['TC_ID']} | {row['Feature']} | {row['Module']} | {row['Title']} | {row['Type']}\n")
