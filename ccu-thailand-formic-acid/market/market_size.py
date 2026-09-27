"""Thai formic acid imports (HS 29151100) and prices, sourced numbers only.

Input: imports_hs29151100_jan.csv, CIF value in THB for January only (team screenshots of
customs statistics, SOURCES.md S14). No quantity (kg) yet, so import tonnes and CIF per kg
are NOT estimated here; add the kg column to get them.
Run: python3 market_size.py   (from the market/ folder)
"""
import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from params import v, tag                      # noqa: E402
from process_cost import benchmark             # noqa: E402

rows = list(csv.DictReader(open(os.path.join(HERE, "imports_hs29151100_jan.csv"))))
total, china = defaultdict(float), defaultdict(float)
for r in rows:
    total[r["year"]] += float(r["cif_thb"])
    if r["country"] == "CN":
        china[r["year"]] += float(r["cif_thb"])

print(f"Imports, January only, CIF million THB and China share  {tag('THAI_IMPORT_JAN_THB')}")
for y in sorted(total):
    print(f"  {y}  {total[y]/1e6:6.2f}   CN {china[y]/total[y]:5.1%}")
print("  Annual value and tonnes need Jan-Dec data with quantity (kg); not estimated.")

case, gallon = v("FARM_CASE_THB"), v("FARM_GALLON_THB")
print(f"\nFarmer price, THB/kg of product  {tag('FARM_CASE_THB')}")
print(f"  case of 6 x 5 kg   {case[0]/30:5.1f} - {case[1]/30:5.1f}")
print(f"  single 5 kg gallon {gallon[0]/5:5.1f} - {gallon[1]/5:5.1f}")

grade, fx = v("GRADE"), v("USD_THB")
ours = sum(benchmark()[0].values()) * grade * fx
print(f"\nOur cost (process_cost.py, sourced benchmark): {ours:.2f} THB/kg of {grade:.0%} acid"
      f" = {ours*5:.0f} THB per 5 kg")
print(f"  farmer pays per 5 kg: {case[0]/6:.0f}-{case[1]/6:.0f} THB by the case, "
      f"{gallon[0]}-{gallon[1]} THB single gallon")
