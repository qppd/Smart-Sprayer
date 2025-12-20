#ifndef RELAY_CONFIG_H
#define RELAY_CONFIG_H

uint16_t RELAY_1 = 4;
uint16_t RELAY_2 = 5;

//-----------------------------------------------------------------
//FUNCTION FOR SETTING RELAY PIN MODE------------------------------
//-----------------------------------------------------------------
void initRELAY(){
  pinMode(RELAY_1, OUTPUT);
  pinMode(RELAY_2, OUTPUT);
}

//-----------------------------------------------------------------
//FUNCTION FOR OPERATING RELAY-------------------------------------
//-----------------------------------------------------------------
void operateRELAY(uint16_t RELAY, boolean OPENED) {
  if (OPENED)
    digitalWrite(RELAY, LOW);
  else
    digitalWrite(RELAY, HIGH);
}

//-----------------------------------------------------------------
//FUNCTION FOR OPERATING SOLID STATE RELAY-------------------------
//-----------------------------------------------------------------
void operateSSR(uint16_t RELAY, boolean OPENED) {
  if (OPENED)
    digitalWrite(RELAY, HIGH);
  else
    digitalWrite(RELAY, LOW);
}

#endif