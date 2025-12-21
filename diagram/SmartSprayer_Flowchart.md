# Smart-Sprayer System Flowchart

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 60}}}%%
flowchart TD
    %% System Startup
    START(["ESP32 Power On"])
    SETUP(["System Initialization<br/>Hardware Setup"])
    READY(["System Ready<br/>LCD Display Active"])

    %% Main Monitoring Loop
    MONITOR(["Main Monitoring Loop<br/>Continuous Operation"])
    CHECK_BUTTONS(["Check Button Presses<br/>User Input Detection"])
    BUTTON_PRESSED{{"Button Pressed?"}}

    %% Scheduling Process
    SCHEDULING_MODE(["Enter Scheduling Mode<br/>LCD Shows Menu"])
    SET_TIME(["Set Spray Time<br/>Use Buttons to Adjust"])
    CONFIRM_TIME(["Confirm Schedule<br/>Save to RTC"])
    SCHEDULED(["Schedule Set<br/>Return to Monitoring"])

    %% Time & Weather Check
    CHECK_TIME(["Check Current Time<br/>Compare with Schedule"])
    TIME_MATCH{{"Time to Spray?"}}
    CHECK_WEATHER(["Check Weather<br/>Rain Detection"])
    WEATHER_OK{{"Weather OK?"}}

    %% Spray Activation
    ACTIVATE_PUMPS(["Activate Pumps<br/>Relay Control"])
    SPRAYING_ACTIVE(["Spraying Active<br/>Monitor Levels"])
    CHECK_LEVELS(["Check Container Levels<br/>Ultrasonic Sensors"])
    LEVELS_OK{{"Levels Sufficient?"}}

    %% Feedback & Completion
    SUCCESS_FEEDBACK(["Success Feedback<br/>Buzzer & LED"])
    SPRAY_COMPLETE(["Spraying Complete<br/>Deactivate Pumps"])
    LOW_LEVEL_WARNING(["Low Level Warning<br/>Alert User"])

    %% Return to Monitoring
    RETURN_MONITOR(["Return to Monitoring<br/>Wait for Next Cycle"])

    %% Flow Connections
    START --> SETUP
    SETUP --> READY
    READY --> MONITOR
    MONITOR --> CHECK_BUTTONS
    CHECK_BUTTONS --> BUTTON_PRESSED

    BUTTON_PRESSED -->|No| MONITOR
    BUTTON_PRESSED -->|Yes| SCHEDULING_MODE

    SCHEDULING_MODE --> SET_TIME
    SET_TIME --> CONFIRM_TIME
    CONFIRM_TIME --> SCHEDULED
    SCHEDULED --> MONITOR

    MONITOR --> CHECK_TIME
    CHECK_TIME --> TIME_MATCH
    TIME_MATCH -->|No| MONITOR
    TIME_MATCH -->|Yes| CHECK_WEATHER

    CHECK_WEATHER --> WEATHER_OK
    WEATHER_OK -->|No| MONITOR
    WEATHER_OK -->|Yes| ACTIVATE_PUMPS

    ACTIVATE_PUMPS --> SPRAYING_ACTIVE
    SPRAYING_ACTIVE --> CHECK_LEVELS
    CHECK_LEVELS --> LEVELS_OK

    LEVELS_OK -->|Yes| SUCCESS_FEEDBACK
    LEVELS_OK -->|No| LOW_LEVEL_WARNING

    SUCCESS_FEEDBACK --> SPRAY_COMPLETE
    LOW_LEVEL_WARNING --> SPRAY_COMPLETE
    SPRAY_COMPLETE --> RETURN_MONITOR
    RETURN_MONITOR --> MONITOR

    %% Styling
    classDef setupClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1,font-weight:bold
    classDef processClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c,font-weight:bold
    classDef decisionClass fill:#fff8e1,stroke:#f57c00,stroke-width:3px,color:#e65100,font-weight:bold
    classDef actionClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20,font-weight:bold

    class START,SETUP,READY setupClass
    class MONITOR,CHECK_BUTTONS,SCHEDULING_MODE,SET_TIME,CONFIRM_TIME,SCHEDULED,CHECK_TIME,CHECK_WEATHER,ACTIVATE_PUMPS,SPRAYING_ACTIVE,CHECK_LEVELS,SUCCESS_FEEDBACK,SPRAY_COMPLETE,LOW_LEVEL_WARNING,RETURN_MONITOR processClass
    class BUTTON_PRESSED,TIME_MATCH,WEATHER_OK,LEVELS_OK decisionClass
    class SCHEDULED actionClass
```

## Flowchart Legend

### **System Startup (Blue)**
- ESP32 powers on and initializes all hardware components
- System becomes ready with active LCD display

### **Main Monitoring (Purple)**
- Continuous loop checking for user input and scheduled events
- Monitors time and weather conditions for spraying decisions

### **Scheduling Process (Purple)**
- User enters scheduling mode via button press
- Sets desired spray time using ESP32 buttons
- Confirms and saves schedule to RTC module

### **Automated Spraying (Purple)**
- System checks if scheduled time matches current time
- Verifies weather conditions before activation
- Activates pumps and monitors spraying process
- Provides feedback and handles completion

### **Decision Points (Orange)**
- Button press detection for user interaction
- Time matching for scheduled spraying
- Weather condition validation
- Container level monitoring

### **Key Features**
1. **Button-Based Scheduling**: Easy time setting using ESP32 buttons
2. **Weather-Aware Operation**: Automatic rain detection and postponement
3. **Level Monitoring**: Real-time container level checking during spraying
4. **User Feedback**: Audio-visual indicators for system status
5. **Automated Cycling**: Continuous monitoring and scheduled operation

This flowchart represents the complete operational process of the Smart-Sprayer system, from initial setup through automated spraying cycles, with user scheduling via ESP32 buttons as the primary interaction method.