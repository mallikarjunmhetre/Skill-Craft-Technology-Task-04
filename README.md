# Skill-Craft-Technology-Task-04
Skill Craft Technology Cyber Security Internship Projects.
# 🔐 KeyLogger Cybersecurity Dashboard

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Cybersecurity](https://img.shields.io/badge/Cybersecurity-Educational-00d4ff?style=for-the-badge&logo=hackthebox&logoColor=white)

**An educational keystroke monitoring tool with a real-time cybersecurity dashboard.**
*Built for security research, ethical hacking education, and system monitoring.*

> ⚠️ **ETHICAL USE ONLY** — This tool is for educational and authorized system monitoring only.
> Unauthorized keylogging is **illegal** under computer fraud laws worldwide.

</div>

---

## 📸 Dashboard Preview

```
┌─────────────────────────────────────────────────────────────────┐
│  🔐 KeyLogger   │  Dashboard Overview              21:30:00     │
│  CYBER DASHBOARD│─────────────────────────────────────────────  │
│                 │                                               │
│  ▶ Dashboard    │  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  ▶ Live Monitor │  │ 1,284    │ │ 1,102    │ │   182    │     │
│  ▶ Analytics    │  │ Total    │ │ Regular  │ │ Special  │     │
│  ▶ Reports      │  └──────────┘ └──────────┘ └──────────┘     │
│                 │                                               │
│  ⚙ Clear Logs  │  [Donut Chart]     [Top Keys Progress Bars]  │
│                 │                                               │
│  v1.0.0         │  [Live Terminal Feed]   [Session Info]       │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## 🗺️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                            │
│                (Keyboard / Mouse Events)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PYTHON BACKEND                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ keylogger.py│───▶│ analyzer.py │    │     server.py       │ │
│  │  (pynput)   │    │ (analytics) │    │   (Flask REST API)  │ │
│  └──────┬──────┘    └─────────────┘    └──────────┬──────────┘ │
│         │                                          │            │
│         ▼                                          │            │
│  ┌──────────────────────────────────────────────┐  │            │
│  │              LOGS/ DIRECTORY                 │  │            │
│  │  keystrokes.log  │  keystrokes.json  │ state │◀─┘            │
│  └──────────────────────────────────────────────┘              │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP REST API (port 5000)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND DASHBOARD                            │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  index.html    │  │  monitor.html  │  │ analytics.html   │  │
│  │  Dashboard     │  │  Live Monitor  │  │ Charts & Stats   │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│  ┌────────────────┐  ┌────────────────────────────────────────┐ │
│  │  reports.html  │  │         js/ + css/                     │ │
│  │  Export & Logs │  │  main.js │ dashboard.js │ monitor.js   │ │
│  └────────────────┘  │  analytics.js │ reports.js             │ │
│                       └────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Keystroke Capture** | `pynput` | Cross-platform keyboard listener |
| **Backend** | `Python 3.8+` | Core application runtime |
| **API Server** | `Flask 3.0` | REST API serving data to frontend |
| **CORS** | `Flask-CORS` | Cross-origin resource sharing |
| **Frontend** | `HTML5` | Semantic page structure |
| **Styling** | `Vanilla CSS3` | Dark cyberpunk theme, glassmorphism |
| **Logic** | `Vanilla JavaScript ES6+` | No framework, pure JS |
| **Charts** | `Chart.js 4.4` | Bar, Doughnut, Line charts |
| **Icons** | `Font Awesome 6.5` | UI icons |
| **Fonts** | `Google Fonts` | Space Grotesk + JetBrains Mono |
| **Animation** | `CSS Keyframes` | Matrix rain, neon glows, micro-animations |
| **Data Storage** | `JSON + Plain Text` | Structured and human-readable logs |

---

## 📁 Project Structure

```
keylogger-cybersecurity/
│
├── 📂 backend/
│   ├── 🐍 keylogger.py          # Core keylogger engine (pynput listener)
│   ├── 🐍 server.py             # Flask REST API server
│   ├── 🐍 analyzer.py           # Keystroke analytics (frequency, bigrams)
│   └── 📄 requirements.txt      # Python dependencies
│
├── 📂 frontend/
│   ├── 🌐 index.html            # Page 1: Dashboard Overview
│   ├── 🌐 monitor.html          # Page 2: Live Terminal Monitor
│   ├── 🌐 analytics.html        # Page 3: Analytics & Charts
│   ├── 🌐 reports.html          # Page 4: Reports & Log Export
│   │
│   ├── 📂 css/
│   │   ├── 🎨 main.css          # Global dark cyber theme + components
│   │   └── 🎨 animations.css    # Keyframes, matrix rain, micro-animations
│   │
│   └── 📂 js/
│       ├── ⚡ main.js           # Shared: clock, API helpers, toast, matrix rain
│       ├── ⚡ dashboard.js      # Dashboard charts, stat counters, live feed
│       ├── ⚡ monitor.js        # Live feed, key bubbles, KPM meter
│       ├── ⚡ analytics.js      # Chart.js charts, keyboard heatmap
│       └── ⚡ reports.js        # Table, search/filter, JSON/CSV/TXT export
│
├── 📂 logs/
│   ├── 📝 keystrokes.log        # Plain text log (auto-created)
│   ├── 📊 keystrokes.json       # Structured JSON log (auto-created)
│   └── 🔧 state.json            # Session state (auto-created)
│
├── 📄 README.md                 # This file
└── 📄 LICENSE                   # MIT License
```

---

## ✨ Key Features

### 🎯 Core Keylogger Engine
- Real-time keystroke capture using `pynput`
- Detects **regular** keys (a-z, 0-9, symbols) and **special** keys (Enter, Ctrl, Alt, Shift, etc.)
- Backspace tracking for accuracy estimation
- Dual logging: **plain text** and **structured JSON**
- Thread-safe session state management

### 📡 Flask REST API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Session status and counters |
| `/api/start` | POST | Start keylogger in background thread |
| `/api/stop` | POST | Send stop signal |
| `/api/live` | GET | Last N keystrokes from memory |
| `/api/keystrokes` | GET | Paginated full keystroke log |
| `/api/analytics` | GET | Computed stats, top keys, hourly data |
| `/api/logs/text` | GET | Plain text log lines |
| `/api/logs/export` | GET | Full JSON export |
| `/api/clear` | DELETE | Clear all log files |

### 🖥️ 4-Page Web Dashboard

| Page | File | Features |
|------|------|---------|
| **Dashboard** | `index.html` | Hero banner, 4 stat cards, donut chart, top keys, live feed preview, session info |
| **Live Monitor** | `monitor.html` | Real-time terminal, last key display, key bubbles, KPM meter, pause/filter |
| **Analytics** | `analytics.html` | Bar chart, doughnut, hourly heatmap, keyboard frequency map, detail bars |
| **Reports** | `reports.html` | JSON/CSV/TXT export, filterable table, pagination, search, danger zone |

### 🎨 Design Highlights
- **Dark Cyberpunk Theme** — Deep navy + neon cyan color palette
- **Matrix Rain** — Animated canvas background on all pages
- **Glassmorphism** — Frosted glass cards with backdrop blur
- **Neon Glow** — Text-shadow and box-shadow neon effects
- **Micro-animations** — Fade-in-up stagger, progress bar fills, scan lines
- **JetBrains Mono** — Monospace font throughout terminal elements

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/keylogger-cybersecurity.git
cd keylogger-cybersecurity
```

### 2. Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Start the Flask Server
```bash
python backend/server.py
```
Server runs on **http://localhost:5000**

### 4. Open the Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

### 5. Start the Keylogger
- Click **"Start Logger"** on the dashboard, OR
- Run standalone: `python backend/keylogger.py`
- Press **ESC** to stop the keylogger

---

## 📊 Usage Guide

### Dashboard (index.html)
- View total/regular/special/backspace counts
- See live keystroke preview in the terminal widget
- Monitor key type distribution in the donut chart

### Live Monitor (monitor.html)
- Watch keystrokes appear in real-time terminal
- See **last pressed key** highlighted large
- View animated **key bubbles** queue
- Track **keystrokes per minute (KPM)**
- Use **Pause** to freeze the feed, **Filter** to show only regular or special keys

### Analytics (analytics.html)
- **Top 15 Keys** — horizontal bar chart ranked by frequency
- **Key Type Breakdown** — doughnut with regular vs special percentage
- **Hourly Heatmap** — bar chart showing activity per hour
- **Keyboard Heatmap** — visual QWERTY layout colored by usage intensity
- **Frequency Details** — progress bars for top 20 keys with percentage share

### Reports (reports.html)
- **Export JSON** — complete structured records
- **Export CSV** — open in Excel / Google Sheets
- **Export TXT** — human-readable timestamped log
- **Search** by key character, filter by type, configure page size
- **Paginated table** with all keystroke records
- **Danger Zone** — permanently clear all logs

---

## 🔧 Standalone Analyzer

Run analytics directly from the command line:
```bash
python backend/analyzer.py
```

Output example:
```
════════════════════════════════════════════════════════════
  📊 KEYSTROKE ANALYSIS REPORT
════════════════════════════════════════════════════════════
  total_keystrokes          : 1,284
  regular_keys              : 1,102
  special_keys              : 182
  backspaces                : 23
  accuracy_estimate         : 97.91%
  session_start             : 2024-01-15 09:30:12.445
  session_end               : 2024-01-15 10:12:08.881

  🔑 TOP 10 KEYS:
  e          ████████████████████ (156)
  t          ████████████████ (128)
  [SPACE]    ███████████████ (120)
  a          ████████████ (98)
  ...
```

---

## 🔒 Cybersecurity Notes

### How It Works
1. `pynput.keyboard.Listener` hooks into the OS keyboard events
2. Each keypress fires the `on_press()` callback
3. The key is classified as **regular** or **special**
4. The record is written to `keystrokes.log` (plain text) and `keystrokes.json` (structured)
5. Flask API reads these files and serves data to the frontend dashboard

### Ethical Use Cases
- ✅ Parental monitoring (on your own devices/household)
- ✅ Employee monitoring (with written consent)
- ✅ Cybersecurity education and CTF challenges
- ✅ Typing speed/accuracy personal analysis
- ✅ Research into human-computer interaction

### Illegal Uses (Do NOT)
- ❌ Monitoring anyone without explicit consent
- ❌ Installing on devices you don't own
- ❌ Capturing credentials or personal data maliciously
- ❌ Selling or distributing captured data

---

## 📦 Dependencies

```
pynput==1.7.6       # Cross-platform keyboard/mouse monitoring
flask==3.0.0        # Lightweight Python web framework
flask-cors==4.0.0   # CORS headers for frontend API calls
```

Frontend CDN dependencies (no install needed):
- [Chart.js 4.4](https://www.chartjs.org/) — Data visualization
- [Font Awesome 6.5](https://fontawesome.com/) — Icons
- [Google Fonts](https://fonts.google.com/) — Space Grotesk + JetBrains Mono

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [pynput](https://pynput.readthedocs.io/) — Keyboard event monitoring library
- [Flask](https://flask.palletsprojects.com/) — Python micro web framework
- [Chart.js](https://www.chartjs.org/) — Beautiful and responsive charts
- [Font Awesome](https://fontawesome.com/) — Icon library

---

<div align="center">

**Made with ❤️ for Cybersecurity Education**

*If you found this useful, please ⭐ star the repository!*

</div>
