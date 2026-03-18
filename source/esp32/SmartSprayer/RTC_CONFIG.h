#ifndef RTC_CONFIG_H
#define RTC_CONFIG_H

// PINS_CONFIG.h is included first in SmartSprayer.ino
#include <TimeLib.h>
#include <TimeAlarms.h>
#include <virtuabotixRTC.h>

// Utility macro
#define countof(a) (sizeof(a) / sizeof(a[0]))

// RTC instance (CLK, DAT, RST)
virtuabotixRTC myRTC(RTC_CLK_PIN, RTC_DAT_PIN, RTC_RST_PIN);

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
  Serial.println("Initializing DS1302 RTC...");

  // Force set initial time with correct year format (2026-02-01 01:22:00)
  // setDS1302Time(seconds, minutes, hours, day of week, day, month, year)
  // Year should be 2-digit: 26 for 2026
  myRTC.setDS1302Time(0, 22, 1, 7, 1, 2, 26);  // Saturday, Feb 1, 2026 01:22:00
  delay(200);
  
  // Read back and verify
  myRTC.updateTime();
  Serial.print("[DEBUG] After init, year value: ");
  Serial.println(myRTC.year);

  // Sync system time with RTC
  updateSystemTimeFromRTC();

  Serial.println("DS1302 RTC initialized successfully!");
  printRTCDateTime();
}

//-----------------------------------------------------------------
//FUNCTION FOR SYNCING RTC WITH NTP--------------------------------
//-----------------------------------------------------------------
void syncRTCWithNTP() {
  Serial.println("Syncing DS1302 RTC with NTP...");

  // Get current NTP time
  time_t ntpTime = now();

  if (ntpTime > 0) {
    // Set RTC time using DS1302
    // setDS1302Time(seconds, minutes, hours, day of week, day, month, year)
    myRTC.setDS1302Time(
      second(ntpTime),
      minute(ntpTime),
      hour(ntpTime),
      weekday(ntpTime),
      day(ntpTime),
      month(ntpTime),
      year(ntpTime) - 2000  // DS1302 uses 2-digit year
    );

    Serial.println("DS1302 RTC synced with NTP successfully");
    printRTCDateTime();
  } else {
    Serial.println("Failed to get NTP time for RTC sync");
  }
}

//-----------------------------------------------------------------
//FUNCTION FOR CHECKING RTC VALIDITY-------------------------------
//-----------------------------------------------------------------
bool isRTCValid() {
  myRTC.updateTime();
  // Check if year is reasonable (between 2000 and 2099)
  return (myRTC.year >= 0 && myRTC.year <= 99);
}

//-----------------------------------------------------------------
//FUNCTION FOR PRINTING RTC DATETIME-------------------------------
//-----------------------------------------------------------------
void printRTCDateTime() {
  // Update time from DS1302
  myRTC.updateTime();

  // Debug: print raw year value
  Serial.print("[DEBUG] Raw year value from RTC: ");
  Serial.println(myRTC.year);

  // Print in format: Date / Time: DD/MM/YYYY HH:MM:SS
  Serial.print("Date / Time: ");
  if (myRTC.dayofmonth < 10) Serial.print("0");
  Serial.print(myRTC.dayofmonth);
  Serial.print("/");
  if (myRTC.month < 10) Serial.print("0");
  Serial.print(myRTC.month);
  Serial.print("/");
  
  // Handle RTC year offset bug: RTC adds ~2096 to year value
  // If year > 2000, subtract 2096 to get correct 20XX year
  int displayYear;
  if (myRTC.year > 2000) {
    displayYear = myRTC.year - 2096;  // Remove RTC offset
    if (displayYear < 2000) displayYear += 2000;  // Add century if needed
  } else if (myRTC.year > 100) {
    displayYear = myRTC.year;  // Already full year
  } else {
    displayYear = myRTC.year + 2000;  // Add century for 2-digit year
  }
  Serial.print(displayYear);
  
  Serial.print("  ");
  if (myRTC.hours < 10) Serial.print("0");
  Serial.print(myRTC.hours);
  Serial.print(":");
  if (myRTC.minutes < 10) Serial.print("0");
  Serial.print(myRTC.minutes);
  Serial.print(":");
  if (myRTC.seconds < 10) Serial.print("0");
  Serial.println(myRTC.seconds);
}

//-----------------------------------------------------------------
//FUNCTION FOR GETTING RTC DATETIME STRING-------------------------
//-----------------------------------------------------------------
String getRTCDateTimeString() {
  myRTC.updateTime();

  // Handle RTC year offset bug: RTC adds ~2096 to year value
  int displayYear;
  if (myRTC.year > 2000) {
    displayYear = myRTC.year - 2096;  // Remove RTC offset
    if (displayYear < 2000) displayYear += 2000;  // Add century if needed
  } else if (myRTC.year > 100) {
    displayYear = myRTC.year;  // Already full year
  } else {
    displayYear = myRTC.year + 2000;  // Add century for 2-digit year
  }

  char datestring[25];
  snprintf(datestring,
           sizeof(datestring),
           "%02d:%02d:%02d %02d/%02d/%04d",
           myRTC.hours,
           myRTC.minutes,
           myRTC.seconds,
           myRTC.dayofmonth,
           myRTC.month,
           displayYear);
  return String(datestring);
}

//-----------------------------------------------------------------
//FUNCTION FOR GETTING FORMATTED DATETIME--------------------------
//-----------------------------------------------------------------
String getFormattedDateTime() {
  return getRTCDateTimeString();
}

//-----------------------------------------------------------------
//FUNCTION FOR UPDATING SYSTEM TIME FROM RTC-----------------------
//-----------------------------------------------------------------
void updateSystemTimeFromRTC() {
  myRTC.updateTime();

  // Set system time using TimeLib
  setTime(myRTC.hours, myRTC.minutes, myRTC.seconds,
          myRTC.dayofmonth, myRTC.month, myRTC.year + 2000);

  Serial.println("System time updated from DS1302 RTC");
}

//-----------------------------------------------------------------
//FUNCTION FOR SETTING RTC TIME MANUALLY---------------------------
//-----------------------------------------------------------------
void setRTCTimeManual(int year, int month, int day, int hour, int minute, int second) {
  // Calculate day of week (1=Monday, 7=Sunday)
  // Using simplified algorithm - you can improve this
  int dow = 1;  // Default to Monday
  
  Serial.print("[RTC] Setting time to: 20");
  Serial.print(year);
  Serial.print("-");
  Serial.print(month);
  Serial.print("-");
  Serial.print(day);
  Serial.print(" ");
  Serial.print(hour);
  Serial.print(":");
  Serial.print(minute);
  Serial.print(":");
  Serial.print(second);
  Serial.println();
  
  myRTC.setDS1302Time(second, minute, hour, dow, day, month, year);
  delay(100);
  myRTC.updateTime();
  
  Serial.println("[RTC] Time set successfully!");
  printRTCDateTime();
}

#endif // RTC_CONFIG_H