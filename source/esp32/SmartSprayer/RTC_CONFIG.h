#ifndef RTC_CONFIG_H
#define RTC_CONFIG_H

#include "PINS_CONFIG.h"
#include <TimeLib.h>
#include <TimeAlarms.h>
#include <Wire.h>
#include <DS3231.h>

// RTC instance
DS3231 myRTC;
bool h12Flag;
bool pmFlag;

// Global variables for alarms and menu
AlarmId sprayAlarmId1 = dtINVALID_ALARM_ID;
AlarmId sprayAlarmId2 = dtINVALID_ALARM_ID;
bool schedulingMode = false;
int currentMenuItem = 0;
int selectedHour = 0;
int selectedMinute = 0;
int selectedPump = 1;

// Function declarations
void initRTC();
void syncRTCWithNTP();
bool isRTCValid();
void printRTCDateTime();
String getRTCDateTimeString();
void updateSystemTimeFromRTC();

//-----------------------------------------------------------------
//FUNCTION FOR INITIALIZING RTC------------------------------------
//-----------------------------------------------------------------
void initRTC() {
  Serial.print("Initializing RTC...");

  Wire.begin();

  myRTC.setClockMode(false);  // set to 24h

  if (myRTC.oscillatorCheck()) {
    Serial.println("RTC oscillator is running");
  } else {
    Serial.println("RTC oscillator has stopped or battery is low");
  }

  // Sync system time with RTC initially
  updateSystemTimeFromRTC();

  Serial.println("RTC initialized successfully!");
}

//-----------------------------------------------------------------
//FUNCTION FOR SYNCING RTC WITH NTP--------------------------------
//-----------------------------------------------------------------
void syncRTCWithNTP() {
  Serial.println("Syncing RTC with NTP...");

  // Get current NTP time
  time_t ntpTime = now();

  if (ntpTime > 0) {
    // Set RTC time
    myRTC.setYear(year(ntpTime) - 2000);
    myRTC.setMonth(month(ntpTime));
    myRTC.setDate(day(ntpTime));
    myRTC.setDoW(weekday(ntpTime));  // TimeLib weekday is 1-7, DS3231 expects 1-7
    myRTC.setHour(hour(ntpTime));
    myRTC.setMinute(minute(ntpTime));
    myRTC.setSecond(second(ntpTime));

    Serial.println("RTC synced with NTP successfully");
    printRTCDateTime();
  } else {
    Serial.println("Failed to get NTP time for RTC sync");
  }
}

//-----------------------------------------------------------------
//FUNCTION FOR CHECKING RTC VALIDITY-------------------------------
//-----------------------------------------------------------------
bool isRTCValid() {
  return myRTC.oscillatorCheck();
}

//-----------------------------------------------------------------
//FUNCTION FOR PRINTING RTC DATETIME-------------------------------
//-----------------------------------------------------------------
void printRTCDateTime() {
  // send what's going on to the serial monitor.
  
  // Start with the year
  Serial.print("2");
  if (myRTC.getCentury()) {      // Won't need this for 89 years.
    Serial.print("1");
  } else {
    Serial.print("0");
  }
  Serial.print(myRTC.getYear(), DEC);
  Serial.print(' ');
  
  // then the month
  Serial.print(myRTC.getMonth(myRTC.getCentury()), DEC);
  Serial.print(" ");
  
  // then the date
  Serial.print(myRTC.getDate(), DEC);
  Serial.print(" ");
  
  // and the day of the week
  Serial.print(myRTC.getDoW(), DEC);
  Serial.print(" ");
  
  // Finally the hour, minute, and second
  Serial.print(myRTC.getHour(h12Flag, pmFlag), DEC);
  Serial.print(" ");
  Serial.print(myRTC.getMinute(), DEC);
  Serial.print(" ");
  Serial.print(myRTC.getSecond(), DEC);
 
  // Add AM/PM indicator
  if (h12Flag) {
    if (pmFlag) {
      Serial.print(" PM ");
    } else {
      Serial.print(" AM ");
    }
  } else {
    Serial.print(" 24h ");
  }
 
  // Display the temperature
  Serial.print("T=");
  Serial.print(myRTC.getTemperature(), 2);
  
  // Tell whether the time is (likely to be) valid
  if (myRTC.oscillatorCheck()) {
    Serial.print(" O+");
  } else {
    Serial.print(" O-");
  }
 
  Serial.println();
}

//-----------------------------------------------------------------
//FUNCTION FOR GETTING RTC DATETIME STRING-------------------------
//-----------------------------------------------------------------
String getRTCDateTimeString() {
  if (!isRTCValid()) {
    return "RTC INVALID";
  }

  char datestring[20];
  snprintf_P(datestring,
             countof(datestring),
             PSTR("%02u:%02u:%02u %02u/%02u"),
             myRTC.getHour(h12Flag, pmFlag),
             myRTC.getMinute(),
             myRTC.getSecond(),
             myRTC.getDate(),
             myRTC.getMonth(myRTC.getCentury()));
  return String(datestring);
}

//-----------------------------------------------------------------
//FUNCTION FOR UPDATING SYSTEM TIME FROM RTC-----------------------
//-----------------------------------------------------------------
void updateSystemTimeFromRTC() {
  if (!isRTCValid()) {
    Serial.println("Cannot update system time: RTC invalid");
    return;
  }

void updateSystemTimeFromRTC() {
  if (!isRTCValid()) {
    Serial.println("Cannot update system time: RTC invalid");
    return;
  }

  // Set system time using TimeLib
  setTime(myRTC.getHour(h12Flag, pmFlag), myRTC.getMinute(), myRTC.getSecond(),
          myRTC.getDate(), myRTC.getMonth(myRTC.getCentury()), myRTC.getYear() + 2000);

  Serial.println("System time updated from RTC");
}
}

#endif // RTC_CONFIG_H