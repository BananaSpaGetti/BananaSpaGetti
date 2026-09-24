// Host check of sim_model.h: runs one batch and prints the numbers that
// lab_scale_calc.py should also give.  g++ -std=c++11 -o sim_test sim_test.cpp && ./sim_test
#include <stdio.h>
#include "sim_model.h"

int run(float setpoint, bool verbose) {
  sim::Model m;
  m.s.setpoint_c = setpoint;
  m.start();
  float p_max = 0;
  sim::Phase last = sim::IDLE;
  for (int i = 0; i < 6 * 3600 && m.s.phase != sim::DONE && m.s.phase != sim::VENTED; i++) {
    m.step(1.0f);
    if (m.s.pressure_mpa > p_max) p_max = m.s.pressure_mpa;
    if (verbose && m.s.phase != last) {
      printf("  t=%6.1f min  %-6s T=%5.1f C  P=%4.2f MPa  X=%4.1f%%\n", m.s.t_s / 60,
             sim::phaseName(m.s.phase), m.s.temp_c, m.s.pressure_mpa, m.s.x * 100);
      last = m.s.phase;
    }
  }
  printf("setpoint %3.0f C: end=%s  CO2 %.2f mmol  H2 %.2f mmol  Pmax %.2f MPa  "
         "HCOOH %.3f g of %.3f g (yield %.1f%%)  %.2f g/L\n",
         setpoint, sim::phaseName(m.s.phase), m.s.n_co2_0 * 1e3, m.targetH2() * 1e3, p_max,
         m.hcoohG(), m.theoryG(), m.yield() * 100, m.concGL());
  return m.s.phase == sim::DONE ? 0 : 1;
}

int main() {
  int fail = run(80, true);
  run(100, false);
  // hotter than the charge allows: must trip the relief valve
  sim::Model m;
  m.c.p_co2_mpa = 1.0f;
  m.c.p_h2_mpa = 2.0f;
  m.s.setpoint_c = 100;
  m.start();
  for (int i = 0; i < 6 * 3600 && m.s.phase != sim::VENTED && m.s.phase != sim::DONE; i++) m.step(1.0f);
  printf("overcharge 1.0+2.0 MPa at 100 C: end=%s\n", sim::phaseName(m.s.phase));
  fail |= m.s.phase != sim::VENTED;
  return fail;
}
