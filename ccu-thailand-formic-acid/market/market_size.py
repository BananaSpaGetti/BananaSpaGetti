"""Thai formic acid imports (HS 29151100) -> rough market size and CO2 need.

Input: imports_hs29151100_jan.csv, CIF value in THB for January only (as supplied
by the team from customs statistics). No quantity column yet, so tonnes are
estimated from an ASSUMED CIF price range. Replace with real kg data when available.
Run: python3 market_size.py
"""
import csv
from collections import defaultdict

CIF_THB_PER_T = (17000, 20000, 25000)  # assumed low / mid / high landed price, 85 % grade
OUR_COST_THB_PER_T_100 = 17500         # cost_model.py, green H2, 100 % HCOOH basis
CO2_T_PER_T_FA = 44.01 / 46.03

rows = list(csv.DictReader(open("imports_hs29151100_jan.csv")))
total, china = defaultdict(float), defaultdict(float)
for r in rows:
    total[r["year"]] += float(r["cif_thb"])
    if r["country"] == "CN":
        china[r["year"]] += float(r["cif_thb"])

print("January CIF (million THB), China share")
for y in sorted(total):
    print(f"  {y}  {total[y]/1e6:6.2f}   CN {china[y]/total[y]:5.1%}")
avg = sum(total.values()) / len(total)
print(f"  avg   {avg/1e6:6.2f}  -> x12 = {avg*12/1e6:.0f} million THB/yr (if January is a typical month)")

print("\nEstimated volume from assumed CIF price (avg January x 12):")
for p in CIF_THB_PER_T:
    t_yr = avg * 12 / p
    print(f"  {p:>6,} THB/t -> {t_yr/12:6,.0f} t/month, {t_yr:7,.0f} t/yr, "
          f"CO2 needed {t_yr*CO2_T_PER_T_FA*0.85:7,.0f} t/yr (85 % grade)")

ours_85 = OUR_COST_THB_PER_T_100 * 0.85
print(f"\nOur cost at 85 % grade ~ {ours_85:,.0f} THB/t (HCOOH content only, excludes extra water handling)")
for p in CIF_THB_PER_T:
    print(f"  vs import {p:>6,} THB/t: margin {p-ours_85:+7,.0f} THB/t")
