// Simulated CO2 + H2 -> HCOOH batch run in a 100 ml PTFE-lined autoclave.
// Same assumptions as ../lab_scale_calc.py, so the panel and the report agree.
// Plain C++ (no Arduino headers) so it can be tested on a PC:
//   g++ -std=c++11 -o sim_test sim_test.cpp && ./sim_test
// Every value it shows is SIMULATED, not measured.
#pragma once
#include <math.h>

namespace sim {

const float R = 8.314f, F = 96485.0f, M_FA = 46.03f;

struct Config {
  float vessel_ml = 100.0f, liquid_ml = 40.0f;
  float charge_temp_c = 25.0f;
  float p_co2_mpa = 0.6f, p_h2_mpa = 1.2f;  // absolute, at charge temperature
  float conversion = 0.30f;                 // final conversion of CO2 at 80 C
  float selectivity = 0.90f;
  float react_time_h = 2.0f;                // conversion reaches ~95 % of final in this time
  float liner_max_mpa = 3.0f, relief_set_mpa = 3.3f;
  float heat_tau_s = 600.0f;                // hotplate + autoclave thermal time constant
  float h2_flow_ml_min = 14.0f;             // PEM electrolyzer output at 2 A (~0.7 ml/(A min) per cell at 25 C)
  float co2_flow_ml_min = 50.0f;            // regulator from the capture line / cylinder
  float ea_kj = 50.0f;                      // apparent activation energy for the rate
};

enum Phase { IDLE, CHARGE, HEAT, REACT, COOL, DONE, VENTED };

inline const char* phaseName(Phase p) {
  static const char* n[] = {"IDLE", "CHARGE", "HEAT", "REACT", "COOL", "DONE", "VENTED"};
  return n[p];
}

struct State {
  Phase phase = IDLE;
  float t_s = 0, phase_t_s = 0;
  float temp_c = 25.0f, setpoint_c = 80.0f;
  float n_co2 = 0, n_h2 = 0;      // mol in headspace
  float n_co2_0 = 0;              // mol charged (limiting reactant basis)
  float x = 0;                    // CO2 conversion so far
  float flow_ml_min = 0;          // gas flow being shown (charge phase)
  float pressure_mpa = 0;
  bool warn = false;
};

class Model {
 public:
  Config c;
  State s;

  float gasVolumeL() const { return (c.vessel_ml - c.liquid_ml) / 1000.0f; }
  float targetCO2() const { return molesAt(c.p_co2_mpa); }
  float targetH2() const { return molesAt(c.p_h2_mpa); }

  void reset() { float sp = s.setpoint_c; s = State(); s.setpoint_c = sp; s.temp_c = c.charge_temp_c; }
  void start() { if (s.phase == IDLE || s.phase == DONE || s.phase == VENTED) { reset(); enter(CHARGE); } }

  // Advance the simulation by dt seconds of process time.
  void step(float dt) {
    s.t_s += dt;
    s.phase_t_s += dt;
    float ambient = c.charge_temp_c;
    switch (s.phase) {
      case IDLE: case DONE: case VENTED:
        s.temp_c += (ambient - s.temp_c) * (1 - expf(-dt / c.heat_tau_s));
        break;
      case CHARGE: {
        // CO2 first, then H2 from the electrolyzer (like the real procedure)
        float mol_per_ml = 101325.0f / (R * (ambient + 273.15f)) * 1e-6f;  // gas at 1 atm
        if (s.n_co2 < targetCO2()) {
          s.flow_ml_min = c.co2_flow_ml_min;
          s.n_co2 = fminf(targetCO2(), s.n_co2 + c.co2_flow_ml_min / 60.0f * dt * mol_per_ml);
        } else if (s.n_h2 < targetH2()) {
          s.flow_ml_min = c.h2_flow_ml_min;
          s.n_h2 = fminf(targetH2(), s.n_h2 + c.h2_flow_ml_min / 60.0f * dt * mol_per_ml);
        } else {
          s.flow_ml_min = 0;
          s.n_co2_0 = s.n_co2;
          enter(HEAT);
        }
        break;
      }
      case HEAT:
        heatToward(s.setpoint_c, dt);
        react(dt);
        if (s.temp_c > s.setpoint_c - 1.0f) enter(REACT);
        break;
      case REACT:
        heatToward(s.setpoint_c, dt);
        react(dt);
        if (s.phase_t_s >= c.react_time_h * 3600.0f) enter(COOL);
        break;
      case COOL:
        heatToward(ambient, dt);
        react(dt);
        if (s.temp_c < ambient + 5.0f) enter(DONE);
        break;
    }
    s.pressure_mpa = pressure();
    s.warn = s.pressure_mpa > 0.9f * c.liner_max_mpa;
    if (s.pressure_mpa >= c.relief_set_mpa && s.phase != VENTED) {
      // relief valve opens: the batch is lost, pressure drops to 1 atm
      float keep = 0.101325f / s.pressure_mpa;
      s.n_co2 *= keep;
      s.n_h2 *= keep;
      enter(VENTED);
      s.pressure_mpa = pressure();
    }
  }

  float hcoohMol() const { return s.n_co2_0 * s.x * c.selectivity; }
  float hcoohG() const { return hcoohMol() * M_FA; }
  float theoryG() const { return (s.n_co2_0 > 0 ? s.n_co2_0 : targetCO2()) * M_FA; }
  float yield() const { return s.x * c.selectivity; }
  float concGL() const { return hcoohG() / (c.liquid_ml / 1000.0f); }
  float h2ChargeC() const { return 2 * F * targetH2(); }

 private:
  float molesAt(float p_mpa) const {
    return p_mpa * 1e6f * gasVolumeL() * 1e-3f / (R * (c.charge_temp_c + 273.15f));
  }
  float pressure() const {
    return (s.n_co2 + s.n_h2) * R * (s.temp_c + 273.15f) / (gasVolumeL() * 1e-3f) / 1e6f;
  }
  void enter(Phase p) { s.phase = p; s.phase_t_s = 0; }
  void heatToward(float target, float dt) {
    s.temp_c += (target - s.temp_c) * (1 - expf(-dt / c.heat_tau_s));
  }
  // First-order approach to the final conversion; k is chosen so that at 80 C
  // the run reaches 95 % of `conversion` in react_time_h, and scaled by Arrhenius.
  void react(float dt) {
    if (s.n_co2_0 <= 0) return;
    float k80 = 3.0f / (c.react_time_h * 3600.0f);
    float t_k = s.temp_c + 273.15f;
    float k = k80 * expf(-c.ea_kj * 1000.0f / R * (1.0f / t_k - 1.0f / 353.15f));
    float x_new = s.x + (c.conversion - s.x) * (1 - expf(-k * dt));
    float dn = (x_new - s.x) * s.n_co2_0;  // CO2 and H2 are consumed 1:1
    s.x = x_new;
    s.n_co2 -= dn;
    s.n_h2 -= dn;
  }
};

}  // namespace sim
