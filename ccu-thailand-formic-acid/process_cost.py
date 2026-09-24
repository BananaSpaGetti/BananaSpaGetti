"""Cost per tonne of 85 % formic acid for the team's process at Bang Pakong:
flue gas -> LNG cold box (dry ice) -> Ru + NH3 autoclave -> ammonium formate
-> + H2SO4 -> HCOOH (distil to 85 %) + ammonium sulfate fertilizer.

Method (levelized cost):
  cost/t = [ variable costs (materials + energy)
           + fixed costs (labour, maintenance, catalyst)
           + capital recovery (CAPEX x CRF)
           - by-product revenue (ammonium sulfate) ] / tonnes produced per year
  CRF = r(1+r)^n / ((1+r)^n - 1)   spreads CAPEX over the plant life like a loan payment.

Every price below is an ASSUMPTION (THB, 2026) - replace with quotes from suppliers.
Run: python3 process_cost.py
"""

M = dict(HCOOH=46.03, CO2=44.01, H2=2.016, NH3=17.031, H2SO4=98.079, AS=132.14)

A = dict(
    output_t_yr=10000,          # 85 % formic acid, ~ Thai imports (market/market_size.py)
    grade=0.85,
    yield_overall=0.90,         # CO2/H2/NH3 that ends up as product (losses in capture, reaction, distillation)
    elec_thb_kwh=4.2,           # industrial grid tariff; solar PPA ~2.5-3
    pem_kwh_per_kg_h2=55,
    h2_compress_kwh_per_kg=3,   # PEM outlet ~30 bar -> reactor pressure
    capture_kwh_per_t_co2=150,  # blowers, drying, pumps (cold itself comes from LNG)
    lng_cold_thb_per_t_co2=0,   # LNG cold is waste energy at a regas terminal; >0 if it must be bought/transported
    nh3_thb_kg=18,
    h2so4_thb_kg=5,
    as_thb_kg=8,                # ammonium sulfate (21-0-0) sold ex-works, below retail bag price
    steam_gj_per_t=10,          # distillation to 85 %
    steam_thb_gj=270,
    water_thb_m3=30,            # RO + DI treated cooling water, 10 L per kg H2
    as_evap_gj_per_t_as=2.0,    # evaporate/crystallise ammonium sulfate solution (double-effect)
    route="nh3",                # "nh3": NH3 base + H2SO4 -> ammonium sulfate by-product
                                # "amine": recyclable tertiary amine, adduct split by heat, no by-product
    amine_kg_per_t=5,           # amine make-up (losses) per t product, amine route
    amine_thb_kg=80,
    amine_steam_gj_per_t=15,    # adduct splitting + distillation (replaces steam_gj_per_t)
    amine_capex_factor=1.10,    # extra splitting column
    catalyst_thb_per_t=500,     # Ru catalyst make-up + lab analysis (CoA)
    maint_frac=0.03,            # maintenance, share of CAPEX per year
    insure_frac=0.01,           # insurance, share of CAPEX per year
    labour_thb_yr=7.8e6,        # 15 staff x 40,000 THB x 13 months
    capex_usd=20e6,             # standalone plant at output_ref_t_yr: capture skid, PEM ~2.5 MW, reactor, separation, tanks
    output_ref_t_yr=10000,      # size capex_usd refers to; other sizes scale with the 0.6 rule
    usd_thb=34,
    discount=0.08,
    life_yr=20,
    # sold in bulk to importers (they pack and distribute); stainless/lined tanker, hazmat driver
    truck_load_t=20,
    truck_trip_thb=6000,        # Bang Pakong -> importer warehouse (Bangkok / Samut Prakan area)
    sell_thb_kg=19,             # price offered to importers, below their assumed CIF 17-25
)


def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def capex(a):
    # six-tenths rule: double the size costs ~1.5x, not 2x
    f = a["amine_capex_factor"] if a["route"] == "amine" else 1.0
    return f * a["capex_usd"] * (a["output_t_yr"] / a["output_ref_t_yr"]) ** 0.6


# Unit fitted at the Bang Pakong stack instead of a separate factory: no land or buildings,
# flue gas tapped from the duct at the stack base, LP steam and cooling water from the plant,
# electricity at EGAT's own generation cost, shared operators.
STACK = dict(A, elec_thb_kwh=3.0, steam_thb_gj=100, capex_usd=14e6,
             labour_thb_yr=4.2e6)  # 8 staff; power-plant operators cover shifts
# Formic acid is the main product, so the recommended case avoids the fertilizer by-product.
STACK_AMINE = dict(STACK, route="amine")
SCENARIOS = {
    "standalone factory, NH3 route": A,
    "at stack, NH3 route, fertilizer sold 8": STACK,
    "at stack, NH3 route, fertilizer not sold": dict(STACK, as_thb_kg=0),
    "at stack, amine route (recommended)": STACK_AMINE,
    "at stack, amine route + solar PPA 2.5": dict(STACK_AMINE, elec_thb_kwh=2.5),
    "at stack, amine route, pilot 1,000 t/yr": dict(STACK_AMINE, output_t_yr=1000),
}


def cost(a):
    fa = a["grade"] / a["yield_overall"]          # t HCOOH-equivalent of feed per t product
    co2 = fa * M["CO2"] / M["HCOOH"]              # t
    h2 = fa * M["H2"] / M["HCOOH"] * 1000         # kg
    nh3 = fa * M["NH3"] / M["HCOOH"]              # t, consumed (leaves as ammonium sulfate)
    h2so4 = fa * M["H2SO4"] / 2 / M["HCOOH"]      # t
    as_t = a["grade"] * M["AS"] / 2 / M["HCOOH"]  # t sold (on product actually made)
    items = {
        "H2 (PEM electricity)": h2 * a["pem_kwh_per_kg_h2"] * a["elec_thb_kwh"],
        "H2 compression": h2 * a["h2_compress_kwh_per_kg"] * a["elec_thb_kwh"],
        "water for PEM": h2 * 0.01 * a["water_thb_m3"],
        "CO2 capture (LNG cold)": co2 * (a["capture_kwh_per_t_co2"] * a["elec_thb_kwh"]
                                         + a["lng_cold_thb_per_t_co2"]),
    }
    if a["route"] == "nh3":
        items.update({
            "ammonia NH3": nh3 * 1000 * a["nh3_thb_kg"],
            "sulfuric acid H2SO4": h2so4 * 1000 * a["h2so4_thb_kg"],
            "steam (distillation)": a["steam_gj_per_t"] * a["steam_thb_gj"],
            "fertilizer drying (steam)": as_t * a["as_evap_gj_per_t_as"] * a["steam_thb_gj"],
        })
    else:
        items.update({
            "amine make-up": a["amine_kg_per_t"] * a["amine_thb_kg"],
            "steam (split + distil)": a["amine_steam_gj_per_t"] * a["steam_thb_gj"],
        })
    items.update({
        "catalyst + lab analysis": a["catalyst_thb_per_t"],
        "maintenance + insurance": capex(a) * a["usd_thb"] * (a["maint_frac"] + a["insure_frac"]) / a["output_t_yr"],
        "labour": a["labour_thb_yr"] / a["output_t_yr"],
        "CAPEX recovery": capex(a) * a["usd_thb"] * crf(a["discount"], a["life_yr"]) / a["output_t_yr"],
    })
    if a["route"] == "nh3":
        items["ammonium sulfate sold"] = -as_t * 1000 * a["as_thb_kg"]
    flows = dict(co2=co2, h2=h2, nh3=nh3, h2so4=h2so4, as_t=as_t)
    return items, flows


def main(a=A):
    items, f = cost(a)
    total = sum(items.values())
    gross = sum(v for v in items.values() if v > 0)
    print(f"Per tonne of {a['grade']:.0%} formic acid (plant {a['output_t_yr']:,} t/yr, "
          f"overall yield {a['yield_overall']:.0%}):")
    if a["route"] == "nh3":
        print(f"  uses  CO2 {f['co2']:.3f} t, H2 {f['h2']:.1f} kg, NH3 {f['nh3']:.3f} t, "
              f"H2SO4 {f['h2so4']:.3f} t;  makes ammonium sulfate {f['as_t']:.2f} t")
    else:
        print(f"  uses  CO2 {f['co2']:.3f} t, H2 {f['h2']:.1f} kg; amine recycled, no by-product")
    for k, v in items.items():
        print(f"  {k:26s} {v:9,.0f} THB/t  ({v/gross:5.0%} of gross)")
    print(f"  {'TOTAL':26s} {total:9,.0f} THB/t = {total/1000:.1f} THB/kg")
    truck = a["truck_trip_thb"] / a["truck_load_t"]
    delivered = total + truck
    trips = a["output_t_yr"] / a["truck_load_t"]
    print(f"\nBulk delivery to importer: {a['truck_trip_thb']:,} THB per {a['truck_load_t']} t tanker "
          f"= {truck:,.0f} THB/t; {trips:,.0f} trips/yr")
    print(f"Delivered cost {delivered:,.0f} THB/t = {delivered/1000:.2f} THB/kg  (importer's CIF assumed 17-25)")
    m = a["sell_thb_kg"] * 1000 - delivered
    print(f"Sell at {a['sell_thb_kg']} THB/kg -> margin {m:,.0f} THB/t x {a['output_t_yr']:,} t "
          f"= {m*a['output_t_yr']/1e6:,.1f} M THB/yr")

    print("\nSensitivity (THB/kg):")
    chem = ([("nh3_thb_kg", 12, 25), ("as_thb_kg", 4, 12)] if a["route"] == "nh3"
            else [("amine_thb_kg", 40, 160), ("amine_steam_gj_per_t", 10, 20)])
    for key, lo, hi in [("elec_thb_kwh", 2.5, 5.0)] + chem + [("capex_usd", 10e6, 40e6),
                        ("yield_overall", 0.8, 0.95), ("output_t_yr", 3000, 20000)]:
        v = [sum(cost(dict(a, **{key: x}))[0].values()) / 1000 for x in (lo, hi)]
        print(f"  {key:16s} {lo:>10g} -> {v[0]:5.1f} | {hi:>10g} -> {v[1]:5.1f}")


def compare():
    print("\nScenarios (THB/kg of 85 % formic acid):")
    for name, a in SCENARIOS.items():
        items, _ = cost(a)
        print(f"  {name:40s} {sum(items.values())/1000:5.1f}   CAPEX {capex(a)/1e6:5.1f} M USD")


if __name__ == "__main__":
    main(STACK_AMINE)
    compare()
