# Smart-Sprayer System Flowchart

```mermaid
flowchart TD
    %% Start of Program
    START([ESP32 Power On])

    %% Setup Function
    SETUP[Setup Function]
    SERIAL_INIT[Serial.begin(9600)]
    LCD_INIT[initLCD()]
    GSM_INIT[initGSM()]
    RELAY_INIT[initRELAY()]
    SR04_INIT[initSR04()]
    WIFI_INIT[initWIFI()]
    FIREBASE_INIT[initFIREBASE()]
    NTP_INIT[initNTP()]
    BUZZER_INIT[initBuzzer()]
    LED_INIT[initLEDs()]
    BUTTON_INIT[initBUTTONS()]
    RTC_INIT[initRTC()]
    SYNC_RTC[syncRTCWithNTP()]

    %% Main Loop
    LOOP[Main Loop - Continuous]
    SET_FLAGS[setInputFlags()]
    RESOLVE_FLAGS[resolveInputFlags()]
    ALARM_DELAY[Alarm.delay(10)]
    SERIAL_CHECK{Serial.available()?}

    %% Serial Command Processing
    READ_COMMAND[Read Serial Command]
    TRIM_COMMAND[command.trim()]

    %% Command Decision Tree
    COMMAND_DECISION{Command Type}

    %% Relay Commands
    RELAY1_ON[operateRELAY(RELAY_1, true)<br/>Print: Relay 1 turned ON]
    RELAY1_OFF[operateRELAY(RELAY_1, false)<br/>Print: Relay 1 turned OFF]
    RELAY2_ON[operateRELAY(RELAY_2, true)<br/>Print: Relay 2 turned ON]
    RELAY2_OFF[operateRELAY(RELAY_2, false)<br/>Print: Relay 2 turned OFF]

    %% GSM Commands
    SEND_SMS[sendSMS(+1234567890, Test SMS)<br/>Print: SMS sent]
    SEND_SMS_ALL[sendSMSToAll(Test SMS)<br/>Print: SMS sent to all]
    CHECK_NETWORK[checkNetwork()<br/>Print: Network check initiated]

    %% Ultrasonic Commands
    GET_DISTANCE1[readDistance()<br/>Print: Distance 1: X cm]
    GET_DISTANCE2[readDistance2()<br/>Print: Distance 2: X cm]

    %% Buzzer Commands
    BUZZER_ON[buzzerOn()<br/>Print: Buzzer turned ON]
    BUZZER_OFF[buzzerOff()<br/>Print: Buzzer turned OFF]
    BUZZER_BEEP[buzzerBeep()<br/>Print: Buzzer beeped]

    %% LED Commands
    LED_OK[setSystemOK()<br/>Print: System OK LED ON]
    LED_ERROR[setSystemError()<br/>Print: System Error LED ON]
    LED_WARNING[setSystemWarning()<br/>Print: System Warning LEDs ON]
    LED_CLEAR[clearSystemLEDs()<br/>Print: System LEDs cleared]
    SET_LEDS[setSystemLEDs(1,0)<br/>Print: System LEDs set manually]

    %% Notification Test Commands
    TEST_ALERT[commercialAlertPattern()<br/>Print: Commercial alert pattern triggered]
    TEST_SUCCESS[commercialSuccessPattern()<br/>Print: Commercial success pattern triggered]
    TEST_ERROR[commercialErrorPattern()<br/>Print: Commercial error pattern triggered]
    TEST_NETWORK[checkAndReconnectNetwork()<br/>Print: Network test result]

    %% Weather Command
    CHECK_WEATHER[checkWeatherForRain()]
    WEATHER_RAIN{willRain?}
    WEATHER_RAIN_MSG[Print: Rain expected - avoid spraying]
    WEATHER_CLEAR_MSG[Print: No rain - safe to spray]

    %% LCD Commands
    CLEAR_LCD[clearLCD()<br/>Print: LCD cleared]
    TEST_LCD[setLCDText() x3<br/>Print: LCD test display set]

    %% Time Commands
    GET_TIME[getFormattedDateTime()<br/>Print: Current time: X]
    GET_TIMESTAMP[getNTPTimestamp()<br/>Print: NTP Timestamp: X]
    GET_TS_FALLBACK[getNTPTimestampWithFallback()<br/>Print: NTP Timestamp (fallback): X]
    GET_LOG_PREFIX[getCurrentLogPrefix()<br/>Print: Log prefix: X]
    GET_DT_FALLBACK[getFormattedDateTimeWithFallback()<br/>Print: DateTime (fallback): X]
    CHECK_NTP[isNTPSynced()<br/>Print: NTP Synced: Yes/No]
    UPDATE_NTP[getNTPDate()<br/>Print: NTP date updated]

    %% System Commands
    WIFI_RESET[resetWiFiSettings()<br/>Print: Resetting WiFi settings]
    BUTTON_STATUS[isButtonPressed()<br/>Print: Button pressed: Yes/No]
    GET_LEVEL[Calculate level & percentage<br/>Print: Distance, Filled, Percentage]

    %% Unknown Command
    UNKNOWN_CMD[Print: Unknown command]

    %% Flow Connections
    START --> SETUP
    SETUP --> SERIAL_INIT
    SERIAL_INIT --> LCD_INIT
    LCD_INIT --> GSM_INIT
    GSM_INIT --> RELAY_INIT
    RELAY_INIT --> SR04_INIT
    SR04_INIT --> WIFI_INIT
    WIFI_INIT --> FIREBASE_INIT
    FIREBASE_INIT --> NTP_INIT
    NTP_INIT --> BUZZER_INIT
    BUZZER_INIT --> LED_INIT
    LED_INIT --> BUTTON_INIT
    BUTTON_INIT --> RTC_INIT
    RTC_INIT --> SYNC_RTC
    SYNC_RTC --> LOOP

    LOOP --> SET_FLAGS
    SET_FLAGS --> RESOLVE_FLAGS
    RESOLVE_FLAGS --> ALARM_DELAY
    ALARM_DELAY --> SERIAL_CHECK

    SERIAL_CHECK -->|No| LOOP
    SERIAL_CHECK -->|Yes| READ_COMMAND
    READ_COMMAND --> TRIM_COMMAND
    TRIM_COMMAND --> COMMAND_DECISION

    COMMAND_DECISION -->|operate-relay1_on| RELAY1_ON
    COMMAND_DECISION -->|operate-relay1_off| RELAY1_OFF
    COMMAND_DECISION -->|operate-relay2_on| RELAY2_ON
    COMMAND_DECISION -->|operate-relay2_off| RELAY2_OFF
    COMMAND_DECISION -->|send-sms| SEND_SMS
    COMMAND_DECISION -->|send-sms-to-all| SEND_SMS_ALL
    COMMAND_DECISION -->|check-network| CHECK_NETWORK
    COMMAND_DECISION -->|get-distance1| GET_DISTANCE1
    COMMAND_DECISION -->|get-distance2| GET_DISTANCE2
    COMMAND_DECISION -->|buzzer-on| BUZZER_ON
    COMMAND_DECISION -->|buzzer-off| BUZZER_OFF
    COMMAND_DECISION -->|buzzer-beep| BUZZER_BEEP
    COMMAND_DECISION -->|led-ok| LED_OK
    COMMAND_DECISION -->|led-error| LED_ERROR
    COMMAND_DECISION -->|led-warning| LED_WARNING
    COMMAND_DECISION -->|led-clear| LED_CLEAR
    COMMAND_DECISION -->|set-leds| SET_LEDS
    COMMAND_DECISION -->|test-alert| TEST_ALERT
    COMMAND_DECISION -->|test-success| TEST_SUCCESS
    COMMAND_DECISION -->|test-error| TEST_ERROR
    COMMAND_DECISION -->|test-network| TEST_NETWORK
    COMMAND_DECISION -->|check-weather| CHECK_WEATHER
    COMMAND_DECISION -->|clear-lcd| CLEAR_LCD
    COMMAND_DECISION -->|test-lcd| TEST_LCD
    COMMAND_DECISION -->|get-time| GET_TIME
    COMMAND_DECISION -->|get-timestamp| GET_TIMESTAMP
    COMMAND_DECISION -->|get-timestamp-fallback| GET_TS_FALLBACK
    COMMAND_DECISION -->|get-log-prefix| GET_LOG_PREFIX
    COMMAND_DECISION -->|get-datetime-fallback| GET_DT_FALLBACK
    COMMAND_DECISION -->|check-ntp| CHECK_NTP
    COMMAND_DECISION -->|update-ntp| UPDATE_NTP
    COMMAND_DECISION -->|wifi-reset| WIFI_RESET
    COMMAND_DECISION -->|button-status| BUTTON_STATUS
    COMMAND_DECISION -->|get-level| GET_LEVEL
    COMMAND_DECISION -->|Unknown| UNKNOWN_CMD

    CHECK_WEATHER --> WEATHER_RAIN
    WEATHER_RAIN -->|True| WEATHER_RAIN_MSG
    WEATHER_RAIN -->|False| WEATHER_CLEAR_MSG

    RELAY1_ON --> LOOP
    RELAY1_OFF --> LOOP
    RELAY2_ON --> LOOP
    RELAY2_OFF --> LOOP
    SEND_SMS --> LOOP
    SEND_SMS_ALL --> LOOP
    CHECK_NETWORK --> LOOP
    GET_DISTANCE1 --> LOOP
    GET_DISTANCE2 --> LOOP
    BUZZER_ON --> LOOP
    BUZZER_OFF --> LOOP
    BUZZER_BEEP --> LOOP
    LED_OK --> LOOP
    LED_ERROR --> LOOP
    LED_WARNING --> LOOP
    LED_CLEAR --> LOOP
    SET_LEDS --> LOOP
    TEST_ALERT --> LOOP
    TEST_SUCCESS --> LOOP
    TEST_ERROR --> LOOP
    TEST_NETWORK --> LOOP
    WEATHER_RAIN_MSG --> LOOP
    WEATHER_CLEAR_MSG --> LOOP
    CLEAR_LCD --> LOOP
    TEST_LCD --> LOOP
    GET_TIME --> LOOP
    GET_TIMESTAMP --> LOOP
    GET_TS_FALLBACK --> LOOP
    GET_LOG_PREFIX --> LOOP
    GET_DT_FALLBACK --> LOOP
    CHECK_NTP --> LOOP
    UPDATE_NTP --> LOOP
    WIFI_RESET --> LOOP
    BUTTON_STATUS --> LOOP
    GET_LEVEL --> LOOP
    UNKNOWN_CMD --> LOOP

    %% Styling
    classDef setupClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef loopClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef commandClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef decisionClass fill:#fff3e0,stroke:#e65100,stroke-width:2px

    class SETUP,START setupClass
    class LOOP,SET_FLAGS,RESOLVE_FLAGS,ALARM_DELAY loopClass
    class RELAY1_ON,RELAY1_OFF,RELAY2_ON,RELAY2_OFF,SEND_SMS,SEND_SMS_ALL,CHECK_NETWORK,GET_DISTANCE1,GET_DISTANCE2,BUZZER_ON,BUZZER_OFF,BUZZER_BEEP,LED_OK,LED_ERROR,LED_WARNING,LED_CLEAR,SET_LEDS,TEST_ALERT,TEST_SUCCESS,TEST_ERROR,TEST_NETWORK,WEATHER_RAIN_MSG,WEATHER_CLEAR_MSG,CLEAR_LCD,TEST_LCD,GET_TIME,GET_TIMESTAMP,GET_TS_FALLBACK,GET_LOG_PREFIX,GET_DT_FALLBACK,CHECK_NTP,UPDATE_NTP,WIFI_RESET,BUTTON_STATUS,GET_LEVEL,UNKNOWN_CMD commandClass
    class COMMAND_DECISION,WEATHER_RAIN,SERIAL_CHECK decisionClass
```

## Flowchart Legend

### **Setup Phase (Blue)**
- Initializes all system components in sequence
- Configures hardware interfaces and communication protocols
- Performs initial time synchronization

### **Main Loop (Purple)**
- Continuous operation cycle
- Handles button inputs and alarm triggers
- Processes serial commands when available

### **Command Processing (Green)**
- Extensive command set for system testing and control
- Covers all hardware components and system functions
- Provides immediate feedback for each command

### **Decision Points (Orange)**
- Command type routing
- Weather condition checking
- Serial data availability

### **Key System Features**
1. **Dual Relay Control**: Independent pump operation
2. **GSM Communication**: SMS notifications and network monitoring
3. **Ultrasonic Sensing**: Container level monitoring
4. **Audio/Visual Feedback**: Commercial-grade buzzer and LED patterns
5. **Weather Integration**: Rain detection and postponement logic
6. **Time Management**: NTP synchronization and RTC backup
7. **Button Interface**: 4-button menu navigation system
8. **Serial Diagnostics**: Comprehensive testing commands

This flowchart represents the complete operational flow of the Smart-Sprayer IoT system, from initialization through continuous operation and command processing.</content>
<parameter name="filePath">c:\Users\sajed\Desktop\PROJECTS\Smart-Sprayer\diagram\SmartSprayer_Flowchart.md