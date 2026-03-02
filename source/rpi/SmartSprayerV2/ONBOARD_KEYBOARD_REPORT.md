# Onboard Virtual Keyboard Integration Report
**Project:** SmartSprayerV2  
**Generated:** 2026-03-02  
**Purpose:** Identify all keyboard-interactive widgets and provide actionable guidance for implementing auto-show/hide Onboard virtual keyboard logic in fullscreen mode.

---

## Overview

| Screen | Input Widgets Found | Onboard Risk Level |
|---|---|---|
| Login (`run_gui.py – LoginScreen`) | 2 | 🔴 High – fullscreen CTk window |
| Mobile Number Setup (`run_gui.py – MobileNumberScreen`) | 1 | 🔴 High – fullscreen CTk window |
| Scheduling (`ui/scheduling.py`) | 5 | 🟠 Medium – embedded panel |
| Settings (`ui/settings.py`) | 3 active + 2 read-only | 🟠 Medium – scrollable panel |
| Account / Change Password (`ui/account.py`) | 3 | 🟠 Medium – embedded panel |
| Legacy Login (`ui/SmartSprayerUI.py`) | 3 | 🟡 Low – older screen |
| Logs Viewer (`ui/spraying_events_logs_viewer.py`) | 1 (read-only) | ⚪ None – display only |

---

## Detailed Widget Inventory

### 1. Login Screen — `run_gui.py` › `LoginScreen`

| # | Variable | Widget Type | Context | Input Type | Onboard Behavior |
|---|---|---|---|---|---|
| 1 | `self.user` | `CTkEntry` | Username field | Text (alphanumeric) | **Auto-show on `<FocusIn>`, hide on `<FocusOut>`** |
| 2 | `self.passw` | `CTkEntry` | Password field (`show="•"`) | Password (masked) | **Auto-show on `<FocusIn>`, hide on `<FocusOut>`** |

**⚠ Fullscreen Risk:** `LoginScreen` is a `ctk.CTk()` window with `-fullscreen True`. Onboard **does not auto-raise** over fullscreen windows by default. Must call `subprocess.Popen(["onboard"])` explicitly on focus and `subprocess.run(["pkill", "onboard"])` on destroy/submit.

---

### 2. Mobile Number Setup Screen — `run_gui.py` › `MobileNumberScreen`

| # | Variable | Widget Type | Context | Input Type | Onboard Behavior |
|---|---|---|---|---|---|
| 3 | `self.phone_entry` | `CTkEntry` | 10-digit phone number | Numeric only | **Auto-show on `<FocusIn>`, numeric layout preferred** |

**⚠ Fullscreen Risk:** Same as LoginScreen — standalone `ctk.CTk()` fullscreen window.

---

### 3. Scheduling Panel — `ui/scheduling.py` › `SchedulingPanel`

| # | Variable | Widget Type | Context | Input Type | Onboard Behavior |
|---|---|---|---|---|---|
| 4 | `self.vol_entry` | `CTkEntry` | Volume (mL) input in new schedule form | Numeric | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| 5 | `self.interval_entry` | `CTkEntry` | Recurring interval in days (e.g. `7`) | Numeric | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| 6 | `self.count_entry` | `CTkEntry` | Recurring count (e.g. `4`) | Numeric | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| 7 | `new_vol_entry` *(local var)* | `CTkEntry` | Volume field inside **Edit Schedule** modal/row | Numeric | Auto-show on `<FocusIn>` – note: local var, bind at creation time |
| 8 | ComboBox (time pickers) | `CTkComboBox` | Hour / Minute selectors (`state="readonly"`) | Dropdown only | ⚪ No keyboard needed – read-only dropdown |

**Note on `new_vol_entry`:** This is a local variable created dynamically inside a function (around line 909). The `<FocusIn>` binding must be applied immediately after widget creation since there is no `self.*` reference.

---

### 4. Settings Panel — `ui/settings.py` › `SettingsFrame`

| # | Variable | Widget Type | Context | Input Type | Onboard Behavior |
|---|---|---|---|---|---|
| 9 | `self.phone_entry` | `CTkEntry` | SMS recipient phone number | Numeric (validated) | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| 10 | `self.name_entry` | `CTkEntry` | SMS recipient name | Text (optional) | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| 11 | `self._wifi_pw_entry` | `CTkEntry` | WiFi password (`show="●"`) | Password (masked) | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| — | `prefix` *(local)* | `CTkEntry` | `+63` prefix – **disabled** | Read-only | ⚪ Skip – `state="disabled"` |
| — | `self.muni` | `CTkComboBox` | Municipality selector | Dropdown only | ⚪ No keyboard needed – read-only dropdown |
| — | `self.brgy` | `CTkComboBox` | Barangay selector | Dropdown only | ⚪ No keyboard needed – read-only dropdown |
| — | `self._wifi_ssid_menu` | `CTkComboBox` | WiFi SSID selector | Dropdown only | ⚪ No keyboard needed – read-only dropdown |

---

### 5. Account / Change Password — `ui/account.py` › `SprayerAccountPanel`

| # | Variable | Widget Type | Context | Input Type | Onboard Behavior |
|---|---|---|---|---|---|
| 12 | `self.current_pass` | `CTkEntry` | Current password (`show="•"`) | Password (masked) | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| 13 | `self.new_pass` | `CTkEntry` | New password (`show="•"`) | Password (masked) | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |
| 14 | `self.confirm_pass` | `CTkEntry` | Confirm password (`show="•"`) | Password (masked) | Auto-show on `<FocusIn>`, hide on `<FocusOut>` |

*All three are created via `_password_field()` helper at lines ~230–240 of `account.py`.*

---

### 6. Legacy Login Screen — `ui/SmartSprayerUI.py`

| # | Variable | Widget Type | Context | Input Type | Onboard Behavior |
|---|---|---|---|---|---|
| 15 | `self.user_entry` | `CTkEntry` | Username | Text | Auto-show on `<FocusIn>` |
| 16 | `self.pass_entry` | `CTkEntry` | Password (`show="*"`) | Password | Auto-show on `<FocusIn>` |
| 17 | `self.mobile_entry` | `CTkEntry` | Mobile number | Numeric | Auto-show on `<FocusIn>` |

**Note:** This screen appears to be a legacy/alternate entry point. If still in use, apply the same fullscreen Onboard strategy as `run_gui.py`.

---

### 7. Logs Viewer — `ui/spraying_events_logs_viewer.py`

| # | Variable | Widget Type | Context | Input Type | Onboard Behavior |
|---|---|---|---|---|---|
| — | `self.log_textbox` | `CTkTextbox` | Log display area | **Read-only display** | ⚪ Skip – set `state="disabled"` to prevent cursor focus |

---

## Fullscreen Onboard Problem — Root Cause

By default, Onboard cannot float above a fullscreen Tkinter/CTk window because:
1. The fullscreen window grabs the entire display layer.
2. Onboard's `--not-docked` mode is blocked by the window manager.

### Recommended Fix

Use **`onboard --layout=Phone`** (or compact layout) launched via subprocess, combined with the main window being set to a **maximized window** (not true fullscreen):

```python
# Instead of:
self.attributes("-fullscreen", True)

# Use:
self.state("zoomed")          # Windows
# or
self.attributes("-zoomed", True)  # Linux/RPi
```

If true fullscreen is required, use this approach:

```python
import subprocess
import os

_onboard_proc = None

def show_keyboard():
    global _onboard_proc
    if _onboard_proc is None or _onboard_proc.poll() is not None:
        _onboard_proc = subprocess.Popen(
            ["onboard", "--size=800x300", "--layout=Phone", "--theme=Nightshade"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def hide_keyboard():
    global _onboard_proc
    if _onboard_proc and _onboard_proc.poll() is None:
        _onboard_proc.terminate()
        _onboard_proc = None
```

---

## Reusable Binding Helper

Add this function to a shared utility module (e.g., `ui/__init__.py` or a new `ui/keyboard_utils.py`):

```python
# ui/keyboard_utils.py

import subprocess

_onboard_proc = None

def show_keyboard():
    """Launch Onboard virtual keyboard if not already running."""
    global _onboard_proc
    if _onboard_proc is None or _onboard_proc.poll() is not None:
        _onboard_proc = subprocess.Popen(
            ["onboard", "--size=800x280", "--layout=Phone"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def hide_keyboard():
    """Terminate Onboard virtual keyboard."""
    global _onboard_proc
    if _onboard_proc and _onboard_proc.poll() is None:
        _onboard_proc.terminate()
        _onboard_proc = None

def bind_keyboard(widget):
    """
    Bind Onboard show/hide to any CTkEntry or CTkTextbox widget.
    Call this once after widget creation.

    Usage:
        bind_keyboard(self.phone_entry)
        bind_keyboard(self.passw)
    """
    # CTkEntry wraps an internal tk.Entry — bind on the inner widget
    inner = getattr(widget, "_entry", None) or widget
    inner.bind("<FocusIn>",  lambda e: show_keyboard(), add="+")
    inner.bind("<FocusOut>", lambda e: hide_keyboard(), add="+")
```

---

## Implementation Checklist

### `run_gui.py`
- [ ] Import `bind_keyboard` from `ui.keyboard_utils`
- [ ] `bind_keyboard(self.user)` in `LoginScreen.__init__`
- [ ] `bind_keyboard(self.passw)` in `LoginScreen.__init__`
- [ ] `bind_keyboard(self.phone_entry)` in `MobileNumberScreen.__init__`
- [ ] Call `hide_keyboard()` in `login()` and `submit()` methods before destroy
- [ ] Replace `-fullscreen True` with `state("zoomed")` OR ensure Onboard uses `--not-docked` mode

### `ui/scheduling.py`
- [ ] Import `bind_keyboard`
- [ ] `bind_keyboard(self.vol_entry)` after creation
- [ ] `bind_keyboard(self.interval_entry)` after creation
- [ ] `bind_keyboard(self.count_entry)` after creation
- [ ] `bind_keyboard(new_vol_entry)` immediately after creation in the edit helper

### `ui/settings.py`
- [ ] Import `bind_keyboard`
- [ ] `bind_keyboard(self.phone_entry)` in `create_sms_card()`
- [ ] `bind_keyboard(self.name_entry)` in `create_sms_card()`
- [ ] `bind_keyboard(self._wifi_pw_entry)` in `create_wifi_card()`

### `ui/account.py`
- [ ] Import `bind_keyboard`
- [ ] `bind_keyboard(self.current_pass)` after `_password_field()` call
- [ ] `bind_keyboard(self.new_pass)` after `_password_field()` call
- [ ] `bind_keyboard(self.confirm_pass)` after `_password_field()` call

### `ui/SmartSprayerUI.py` (legacy)
- [ ] Import `bind_keyboard`
- [ ] `bind_keyboard(self.user_entry)`
- [ ] `bind_keyboard(self.pass_entry)`
- [ ] `bind_keyboard(self.mobile_entry)`

### Global
- [ ] Create `ui/keyboard_utils.py` with the helper above
- [ ] Consider calling `hide_keyboard()` from `SmartSprayerUI._on_closing()`
- [ ] Test Onboard visibility with `--not-docked` and/or switch from `-fullscreen` to `state("zoomed")`

---

## Summary by Priority

| Priority | File | Action |
|---|---|---|
| 🔴 Critical | `run_gui.py` | Fullscreen blocks Onboard — switch to `zoomed` + bind all 3 entries |
| 🔴 Critical | `run_gui.py` | Call `hide_keyboard()` on login/submit/screen switch |
| 🟠 High | `ui/settings.py` | Bind `phone_entry`, `name_entry`, `_wifi_pw_entry` |
| 🟠 High | `ui/scheduling.py` | Bind `vol_entry`, `interval_entry`, `count_entry`, `new_vol_entry` |
| 🟠 High | `ui/account.py` | Bind `current_pass`, `new_pass`, `confirm_pass` |
| 🟡 Medium | `ui/SmartSprayerUI.py` | Bind if this screen is still live |
| ⚪ None | `ui/spraying_events_logs_viewer.py` | Disable `log_textbox` to prevent accidental keyboard focus |
