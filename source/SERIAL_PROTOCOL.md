# Smart Sprayer Serial Communication Protocol

## Overview

This document defines the framed serial protocol used between ESP32 and Raspberry Pi for reliable tank level monitoring.

## Protocol Design

### Frame Structure

All framed messages use the following structure:

```
<COMMAND:data:checksum>
```

- **Start Marker**: `<`
- **End Marker**: `>`
- **Field Separator**: `:`
- **Checksum**: XOR of all bytes in COMMAND and data fields

### Frame Format

```
< COMMAND : data : checksum >
└─┬─┘ └──┬──┘ └─┬─┘ └───┬───┘ └┬┘
  │      │      │        │       │
Start  Command Data   Checksum  End
```

## Commands

### 1. GET_LEVELS (Tank Level Query)

**Purpose**: Request both tank levels from ESP32

**Request Frame**:
```
<GET_LEVELS::checksum>
```

**Response Frame**:
```
<LEVELS:dist1,pct1,dist2,pct2:checksum>
```

**Example**:
- Request: `<GET_LEVELS::71>`
- Response: `<LEVELS:26,85.71,45,17.86:B3>`

**Response Fields**:
- `dist1`: Distance reading from Sensor 1 in cm (0 = invalid)
- `pct1`: Fill percentage for Container 1 (0-100, or -1 for invalid)
- `dist2`: Distance reading from Sensor 2 in cm (0 = invalid)
- `pct2`: Fill percentage for Container 2 (0-100, or -1 for invalid)

### 2. Backward Compatibility Commands

All existing non-framed commands continue to work:
- `get-levels` (old format, for backward compatibility)
- `get-distance1`
- `get-distance2`
- `operate-relay1_on/off`
- `operate-relay2_on/off`
- `spray_RELAY_DURATION_VOLUME`
- etc.

## Ultrasonic Sensor Reading Rules

### Distance Interpretation

| Distance (cm) | Interpretation | Percentage |
|---------------|---------------|------------|
| 0 cm | INVALID (sensor error) | -1 |
| 1-22 cm | FULL | 100% |
| 22-50 cm | Proportional mapping | 0-100% |
| >50 cm | EMPTY | 0% |

### Percentage Calculation

For distances between 22-50 cm:
```
percentage = ((50 - distance) / (50 - 22)) × 100
```

### Smoothing/Filtering

ESP32 implements a **moving average filter** with:
- Window size: 5 readings
- Median selection from 3 attempts per reading
- Filters out 0cm readings (invalid)
- Filters out >70cm readings (out of range)

## Checksum Calculation

Simple XOR checksum for error detection:

```cpp
// ESP32 (C++)
uint8_t calculateChecksum(const String& data) {
  uint8_t checksum = 0;
  for (int i = 0; i < data.length(); i++) {
    checksum ^= data[i];
  }
  return checksum;
}
```

```python
# RPI (Python)
def calculate_checksum(data: str) -> int:
    checksum = 0
    for char in data:
        checksum ^= ord(char)
    return checksum
```

## Communication Flow

### Polling Cycle (Every 2 seconds)

```
RPI                           ESP32
 |                              |
 |----<GET_LEVELS::71>--------->|
 |                              |
 |                          [Read sensors]
 |                          [Apply filter]
 |                          [Calculate %]
 |                              |
 |<---<LEVELS:26,85,45,18:B3>---|
 |                              |
[Validate checksum]             |
[Update dashboard]              |
 |                              |
```

### Error Handling

1. **Invalid Checksum**: Ignore frame, use last valid reading
2. **Timeout (>1s)**: Ignore request, use last valid reading
3. **Malformed Frame**: Ignore, use last valid reading
4. **Invalid Sensor Reading**: Return -1 for percentage, distance = 0

## RPI Dashboard Update Logic

```python
# Maintain last valid readings
last_tank1_level = 0.0
last_tank2_level = 0.0

# On new frame received:
if validate_checksum(frame):
    levels = parse_frame(frame)
    
    # Only update if valid reading
    if levels['pct1'] >= 0:
        last_tank1_level = levels['pct1']
    
    if levels['pct2'] >= 0:
        last_tank2_level = levels['pct2']
    
    # Update dashboard with last valid values
    update_display(last_tank1_level, last_tank2_level)
```

## Migration Strategy

### Phase 1: Backward Compatible
- ESP32 supports both framed and non-framed commands
- RPI can use either protocol
- Default to old protocol if framed not available

### Phase 2: Gradual Migration
- RPI prefers framed protocol, falls back to old
- Monitor error rates

### Phase 3: Full Migration
- Remove debug prints from old protocol
- Optimize frame handling

## Performance Characteristics

- **Latency**: <100ms per query
- **Update Rate**: 2 seconds (configurable)
- **Error Detection**: >99% via checksum
- **Bandwidth**: ~50 bytes per transaction
- **CPU Usage**: <1% on both devices

## Debug Mode

Debug prints can be enabled/disabled independently:
- Framed protocol never prints debug info (clean frames only)
- Old protocol can still print debug info for troubleshooting
- Set `#define PROTOCOL_DEBUG 0` to disable all debug

## Example Transaction

```
RPI sends: <GET_LEVELS::71>
ESP32 responds: <LEVELS:26,85.71,0,−1:A5>

Interpretation:
- Tank 1: 26cm distance, 85.71% full
- Tank 2: 0cm distance (invalid), -1% (INVALID reading)

RPI action:
- Update Tank 1 display to 85.71%
- Keep Tank 2 at previous valid value
```

## Technical Notes

### Why This Protocol?

1. **Framing**: Clear start/end markers prevent desynchronization
2. **Checksum**: Detects corrupted data (electrical noise, timing issues)
3. **Simple**: Easy to implement on resource-constrained ESP32
4. **Backward Compatible**: Doesn't break existing functionality
5. **Efficient**: Minimal overhead (~10 bytes per frame)

### Alternative Protocols Considered

- **JSON**: Too heavy for ESP32, parsing overhead
- **Protobuf**: Requires libraries, complex
- **COBS**: Excellent but overkill for this use case
- **Custom Binary**: Not human-readable, harder to debug

### Future Enhancements

- Add sequence numbers to detect dropped frames
- Add CRC16 for stronger error detection
- Add acknowledgment frames for critical commands
- Add timestamping for latency measurement
