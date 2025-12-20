#include "LCD_CONFIG.h"
#include "GSM_CONFIG.h"
#include "RELAY_CONFIG.h"
#include "SR04_CONFIG.h"

void setup() {
  initLCD();
  initGSM();
  initRELAY();
  initSR04();
}

void loop() {
  // put your main code here, to run repeatedly:

}