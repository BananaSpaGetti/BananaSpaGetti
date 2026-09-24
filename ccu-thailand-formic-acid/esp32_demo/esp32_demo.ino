// CCU formic acid reactor - demo control panel (ESP32 + SSD1306 OLED + 3 buttons)
//
// Shows a SIMULATED batch run of CO2 + H2 -> HCOOH in the 100 ml autoclave:
// charge (CO2, then H2 from the PEM electrolyzer) -> heat -> react -> cool.
// No sensors are read; every number comes from sim_model.h, which uses the
// same assumptions as ../lab_scale_calc.py. The screen says "SIM" so judges
// are not misled.
//
// Wiring (ESP32 DevKit v1):
//   OLED 128x64 SSD1306 I2C: SDA -> GPIO21, SCL -> GPIO22, VCC -> 3V3, GND -> GND
//   BTN_START  GPIO25 -> button -> GND   start a run / abort
//                                         (hold PAGE while pressing START = safety demo:
//                                          double charge, trips HIGH and the relief valve)
//   BTN_PAGE   GPIO26 -> button -> GND   next screen
//   BTN_TEMP   GPIO27 -> button -> GND   reactor setpoint 60 / 80 / 100 / 120 C
//   LED_WARN   GPIO2  (on-board LED)     pressure > 90 % of liner limit or vented
// Libraries: Adafruit SSD1306, Adafruit GFX (Arduino Library Manager).
// Serial (115200) prints CSV for plotting: t_min,phase,T_C,P_MPa,X,HCOOH_g

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "sim_model.h"

const int BTN_START = 25, BTN_PAGE = 26, BTN_TEMP = 27, LED_WARN = 2;
const float TIME_SCALE = 120.0f;  // process seconds per real second (4 h run ~ 2 min)
const float SETPOINTS[] = {60, 80, 100, 120};
const int N_SETPOINTS = 4, N_PAGES = 3;

Adafruit_SSD1306 oled(128, 64, &Wire, -1);
sim::Model model;
int page = 0, setpointIdx = 1;
unsigned long lastStep = 0, lastLog = 0;

struct Button {
  int pin;
  bool last;
  unsigned long changed;
  bool pressed() {  // true once per press, 30 ms debounce
    bool now = digitalRead(pin) == LOW;
    if (now != last && millis() - changed > 30) {
      last = now;
      changed = millis();
      return now;
    }
    return false;
  }
};
Button bStart{BTN_START, false, 0}, bPage{BTN_PAGE, false, 0}, bTemp{BTN_TEMP, false, 0};

void header(const char* title) {
  oled.setTextSize(1);
  oled.setCursor(0, 0);
  oled.print(title);
  oled.setCursor(104, 0);
  oled.print("SIM");
  oled.drawFastHLine(0, 9, 128, SSD1306_WHITE);
}

void bar(int y, float frac) {
  frac = constrain(frac, 0.0f, 1.0f);
  oled.drawRect(0, y, 128, 6, SSD1306_WHITE);
  oled.fillRect(1, y + 1, (int)(126 * frac), 4, SSD1306_WHITE);
}

void drawOverview() {
  const sim::State& s = model.s;
  header("REACTOR");
  oled.setCursor(0, 12);
  oled.printf("%-6s  %3d:%02d", sim::phaseName(s.phase), (int)(s.t_s / 3600), ((int)s.t_s / 60) % 60);
  oled.setTextSize(2);
  oled.setCursor(0, 22);
  oled.printf("%5.1fC", s.temp_c);
  oled.setCursor(0, 40);
  oled.printf("%4.2fMPa", s.pressure_mpa);
  oled.setTextSize(1);
  oled.setCursor(80, 26);
  oled.printf("SP %3.0f", s.setpoint_c);
  if (s.phase == sim::VENTED) {
    oled.setCursor(0, 57);
    oled.print("RELIEF VALVE OPENED");
  } else {
    bar(57, s.pressure_mpa / model.c.liner_max_mpa);
    if (s.warn) { oled.setCursor(96, 44); oled.print("HIGH"); }
  }
}

void drawGas() {
  const sim::State& s = model.s;
  header("GAS FEED");
  oled.setCursor(0, 12);
  const char* src = s.phase != sim::CHARGE ? "-" : (s.n_co2 < model.targetCO2() ? "CO2 line" : "H2 PEM");
  oled.printf("Feed : %s", src);
  oled.setCursor(0, 22);
  oled.printf("Flow : %4.1f ml/min", s.flow_ml_min);
  oled.setCursor(0, 32);
  oled.printf("CO2  : %5.2f mmol", s.n_co2 * 1e3f);
  oled.setCursor(0, 42);
  oled.printf("H2   : %5.2f mmol", s.n_h2 * 1e3f);
  oled.setCursor(0, 52);
  oled.printf("PEM  : %4.0f C needed", model.h2ChargeC());
}

void drawYield() {
  const sim::State& s = model.s;
  header("YIELD  CO2+H2>HCOOH");
  oled.setCursor(0, 12);
  oled.printf("Conv X : %5.1f %%", s.x * 100);
  oled.setCursor(0, 22);
  oled.printf("Select : %5.1f %%", model.c.selectivity * 100);
  oled.setCursor(0, 32);
  oled.printf("HCOOH  : %5.3f g", model.hcoohG());
  oled.setCursor(0, 42);
  oled.printf("Theory : %5.3f g", model.theoryG());
  oled.setCursor(0, 52);
  oled.printf("%4.1f%% yield %4.1f g/L", model.yield() * 100, model.concGL());
}

void setup() {
  Serial.begin(115200);
  pinMode(BTN_START, INPUT_PULLUP);
  pinMode(BTN_PAGE, INPUT_PULLUP);
  pinMode(BTN_TEMP, INPUT_PULLUP);
  pinMode(LED_WARN, OUTPUT);
  if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) Serial.println("SSD1306 not found at 0x3C");
  oled.setTextColor(SSD1306_WHITE);
  model.s.setpoint_c = SETPOINTS[setpointIdx];
  model.reset();
  Serial.println("t_min,phase,T_C,P_MPa,X,HCOOH_g");
  lastStep = millis();
}

void loop() {
  if (bStart.pressed()) {
    if (model.s.phase == sim::IDLE || model.s.phase == sim::DONE || model.s.phase == sim::VENTED) {
      bool safetyDemo = digitalRead(BTN_PAGE) == LOW;
      model.c.p_co2_mpa = safetyDemo ? 1.0f : sim::Config().p_co2_mpa;
      model.c.p_h2_mpa = safetyDemo ? 2.0f : sim::Config().p_h2_mpa;
      if (safetyDemo) {
        setpointIdx = 2;  // 100 C
        model.s.setpoint_c = SETPOINTS[setpointIdx];
      }
      model.start();
    } else {
      model.reset();  // abort
    }
  }
  if (bPage.pressed()) page = (page + 1) % N_PAGES;
  if (bTemp.pressed()) {
    setpointIdx = (setpointIdx + 1) % N_SETPOINTS;
    model.s.setpoint_c = SETPOINTS[setpointIdx];
  }

  unsigned long now = millis();
  float dt = (now - lastStep) / 1000.0f * TIME_SCALE;
  lastStep = now;
  while (dt > 0) {  // small steps keep the heating and kinetics stable
    float h = dt > 5.0f ? 5.0f : dt;
    model.step(h);
    dt -= h;
  }
  digitalWrite(LED_WARN, model.s.warn || model.s.phase == sim::VENTED ? HIGH : LOW);

  oled.clearDisplay();
  if (page == 0) drawOverview();
  else if (page == 1) drawGas();
  else drawYield();
  oled.display();

  if (now - lastLog > 500 && model.s.phase != sim::IDLE) {
    lastLog = now;
    Serial.printf("%.1f,%s,%.1f,%.3f,%.4f,%.4f\n", model.s.t_s / 60, sim::phaseName(model.s.phase),
                  model.s.temp_c, model.s.pressure_mpa, model.s.x, model.hcoohG());
  }
  delay(20);
}
