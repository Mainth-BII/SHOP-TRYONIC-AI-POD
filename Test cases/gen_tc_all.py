import csv, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_tc_part1 import ALL_PART1
from gen_tc_part2 import ALL_PART2
from gen_tc_part3 import ALL_PART3

ALL = ALL_PART1 + ALL_PART2 + ALL_PART3
HEADERS = ["TC_ID","US_Mapping","Feature","Module","Title","Type","Priority","Precondition","Test_Data","Steps","Expected_Result"]

out_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(out_dir, "TC_POD-TShirt-Platform_v4_2026-03-13.csv")

with io.open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(HEADERS)
    w.writerows(ALL)

# Stats
total = len(ALL)
p0 = sum(1 for t in ALL if t[6] == "P0")
p1 = sum(1 for t in ALL if t[6] == "P1")
p2 = sum(1 for t in ALL if t[6] == "P2")
pos = sum(1 for t in ALL if t[5] == "Positive")
neg = sum(1 for t in ALL if t[5] == "Negative")
bnd = sum(1 for t in ALL if t[5] == "Boundary")
edge = sum(1 for t in ALL if t[5] == "Edge Case")
uiux = sum(1 for t in ALL if t[5] == "UI/UX")

print(f"✅ CSV generated: {csv_file}")
print(f"📋 Total: {total} test cases")
print(f"   P0: {p0} | P1: {p1} | P2: {p2}")
print(f"   Positive: {pos} | Negative: {neg} | Boundary: {bnd} | Edge: {edge} | UI/UX: {uiux}")
print(f"\n📊 Breakdown by Epic:")
for name, data in [("Auth", ALL_PART1[:46]), ("Templates", ALL_PART1[46:58]), ("Products", ALL_PART1[58:]),
                     ("Editor", ALL_PART2[:25]), ("Checkout", ALL_PART2[25:43]), ("Orders", ALL_PART2[43:]),
                     ("Admin", ALL_PART3[:23]), ("AI", ALL_PART3[23:35]), ("Credits", ALL_PART3[35:])]:
    print(f"   {name}: {len(data)} TCs")
