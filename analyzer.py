"""
╔══════════════════════════════════════════════════════════════════╗
║         KEYSTROKE ANALYZER — Pattern & Statistics Engine         ║
╚══════════════════════════════════════════════════════════════════╝
Standalone analytics module. Run directly or import into server.py.
"""
import os
import json
from collections import Counter
from datetime import datetime
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR   = os.path.join(BASE_DIR, "logs")
JSON_FILE = os.path.join(LOG_DIR, "keystrokes.json")
def load_records():
    """Load all records from the JSON log."""
    if not os.path.exists(JSON_FILE):
        print("[!] No keystroke log found. Start the keylogger first.")
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
def frequency_analysis(records):
    """Most frequently pressed keys."""
    keys = [r.get("display", "?") for r in records]
    return Counter(keys).most_common(20)
def session_summary(records):
    """High-level session statistics."""
    if not records:
        return {}
    total = len(records)
    special = sum(1 for r in records if r.get("type") == "special")
    regular = total - special
    backspaces = sum(1 for r in records if r.get("is_backspace"))
    timestamps = [r["timestamp"] for r in records if "timestamp" in r]
    start = timestamps[0] if timestamps else "N/A"
    end   = timestamps[-1] if timestamps else "N/A"
    return {
        "total_keystrokes": total,
        "regular_keys": regular,
        "special_keys": special,
        "backspaces": backspaces,
        "session_start": start,
        "session_end": end,
        "accuracy_estimate": round((1 - backspaces / max(regular, 1)) * 100, 2),
    }
def bigram_analysis(records):
    """Most common two-key sequences (bigrams)."""
    regular = [r for r in records if r.get("type") == "regular"]
    keys = [r.get("key", "") for r in regular if len(r.get("key", "")) == 1]
    bigrams = [keys[i] + keys[i+1] for i in range(len(keys)-1)]
    return Counter(bigrams).most_common(10)
def hourly_heatmap(records):
    """Count keystrokes per hour of day."""
    hourly = {str(h).zfill(2): 0 for h in range(24)}
    for r in records:
        try:
            hour = r["timestamp"].split(" ")[1].split(":")[0]
            hourly[hour] += 1
        except (KeyError, IndexError):
            pass
    return hourly
def print_report():
    """Pretty-print an analysis report to console."""
    records = load_records()
    if not records:
        return
    print("\n" + "═" * 60)
    print("  📊 KEYSTROKE ANALYSIS REPORT")
    print("═" * 60)
    summary = session_summary(records)
    for k, v in summary.items():
        print(f"  {k:<25} : {v}")
    print("\n  🔑 TOP 10 KEYS:")
    for key, count in frequency_analysis(records)[:10]:
        bar = "█" * min(count, 40)
        print(f"  {key:<10} {bar} ({count})")
    print("\n  🔗 TOP 5 BIGRAMS:")
    for bigram, count in bigram_analysis(records)[:5]:
        print(f"  '{bigram}' × {count}")
    print("\n  🕐 HOURLY HEATMAP:")
    hourly = hourly_heatmap(records)
    for hour, count in hourly.items():
        bar = "▓" * min(count, 50)
        if count:
            print(f"  {hour}:00  {bar} ({count})")
    print("═" * 60 + "\n")
if __name__ == "__main__":
    print_report()
