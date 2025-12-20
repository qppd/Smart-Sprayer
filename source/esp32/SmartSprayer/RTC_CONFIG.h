#ifndef RTC_CONFIG_H
#define RTC_CONFIG_H

#include "PINS_CONFIG.h"
#include <TimeLib.h>
#include <TimeAlarms.h>
#include <ThreeWire.h>
#include <RtcDS1302.h>

// RTC instance
ThreeWire myWire(RTC_IO_PIN, RTC_CLK_PIN, RTC_CE_PIN); // IO, SCLK, CE
RtcDS1302<ThreeWire> Rtc(myWire);

// Global variables for alarms and menu
AlarmId sprayAlarmId = dtINVALID_ALARM_ID;
bool schedulingMode = false;
int currentMenuItem = 0;
int selectedHour = 0;
int selectedMinute = 0;

// Function declarations
void initRTC();
void syncRTCWithNTP();
bool isRTCValid();
void printRTCDateTime(const RtcDateTime& dt);
String getRTCDateTimeString();
void updateSystemTimeFromRTC();

//-----------------------------------------------------------------
//FUNCTION FOR INITIALIZING RTC------------------------------------
//-----------------------------------------------------------------
void initRTC() {
  Serial.print("Initializing RTC...");

  Rtc.Begin();

  RtcDateTime compiled = RtcDateTime(__DATE__, __TIME__);
  Serial.println();

  if (!Rtc.IsDateTimeValid()) {
    // Common Causes:
    //    1) first time you ran and the device wasn't running yet
    //    2) the battery on the device is low or even missing

    Serial.println("RTC lost confidence in the DateTime!");
    Rtc.SetDateTime(compiled);
  }

  if (!Rtc.GetIsRunning()) {
    Serial.println("RTC was not actively running, starting now");
    Rtc.SetIsRunning(true);
  }

  RtcDateTime now = Rtc.GetDateTime();
  if (now < compiled) {
    Serial.println("RTC is older than compile time!  (Updating DateTime)");
    Rtc.SetDateTime(compiled);
  } else if (now > compiled) {
    Serial.println("RTC is newer than compile time. (this is expected)");
  } else if (now == compiled) {
    Serial.println("RTC is the same as compile time! (not expected but all is fine)");
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
    // Convert to RtcDateTime
    RtcDateTime rtcTime = RtcDateTime(year(ntpTime), month(ntpTime), day(ntpTime),
                                     hour(ntpTime), minute(ntpTime), second(ntpTime));

    // Set RTC time
    Rtc.SetDateTime(rtcTime);

    Serial.println("RTC synced with NTP successfully");
    printRTCDateTime(rtcTime);
  } else {
    Serial.println("Failed to get NTP time for RTC sync");
  }
}

//-----------------------------------------------------------------
//FUNCTION FOR CHECKING RTC VALIDITY-------------------------------
//-----------------------------------------------------------------
bool isRTCValid() {
  return Rtc.IsDateTimeValid() && Rtc.GetIsRunning();
}

//-----------------------------------------------------------------
//FUNCTION FOR PRINTING RTC DATETIME-------------------------------
//-----------------------------------------------------------------
void printRTCDateTime(const RtcDateTime& dt) {
  char datestring[26];
  snprintf_P(datestring,
             countof(datestring),
             PSTR("%04u/%02u/%02u %02u:%02u:%02u"),
             dt.Year(),
             dt.Month(),
             dt.Day(),
             dt.Hour(),
             dt.Minute(),
             dt.Second());
  Serial.print("RTC DateTime: ");
  Serial.println(datestring);
}

//-----------------------------------------------------------------
//FUNCTION FOR GETTING RTC DATETIME STRING-------------------------
//-----------------------------------------------------------------
String getRTCDateTimeString() {
  if (!isRTCValid()) {
    return "RTC INVALID";
  }

  RtcDateTime dt = Rtc.GetDateTime();
  char datestring[20];
  snprintf_P(datestring,
             countof(datestring),
             PSTR("%02u:%02u:%02u %02u/%02u"),
             dt.Hour(),
             dt.Minute(),
             dt.Second(),
             dt.Day(),
             dt.Month());
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

  RtcDateTime dt = Rtc.GetDateTime();

  // Set system time using TimeLib
  setTime(dt.Hour(), dt.Minute(), dt.Second(),
          dt.Day(), dt.Month(), dt.Year());

  Serial.println("System time updated from RTC");
}

#endif // RTC_CONFIG_H