# 🕉️ कर्म प्रधान — Karma-Driven Productivity Dashboard

> **"कर्म प्रधान विश्व रचि राखा, जो जस करहि सो तस फल चाखा"**
> *As you sow, so shall you reap.*

A full-featured, dark-themed Streamlit productivity dashboard for students and professionals.

---

## ✨ Features

| Section | What it does |
|---|---|
| **Today's Tasks** | Add tasks with priority, time estimates, progress sliders, actual time input |
| **Weekly Summary** | Bar + line charts for 7-day completion, streak heatmap |
| **Monthly Tracker** | Calendar heatmap, daily done vs total, 6-month trend |
| **Flexibility & Recovery** | Log plan failures, view plan-vs-actual, flexibility rules |
| **Long-Term Goals** | Add/track goals, radar chart, strategy bridge |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the dashboard
```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 🗄️ Data Storage
- All data is stored in a local **SQLite database** (`karma_dashboard.db`)
- Auto-created on first run in the same folder
- Demo data is seeded automatically for the first 2 weeks
- No internet required after install

---

## 📁 File Structure
```
karma_dashboard/
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
└── karma_dashboard.db      ← SQLite DB (auto-created on first run)
```

---

## 🎨 Design Notes
- **Dark theme** — professional navy/black palette
- **Color-coded priorities**: 🔴 Red (High), 🟡 Amber (Medium), 🔵 Blue (Low), 🟢 Teal (Balance)
- **Responsive** — works on laptop and wide screens
- **Live updates** — all charts update as you enter data

---

## 🔧 Customization Tips

| Want to change | Edit in `app.py` |
|---|---|
| Work capacity (default 8h) | `WORK_CAPACITY = 480` |
| Demo data | `seed_demo_data()` function |
| Color scheme | `HIGH_COL`, `MED_COL`, `LOW_COL` constants |
| DB location | `DB_PATH = "karma_dashboard.db"` |
