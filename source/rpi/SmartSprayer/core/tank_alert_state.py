# tank_alert_state.py
# Shared module-level state for tank critical SMS alerts.
# Imported by dashboard (to set flags) and settings (to manually re-arm).
# Module-level globals are shared across all imports in the same process.

_tank1_sent = False
_tank2_sent = False


def is_sent(tank_num: int) -> bool:
    """Return True if the critical SMS for tank_num (1 or 2) has already been sent."""
    return _tank1_sent if tank_num == 1 else _tank2_sent


def set_sent(tank_num: int, value: bool = True) -> None:
    """Mark alert as sent (True) or clear it to allow re-arming (False)."""
    global _tank1_sent, _tank2_sent
    if tank_num == 1:
        _tank1_sent = value
    else:
        _tank2_sent = value


def reset(tank_num: int) -> None:
    """Re-arm the critical SMS for tank_num so it can fire again next time level drops critical."""
    set_sent(tank_num, False)
