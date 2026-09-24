# Project context: CCU system for formic acid production (Thailand import replacement)

Engineering innovation project (student). Read this first, then README.md.

## Goal

Capture industrial CO₂ and convert it to formic acid (HCOOH) to replace part of the
formic acid Thailand imports (not all of it is imported), supporting the net-zero transition.
Sales channel: sell to existing formic acid importers/distributors, who resell to
farmers (mainly rubber latex coagulation).

- **CO₂ source (current target):** EGAT Bang Pakong power plant, Chachoengsao: 3,248 MW,
  thermal + combined-cycle, natural gas (fuel oil / diesel backup); see `bang_pakong_co2.py`.
  Earlier work in this folder (README.md, cost_model.py) modelled **Mae Moh (lignite)**;
  keep both, but new work should target Bang Pakong.
- **Deployment:** not a separate factory. The unit is retrofitted at the Bang Pakong stack
  (flue gas tapped from the duct at the stack base), sharing the plant's land, LP steam, cooling
  water, power and operators. `process_cost.py` has standalone vs stack scenarios.
- **Market:** rubber, leather and textile plants in the Eastern Economic Corridor (EEC),
  close to Bang Pakong, so logistics are short.
- **Process (team's design):** flue gas → dry → LNG cold box (−150 to −180 °C) → CO₂ freezes
  as dry ice, N₂/O₂/Ar pass through (`cryo_capture.py`) → dry ice into autoclave with Ru catalyst
  + base → H₂ from PEM electrolysis of treated cooling water, CO₂:H₂ = 1:1 → formate → HCOOH 85 %.
  **Formic acid is the main product.** Recommended base: a recyclable tertiary amine (formate–amine
  adduct split by heat, amine returns to the reactor, no by-product; 17.9 THB/kg at the stack).
  The team's first idea, ammonia + H₂SO₄, makes 1.2 t ammonium sulfate per t product and only pays
  if that fertilizer is sold (27.9 THB/kg if not). Heating ammonium formate gives formamide, not formic acid.
  Electrolyzer power must be renewable: grid/gas power (~0.4 kg CO₂/kWh × ~55 kWh/kg H₂) emits
  about as much CO₂ as the process uses.

## Hardware being designed

| Item | Spec |
|---|---|
| CO₂ source | gas cylinder / capture line from EGAT Bang Pakong |
| H₂ source | PEM electrolyzer stack |
| Reactor | hydrothermal autoclave, SS316, 50–100 ml, PTFE liner, magnetic stirrer, 0–5 MPa gauge, relief valve, thermowell + type K thermocouple |
| Stirring / heating | DLAB H280-Pro style hotplate magnetic stirrer |
| CAD | Autodesk Inventor: assembly, 3D sketch paths for piping, motion/flow animation |
| Physical mockup | recycled / low-cost: clear acrylic, containers, spray-painted structure (reactor, gas tank, electrolyzer) |
| Demo panel | ESP32 + OLED + push buttons simulating pressure, temperature, flow and yield for judges |

## Files

| File | What it is |
|---|---|
| `README.md` | Thai report: capture cost (Mae Moh), process, product quality, uses, related papers |
| `cost_model.py` | capture cost + levelized formic acid cost (plant scale, Mae Moh assumptions) |
| `lab_scale_calc.py` | autoclave stoichiometry, limiting reactant, theoretical/actual yield, pressure safety check, PEM electrolyzer charge/time |
| `esp32_demo/` | demo control panel firmware; `sim_model.h` holds the physics and uses the same assumptions as `lab_scale_calc.py` |
| `cryo_capture.py` | frost points of flue gas components, CO₂ capture vs temperature, LNG cold needed, max dry ice per autoclave charge |
| `process_cost.py` | levelized cost per t of 85 % formic acid, amine route (default) or NH₃ + H₂SO₄ route, scenarios and sensitivity |
| `bang_pakong_co2.py` | Bang Pakong emissions (assumed CF/EF ranges) vs CO₂ a formic acid plant needs |
| `market/` | HS 29151100 import values (Jan 2023–2026), farmer prices, target distributors + interview questions (`distributors.md`) |
| `EGAT_capture_cost_research.md` | what is and is not published about EGAT capture costs |
| `summaries/`, `pdfs/` | Thai summaries and open-access PDFs of related papers |

Checks: `python3 lab_scale_calc.py`, `python3 cost_model.py`,
`cd esp32_demo && g++ -std=c++11 -o sim_test sim_test.cpp && ./sim_test` (exit 0 = pass).
If you change an assumption, change it in both `lab_scale_calc.py` and `esp32_demo/sim_model.h`.

## Engineering caveats (keep these in any report or slide)

1. **Gas plant ≠ coal plant.** Combined-cycle flue gas is only ~3–4 vol% CO₂ (coal ~12–14 %),
   so capture per tonne costs more than the Mae Moh figure in README.md. No verified
   Bang Pakong capture cost was found (see `EGAT_capture_cost_research.md`); a Bang Pakong
   version of `cost_model.py` is still to do.
2. **CO₂ + H₂ → HCOOH is thermodynamically uphill without a base** (ΔG° ≈ +33 kJ/mol in the
   gas phase). Real systems add a base (e.g. triethylamine, KHCO₃/NaHCO₃) and get **formate**,
   which then needs acidification or amine splitting and distillation to get HCOOH.
3. **Pressure limit:** the gauge reads 0–5 MPa but PTFE-lined autoclaves are usually rated
   ≈ 3 MPa and ≈ 200 °C. `lab_scale_calc.py` checks against the lower limit.
4. **Demo values are simulated.** The ESP32 panel shows "SIM" on screen; do not present its
   numbers as measurements.
5. **Not 100 % imported** (confirmed by the team). Get the real import volume and CIF price
   from Thai customs statistics (HS 2915.11) before putting numbers on a slide.
6. **Bang Pakong CO₂ is falling every year**, but formic acid needs only ~0.96 t CO₂ per t,
   a tiny slipstream of a power plant's emissions. The real risk is unit retirement, not
   volume: plan modular capture and a backup CO₂ source (e.g. fermentation or gas-separation
   CO₂ in the EEC).
