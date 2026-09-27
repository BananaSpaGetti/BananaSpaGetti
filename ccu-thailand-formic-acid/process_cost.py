"""Cost of CO2-based formic acid at Bang Pakong, built ONLY from sourced numbers (params.py / SOURCES.md).

Method:
  1. Conversion cost (CO2 + H2 -> HCOOH, purification) = the published plant of
     Tzitzili et al. 2025 (Table 5, Case A: 1.18 USD/kg at 13,030 t/yr, CO2 bought already captured).
  2. Scale to our size: variable costs (raw materials, utilities, other) stay per kg;
     facility-related cost follows the six-tenths rule; labour is kept as the same crew (fixed per year).
  3. Add CO2 capture at the NGCC stack = NETL Baseline Rev 4a cost per t CO2 captured
     x CO2 used per kg in the Tzitzili plant.
  4. Convert to 85 % product (x 0.85: less purification than the 99.78 % acid in the study,
     so this is on the high side) and to THB with the Bank of Thailand rate.
Anything without a public source (Thai chemical prices, steam price, trucking, CIF per kg) is
not used here; see SOURCES.md. The old assumption-based model: python3 process_cost.py --assumed
Run: python3 process_cost.py
"""
import sys

from params import P, v, tag


def benchmark(target_t=None, capture_usd_t=None):
    target_kg = (target_t or v("TARGET_T_YR")) * 1000 * v("GRADE")      # kg HCOOH (100 %)
    s = target_kg / v("FA_PLANT_KG_YR")                                  # size ratio vs study plant
    split = v("FA_OPEX_SPLIT")
    other = 1 - sum(split.values())
    base = v("FA_UNIT_COST_USD_KG")
    per_kg = {                                                           # USD per kg HCOOH
        "raw materials (H2, CO2 price in study, amine, catalyst)": base * split["raw_materials"],
        "utilities (power, steam, chilled water)": base * split["utilities"],
        "other operating": base * other,
        "facility-related (scaled 0.6 rule)": base * split["facility"] * s ** (v("SCALE_EXP") - 1),
        "labour (same crew)": base * split["labour"] / s,
    }
    co2_per_kg = v("FA_CO2_KG_YR") / v("FA_PLANT_KG_YR")
    per_kg["CO2 capture at NGCC stack"] = co2_per_kg * (capture_usd_t or v("CAPTURE_USD_T")) / 1000
    return per_kg, s, co2_per_kg


def main():
    if "--assumed" in sys.argv:
        import process_cost_assumed
        process_cost_assumed.main(process_cost_assumed.STACK_AMINE)
        return

    fx, grade = v("USD_THB"), v("GRADE")
    per_kg, s, co2_per_kg = benchmark()
    total = sum(per_kg.values())

    print("Inputs:")
    for k in ("FA_UNIT_COST_USD_KG", "FA_PLANT_KG_YR", "FA_OPEX_SPLIT", "FA_CO2_KG_YR",
              "CAPTURE_USD_T", "TARGET_T_YR", "GRADE", "SCALE_EXP", "USD_THB"):
        print(f"  {k:20s} {str(v(k))[:60]:60s} {P[k]['unit'][:34]:34s} {tag(k)}")

    print(f"\nOur plant: {v('TARGET_T_YR'):,} t/yr of {grade:.0%} acid = {s:.3f} x the study plant; "
          f"CO2 {co2_per_kg:.3f} kg per kg HCOOH")
    print(f"{'':58s}{'USD/kg HCOOH':>14s}{'THB/kg 85 %':>14s}")
    for k, x in per_kg.items():
        print(f"  {k:56s}{x:14.3f}{x * grade * fx:14.2f}")
    print(f"  {'TOTAL':56s}{total:14.3f}{total * grade * fx:14.2f}")
    print("  note: if the study's raw materials already include a CO2 purchase price (its Table S16),")
    print("        the capture line partly double-counts, so the total is on the high side.")

    lo = sum(benchmark(capture_usd_t=v("CAPTURE_USD_T"))[0].values())
    hi = sum(benchmark(capture_usd_t=v("CAPTURE_USD_T_REV4"))[0].values())
    print(f"  capture 61-80 USD/t (NETL Rev 4a / Rev 4): {lo*grade*fx:.2f}-{hi*grade*fx:.2f} THB/kg 85 %")
    at_study = v("FA_UNIT_COST_USD_KG") + co2_per_kg * v("CAPTURE_USD_T") / 1000
    print(f"  at the study's own size (13,030 t/yr): {at_study*grade*fx:.2f} THB/kg 85 %")

    print("\nCompare (per kg of 85 % acid):")
    print(f"  study's selling price 1.40 USD/kg     {v('FA_PRICE_USD_KG')*grade*fx:6.2f} THB  {tag('FA_PRICE_USD_KG')}")
    print(f"  study's minimum selling price 1.36    {v('FA_MSP_USD_KG')*grade*fx:6.2f} THB  {tag('FA_MSP_USD_KG')}")
    c = v("FARM_CASE_THB")
    print(f"  farmer buys by the case (6 x 5 kg)    {c[0]/30:6.2f}-{c[1]/30:.2f} THB  {tag('FARM_CASE_THB')}")
    print("  import CIF per kg                     unknown: needs import quantity in kg (SOURCES.md)")

    h2_kg = v("M_H2") / v("M_HCOOH")
    pem_thb = h2_kg * v("PEM_KWH_KG") * v("ELEC_THB_KWH")
    print(f"\nFor reference: making our own H2 by PEM at the average Thai tariff costs "
          f"{h2_kg:.4f} kg x {v('PEM_KWH_KG')} kWh x {v('ELEC_THB_KWH')} THB = {pem_thb:.2f} THB per kg HCOOH "
          f"{tag('PEM_KWH_KG')} {tag('ELEC_THB_KWH')}")
    print("  (the study buys H2; its H2 price is in Supplementary Table S16, not in the PDF)")


if __name__ == "__main__":
    main()
