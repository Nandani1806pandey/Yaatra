"""
कर्म प्रधान विश्व रचि राखा, जो जस करहि सो तस फल चाखा
Karma-Driven Productivity Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3
import json
from datetime import datetime, date, timedelta
import random
import os

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="कर्म प्रधान Dashboard",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL STYLES ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default streamlit menu/footer */
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 1400px; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 20px;
    border: 1px solid #dc2626;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '🕉';
    position: absolute;
    right: 30px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 72px;
    opacity: 0.12;
}
.hero-quote {
    font-family: 'Noto Sans Devanagari', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #f5c518;
    margin: 0 0 6px 0;
    text-shadow: 0 0 20px rgba(245,197,24,0.4);
    letter-spacing: 0.5px;
}
.hero-sub {
    font-size: 13px;
    color: #a8b2d8;
    margin: 0 0 12px 0;
    font-style: italic;
}
.hero-meta {
    display: flex;
    gap: 20px;
    margin-top: 8px;
}
.hero-pill {
    background: rgba(220,38,38,0.2);
    border: 1px solid rgba(220,38,38,0.4);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #dc2626;
    font-weight: 500;
}

/* Metric cards */
.metric-card {
    background: #16213e;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #1a3358;
    text-align: center;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-val { font-size: 28px; font-weight: 700; margin: 4px 0; }
.metric-label { font-size: 11px; color: #8892b0; text-transform: uppercase; letter-spacing: 0.8px; }
.metric-green { color: #64ffda; }
.metric-red { color: #ef4444; }
.metric-amber { color: #ffd700; }
.metric-blue { color: #57cbff; }

/* Priority containers */
.priority-high {
    background: linear-gradient(135deg, #2d0a0a, #1a0505);
    border: 1px solid #7f1d1d;
    border-left: 4px solid #dc2626;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.priority-med {
    background: linear-gradient(135deg, #2d2000, #1a1400);
    border: 1px solid #8b6914;
    border-left: 4px solid #ffd700;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.priority-low {
    background: linear-gradient(135deg, #0a1a2d, #0a1020);
    border: 1px solid #0a4d8b;
    border-left: 4px solid #57cbff;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.priority-ent {
    background: linear-gradient(135deg, #0a2d1a, #071a0f);
    border: 1px solid #0a6b3a;
    border-left: 4px solid #64ffda;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

.task-name { font-size: 15px; font-weight: 600; color: #ccd6f6; }
.task-meta { font-size: 12px; color: #8892b0; margin-top: 3px; }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
}
.badge-high { background: rgba(220,38,38,0.2); color: #dc2626; border: 1px solid rgba(220,38,38,0.3); }
.badge-med  { background: rgba(255,215,0,0.15); color: #ffd700; border: 1px solid rgba(255,215,0,0.3); }
.badge-low  { background: rgba(87,203,255,0.15); color: #57cbff; border: 1px solid rgba(87,203,255,0.3); }
.badge-done { background: rgba(100,255,218,0.15); color: #64ffda; border: 1px solid rgba(100,255,218,0.3); }

/* Section headers */
.section-header {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8892b0;
    border-bottom: 1px solid #1a3358;
    padding-bottom: 8px;
    margin-bottom: 12px;
}

/* Sidebar */
.css-1d391kg { background: #0d1117 !important; }

/* Progress bar custom */
.prog-wrap { background: #1a3358; border-radius: 4px; height: 8px; overflow: hidden; }
.prog-fill-high { background: linear-gradient(90deg, #dc2626, #ef4444); height: 100%; border-radius: 4px; }
.prog-fill-med  { background: linear-gradient(90deg, #ffd700, #ffaa00); height: 100%; border-radius: 4px; }
.prog-fill-low  { background: linear-gradient(90deg, #57cbff, #0099cc); height: 100%; border-radius: 4px; }
.prog-fill-done { background: linear-gradient(90deg, #64ffda, #00cc88); height: 100%; border-radius: 4px; }

/* Flexibility log */
.flex-note {
    background: #101828;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: #a8b2d8;
    margin-bottom: 8px;
}

/* Long-term goal card */
.goal-card {
    background: #101828;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.goal-title { font-size: 15px; font-weight: 600; color: #ccd6f6; }
.goal-deadline { font-size: 12px; color: #8892b0; }

/* Heatmap label */
.heatmap-label { font-size: 12px; color: #8892b0; text-align: center; margin-top: 4px; }

/* Streaks */
.streak-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px; height: 32px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px;
}
.streak-done { background: #064e3b; color: #64ffda; border: 1px solid #065f46; }
.streak-miss { background: #1a1f2e; color: #4a5568; border: 1px solid #2d3748; }
.streak-today { background: #1d4ed8; color: #bfdbfe; border: 1px solid #2563eb; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #101828;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: #8892b0;
}
.stTabs [aria-selected="true"] {
    background: #1d4ed8 !important;
    color: white !important;
}

/* Phase 2: Mission & Motivation Styles */
.mission-card {
    background: linear-gradient(135deg, #0d1b2a 0%, #16213e 50%, #0d1117 100%);
    border: 1px solid #1a3358;
    border-left: 4px solid #f5c518;
    border-radius: 12px;
    padding: 22px 26px;
    margin-bottom: 16px;
    position: relative;
}
.mission-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #f5c518;
    margin-bottom: 6px;
}
.mission-statement {
    font-size: 18px;
    font-weight: 600;
    color: #f8fafc;
    line-height: 1.5;
}
.intention-box {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-left: 4px solid #64ffda;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
}
.pillar-card {
    background: #101828;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
}
.pillar-header {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 8px;
}
.affirmation-pill {
    background: rgba(245, 197, 24, 0.08);
    border: 1px solid rgba(245, 197, 24, 0.25);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #cbd5e1;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─── DATABASE SETUP ───────────────────────────────────────────────────────────
DB_PATH = "karma_dashboard.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            name        TEXT NOT NULL,
            priority    TEXT NOT NULL,
            est_mins    REAL DEFAULT 0,
            actual_mins REAL DEFAULT 0,
            pct_done    REAL DEFAULT 0,
            completed   INTEGER DEFAULT 0,
            category    TEXT DEFAULT 'work',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS daily_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT UNIQUE NOT NULL,
            total_tasks INTEGER DEFAULT 0,
            done_tasks  INTEGER DEFAULT 0,
            avg_pct     REAL DEFAULT 0,
            mood        TEXT DEFAULT 'neutral',
            notes       TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS long_term_goals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            deadline    TEXT,
            progress    REAL DEFAULT 0,
            category    TEXT DEFAULT 'career',
            description TEXT DEFAULT '',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS flex_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            what_failed TEXT,
            why_failed  TEXT,
            reallocation TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS mission_profile (
            id                      INTEGER PRIMARY KEY CHECK (id = 1),
            life_mission            TEXT DEFAULT '',
            career_aspirations      TEXT DEFAULT '',
            learning_goals          TEXT DEFAULT '',
            personal_growth         TEXT DEFAULT '',
            identity_statement      TEXT DEFAULT '',
            why_it_matters          TEXT DEFAULT '',
            what_it_enables         TEXT DEFAULT '',
            target_outcome          TEXT DEFAULT '',
            target_date             TEXT DEFAULT '',
            motivational_statements TEXT DEFAULT '[]',
            show_sanskrit_motto     INTEGER DEFAULT 1,
            quote_rotation_mode     TEXT DEFAULT 'daily',
            updated_at              TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS daily_intentions (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            date                    TEXT UNIQUE NOT NULL,
            intention               TEXT NOT NULL,
            top_priority_task_id    INTEGER,
            why_today_matters       TEXT DEFAULT '',
            energy_level            INTEGER DEFAULT 3,
            created_at              TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS goal_milestones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id     INTEGER NOT NULL,
            title       TEXT NOT NULL,
            target_date TEXT,
            completed   INTEGER DEFAULT 0,
            weight      REAL DEFAULT 1.0,
            notes       TEXT DEFAULT '',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(goal_id) REFERENCES long_term_goals(id) ON DELETE CASCADE
        );
    """)

    # Non-destructive migrations for existing long_term_goals table
    c_goals = [col[1] for col in c.execute("PRAGMA table_info(long_term_goals)").fetchall()]
    for col_name, col_type in [
        ("motivation", "TEXT DEFAULT ''"),
        ("start_date", "TEXT DEFAULT ''"),
        ("desired_outcome", "TEXT DEFAULT ''"),
        ("success_criteria", "TEXT DEFAULT ''"),
        ("status", "TEXT DEFAULT 'active'"),
        ("blockers", "TEXT DEFAULT ''"),
        ("next_action", "TEXT DEFAULT ''"),
        ("review_frequency", "TEXT DEFAULT 'weekly'")
    ]:
        if col_name not in c_goals:
            c.execute(f"ALTER TABLE long_term_goals ADD COLUMN {col_name} {col_type}")

    # Non-destructive migrations for existing tasks table
    c_tasks = [col[1] for col in c.execute("PRAGMA table_info(tasks)").fetchall()]
    for col_name, col_type in [
        ("goal_id", "INTEGER DEFAULT NULL"),
        ("milestone_id", "INTEGER DEFAULT NULL"),
        ("blockers", "TEXT DEFAULT ''")
    ]:
        if col_name not in c_tasks:
            c.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()

init_db()

# ─── DB HELPERS ──────────────────────────────────────────────────────────────
def get_tasks(for_date=None):
    if for_date is None:
        for_date = date.today().isoformat()
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM tasks WHERE date=? ORDER BY priority, id", conn, params=(for_date,))
    conn.close()
    return df

def add_task(name, priority, est_mins, category="work", for_date=None, goal_id=None, milestone_id=None, blockers=""):
    if for_date is None:
        for_date = date.today().isoformat()
    conn = get_conn()
    conn.execute("INSERT INTO tasks (date,name,priority,est_mins,category,goal_id,milestone_id,blockers) VALUES (?,?,?,?,?,?,?,?)",
                 (for_date, name, priority, est_mins, category, goal_id, milestone_id, blockers))
    conn.commit()
    conn.close()

def update_task(task_id, actual_mins, pct_done, completed, goal_id=None, milestone_id=None, blockers=None):
    conn = get_conn()
    if goal_id is not None or blockers is not None or milestone_id is not None:
        conn.execute("""
            UPDATE tasks SET 
                actual_mins=?, pct_done=?, completed=?,
                goal_id=COALESCE(?, goal_id),
                milestone_id=COALESCE(?, milestone_id),
                blockers=COALESCE(?, blockers)
            WHERE id=?
        """, (actual_mins, pct_done, completed, goal_id, milestone_id, blockers, task_id))
    else:
        conn.execute("UPDATE tasks SET actual_mins=?, pct_done=?, completed=? WHERE id=?",
                     (actual_mins, pct_done, completed, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def get_weekly_data():
    conn = get_conn()
    end = date.today()
    start = end - timedelta(days=6)
    df = pd.read_sql("""
        SELECT date,
               COUNT(*) as total,
               SUM(completed) as done,
               AVG(pct_done) as avg_pct
        FROM tasks
        WHERE date BETWEEN ? AND ?
        GROUP BY date ORDER BY date
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    all_days = pd.date_range(start, end)
    all_df = pd.DataFrame({'date': [d.strftime('%Y-%m-%d') for d in all_days]})
    merged = all_df.merge(df, on='date', how='left').fillna(0)
    return merged

def get_monthly_data():
    conn = get_conn()
    end = date.today()
    start = date(end.year, end.month, 1)
    df = pd.read_sql("""
        SELECT date, COUNT(*) as total, SUM(completed) as done, AVG(pct_done) as avg_pct
        FROM tasks WHERE date BETWEEN ? AND ?
        GROUP BY date ORDER BY date
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    return df

def get_month_record(year=None, month=None):
    """Return a full month's daily done/left/total/pct for every day in that month."""
    today_obj = date.today()
    if year is None:  year  = today_obj.year
    if month is None: month = today_obj.month
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)

    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            date,
            COUNT(*)                                    AS total,
            SUM(completed)                              AS done,
            SUM(CASE WHEN completed=0 THEN 1 ELSE 0 END) AS left_tasks,
            AVG(pct_done)                               AS avg_pct,
            SUM(est_mins)                               AS total_est_mins,
            SUM(actual_mins)                            AS total_actual_mins,
            SUM(CASE WHEN priority='high'   THEN 1 ELSE 0 END) AS high_total,
            SUM(CASE WHEN priority='high'   AND completed=1 THEN 1 ELSE 0 END) AS high_done,
            SUM(CASE WHEN priority='medium' THEN 1 ELSE 0 END) AS med_total,
            SUM(CASE WHEN priority='medium' AND completed=1 THEN 1 ELSE 0 END) AS med_done,
            SUM(CASE WHEN priority='low'    THEN 1 ELSE 0 END) AS low_total,
            SUM(CASE WHEN priority='low'    AND completed=1 THEN 1 ELSE 0 END) AS low_done
        FROM tasks
        WHERE date BETWEEN ? AND ?
        GROUP BY date ORDER BY date
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()

    # Fill every calendar day even if no tasks
    all_days = pd.DataFrame({
        'date': [(start + timedelta(days=i)).isoformat()
                 for i in range((end - start).days + 1)]
    })
    merged = all_days.merge(df, on='date', how='left').fillna(0)
    return merged, start, end

def get_goals():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM long_term_goals ORDER BY deadline", conn)
    conn.close()
    return df

def add_goal(title, deadline, category, description, progress=0, motivation="", start_date="", desired_outcome="", success_criteria="", status="active", blockers="", next_action="", review_frequency="weekly"):
    conn = get_conn()
    conn.execute("""
        INSERT INTO long_term_goals (
            title, deadline, category, description, progress,
            motivation, start_date, desired_outcome, success_criteria, status, blockers, next_action, review_frequency
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (title, deadline, category, description, progress, motivation, start_date, desired_outcome, success_criteria, status, blockers, next_action, review_frequency))
    conn.commit()
    conn.close()

def update_goal_details(goal_id, title, deadline, category, description, progress, motivation, desired_outcome, success_criteria, status, blockers, next_action):
    conn = get_conn()
    conn.execute("""
        UPDATE long_term_goals SET
            title=?, deadline=?, category=?, description=?, progress=?,
            motivation=?, desired_outcome=?, success_criteria=?, status=?, blockers=?, next_action=?
        WHERE id=?
    """, (title, deadline, category, description, progress, motivation, desired_outcome, success_criteria, status, blockers, next_action, goal_id))
    conn.commit()
    conn.close()

def update_goal_progress(goal_id, progress):
    conn = get_conn()
    conn.execute("UPDATE long_term_goals SET progress=? WHERE id=?", (progress, goal_id))
    conn.commit()
    conn.close()

def delete_goal(goal_id):
    conn = get_conn()
    conn.execute("DELETE FROM goal_milestones WHERE goal_id=?", (goal_id,))
    conn.execute("UPDATE tasks SET goal_id=NULL, milestone_id=NULL WHERE goal_id=?", (goal_id,))
    conn.execute("DELETE FROM long_term_goals WHERE id=?", (goal_id,))
    conn.commit()
    conn.close()

# ─── PHASE 3: MILESTONE & GOAL HIERARCHY HELPERS ──────────────────────────────
def get_goal_milestones(goal_id):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM goal_milestones WHERE goal_id=? ORDER BY completed ASC, target_date ASC, id ASC", conn, params=(goal_id,))
    conn.close()
    return df

def add_milestone(goal_id, title, target_date="", weight=1.0, notes=""):
    conn = get_conn()
    conn.execute("INSERT INTO goal_milestones (goal_id, title, target_date, weight, notes) VALUES (?,?,?,?,?)",
                 (goal_id, title, target_date, weight, notes))
    conn.commit()
    conn.close()

def toggle_milestone(milestone_id, completed):
    conn = get_conn()
    conn.execute("UPDATE goal_milestones SET completed=? WHERE id=?", (1 if completed else 0, milestone_id))
    conn.commit()
    conn.close()

def delete_milestone(milestone_id):
    conn = get_conn()
    conn.execute("UPDATE tasks SET milestone_id=NULL WHERE milestone_id=?", (milestone_id,))
    conn.execute("DELETE FROM goal_milestones WHERE id=?", (milestone_id,))
    conn.commit()
    conn.close()

def get_goal_tasks(goal_id):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM tasks WHERE goal_id=? ORDER BY date DESC, id DESC", conn, params=(goal_id,))
    conn.close()
    return df

def log_flex(what_failed, why_failed, reallocation):
    conn = get_conn()
    conn.execute("INSERT INTO flex_log (date,what_failed,why_failed,reallocation) VALUES (?,?,?,?)",
                 (date.today().isoformat(), what_failed, why_failed, reallocation))
    conn.commit()
    conn.close()

def get_flex_logs():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM flex_log ORDER BY created_at DESC LIMIT 10", conn)
    conn.close()
    return df

# ─── PHASE 4: ANALYTICS & DIAGNOSIS HELPERS ───────────────────────────────────
def get_analytics_data(days=30):
    """Return all tasks from the last N days for analytics."""
    conn = get_conn()
    end = date.today()
    start = end - timedelta(days=days - 1)
    df = pd.read_sql("""
        SELECT date, priority, category, est_mins, actual_mins, pct_done,
               completed, goal_id, blockers
        FROM tasks
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    return df, start, end

def get_estimation_accuracy(days=30):
    """Return per-day estimation accuracy: total planned vs actual minutes."""
    conn = get_conn()
    end = date.today()
    start = end - timedelta(days=days - 1)
    df = pd.read_sql("""
        SELECT date,
               SUM(est_mins) as planned_mins,
               SUM(actual_mins) as actual_mins,
               SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) as done_count,
               COUNT(*) as total_count,
               AVG(pct_done) as avg_pct
        FROM tasks
        WHERE date BETWEEN ? AND ?
          AND est_mins > 0
        GROUP BY date ORDER BY date
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    if not df.empty:
        df["accuracy_ratio"] = df.apply(
            lambda r: round(r["actual_mins"] / r["planned_mins"] * 100, 1)
                      if r["planned_mins"] > 0 else 0, axis=1)
    return df

def get_category_breakdown(days=30):
    """Time allocation by category over the last N days."""
    conn = get_conn()
    end = date.today()
    start = end - timedelta(days=days - 1)
    df = pd.read_sql("""
        SELECT category,
               COUNT(*) as total_tasks,
               SUM(completed) as done_tasks,
               SUM(est_mins) as planned_mins,
               SUM(actual_mins) as actual_mins,
               AVG(pct_done) as avg_pct
        FROM tasks
        WHERE date BETWEEN ? AND ?
        GROUP BY category ORDER BY actual_mins DESC
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    return df

def get_rolling_consistency(days=90):
    """Rolling 7-day consistency rate over the last N days."""
    conn = get_conn()
    end = date.today()
    start = end - timedelta(days=days - 1)
    df = pd.read_sql("""
        SELECT date,
               SUM(completed) as done,
               COUNT(*) as total,
               AVG(pct_done) as avg_pct
        FROM tasks WHERE date BETWEEN ? AND ?
        GROUP BY date ORDER BY date
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    all_days = pd.DataFrame({'date': [
        (start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)
    ]})
    merged = all_days.merge(df, on='date', how='left').fillna(0)
    # Rolling 7-day completion rate
    merged["completion_rate"] = merged.apply(
        lambda r: r["done"] / r["total"] * 100 if r["total"] > 0 else None, axis=1)
    merged["rolling_7d"] = merged["completion_rate"].rolling(7, min_periods=1).mean()
    merged["active"] = merged["total"] > 0
    return merged

def get_six_month_real_data():
    """Return monthly aggregates for the past 6 months (real data, not simulated)."""
    conn = get_conn()
    results = []
    today_obj = date.today()
    for i in range(5, -1, -1):
        y = today_obj.year
        m = today_obj.month - i
        while m <= 0:
            m += 12; y -= 1
        m_start = date(y, m, 1)
        if m == 12:
            m_end = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            m_end = date(y, m + 1, 1) - timedelta(days=1)
        row = conn.execute("""
            SELECT COUNT(*) as total, SUM(completed) as done
            FROM tasks WHERE date BETWEEN ? AND ?
        """, (m_start.isoformat(), m_end.isoformat())).fetchone()
        total = row[0] or 0
        done = row[1] or 0
        eff = round(done / total * 100, 1) if total > 0 else None
        results.append({"month": m_start.strftime("%b '%y"), "efficiency": eff,
                        "total": total, "done": done})
    conn.close()
    return results

def get_priority_completion_trend(days=30):
    """Per-priority completion rates for the last N days."""
    conn = get_conn()
    end = date.today()
    start = end - timedelta(days=days - 1)
    df = pd.read_sql("""
        SELECT date, priority,
               SUM(completed) as done,
               COUNT(*) as total,
               AVG(pct_done) as avg_pct
        FROM tasks WHERE date BETWEEN ? AND ?
        GROUP BY date, priority ORDER BY date
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    return df

def get_blockers_analysis(days=30):
    """Count and categorize blockers from tasks and flex_log."""
    conn = get_conn()
    end = date.today()
    start = end - timedelta(days=days - 1)
    # Tasks with blockers
    task_blockers = pd.read_sql("""
        SELECT blockers FROM tasks
        WHERE date BETWEEN ? AND ? AND blockers != '' AND blockers IS NOT NULL
    """, conn, params=(start.isoformat(), end.isoformat()))
    # Flex log failures
    flex_df = pd.read_sql("""
        SELECT what_failed, why_failed FROM flex_log
        WHERE date BETWEEN ? AND ?
    """, conn, params=(start.isoformat(), end.isoformat()))
    conn.close()
    return task_blockers, flex_df

# ─── PHASE 2: MISSION & MOTIVATION HELPERS ────────────────────────────────────
def get_mission_profile():
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM mission_profile WHERE id=1").fetchone()
    if not row:
        default_affirmations = json.dumps([
            "Consistency over intensity: show up and take deliberate action every single day.",
            "Discipline is remembering what you want most over what you want now.",
            "कर्म पर ध्यान, प्रगति का प्रमाण, और हर दिन बेहतर दिशा।"
        ])
        c.execute("""
            INSERT OR IGNORE INTO mission_profile (
                id, life_mission, career_aspirations, learning_goals, personal_growth,
                identity_statement, why_it_matters, what_it_enables, target_outcome, target_date,
                motivational_statements, show_sanskrit_motto, quote_rotation_mode
            ) VALUES (
                1,
                'Master core engineering disciplines, build resilient systems, and achieve intellectual and financial freedom.',
                'Attain a stable senior engineering career with >=50k monthly baseline and clear technical leadership.',
                'Systematic mastery of distributed systems, Linux internals, SQL, Docker, and GATE computer science.',
                'Practice radical personal accountability: honest reflection over self-blame, consistency over fleeting motivation.',
                'A disciplined systems engineer who honors commitments and turns knowledge into real-world impact.',
                'Because deliberate daily karma is the only authentic foundation for long-term self-respect and lasting achievement.',
                'Complete autonomy, ability to solve hard problems, provide for family, and build transformative technology.',
                'Rank 1st in GATE & achieve stable engineering income with advanced infrastructure mastery',
                '2027-02-01',
                ?,
                1,
                'daily'
            )
        """, (default_affirmations,))
        conn.commit()
        row = c.execute("SELECT * FROM mission_profile WHERE id=1").fetchone()

    cols = [col[0] for col in c.description]
    conn.close()
    return dict(zip(cols, row))

def update_mission_profile(profile_dict):
    conn = get_conn()
    conn.execute("""
        UPDATE mission_profile SET
            life_mission = ?,
            career_aspirations = ?,
            learning_goals = ?,
            personal_growth = ?,
            identity_statement = ?,
            why_it_matters = ?,
            what_it_enables = ?,
            target_outcome = ?,
            target_date = ?,
            motivational_statements = ?,
            show_sanskrit_motto = ?,
            quote_rotation_mode = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    """, (
        profile_dict.get('life_mission', ''),
        profile_dict.get('career_aspirations', ''),
        profile_dict.get('learning_goals', ''),
        profile_dict.get('personal_growth', ''),
        profile_dict.get('identity_statement', ''),
        profile_dict.get('why_it_matters', ''),
        profile_dict.get('what_it_enables', ''),
        profile_dict.get('target_outcome', ''),
        profile_dict.get('target_date', ''),
        profile_dict.get('motivational_statements', '[]'),
        int(profile_dict.get('show_sanskrit_motto', 1)),
        profile_dict.get('quote_rotation_mode', 'daily')
    ))
    conn.commit()
    conn.close()

def get_daily_intention(for_date=None):
    if for_date is None:
        for_date = date.today().isoformat()
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM daily_intentions WHERE date=?", (str(for_date),)).fetchone()
    if row:
        cols = [col[0] for col in c.description]
        res = dict(zip(cols, row))
    else:
        res = None
    conn.close()
    return res

def save_daily_intention(for_date, intention, why_today_matters="", energy_level=3, top_priority_task_id=None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO daily_intentions (date, intention, why_today_matters, energy_level, top_priority_task_id)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            intention = excluded.intention,
            why_today_matters = excluded.why_today_matters,
            energy_level = excluded.energy_level,
            top_priority_task_id = excluded.top_priority_task_id
    """, (str(for_date), intention, why_today_matters, energy_level, top_priority_task_id))
    conn.commit()
    conn.close()

def seed_demo_data():
    """Seed 2 weeks of historical demo data if DB is empty."""
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    if count > 0:
        return
    task_templates = [
        ("Complete project report",   "high",   90),
        ("Team standup + emails",      "high",   30),
        ("Study for exam",             "high",   60),
        ("Review pull requests",       "high",   45),
        ("Respond to client messages", "medium", 20),
        ("Read industry newsletter",   "medium", 15),
        ("Update documentation",       "medium", 40),
        ("Plan next week",             "medium", 30),
        ("Inbox zero",                 "low",    20),
        ("Organize desktop files",     "low",    15),
    ]
    for i in range(14):
        d = (date.today() - timedelta(days=14 - i)).isoformat()
        sample = random.sample(task_templates, random.randint(4, 7))
        conn = get_conn()
        for name, pri, est in sample:
            done = random.choice([0, 0, 1, 1, 1])
            pct  = 100 if done else random.randint(0, 80)
            actual = est + random.randint(-10, 20)
            conn.execute("INSERT INTO tasks (date,name,priority,est_mins,actual_mins,pct_done,completed) VALUES (?,?,?,?,?,?,?)",
                         (d, name, pri, est, actual, pct, done))
        conn.commit()
        conn.close()
    # Demo goals
    goals_data = [
        ("Get AWS Certified",         "2024-12-31", "career",   "Cloud certification for career growth", 34),
        ("Launch personal project",   "2024-09-30", "project",  "SaaS side project MVP", 18),
        ("Fitness: Run 5K daily",     "2024-06-30", "health",   "Build consistent running habit", 55),
        ("Read 24 books this year",   "2024-12-31", "learning", "2 books per month", 42),
    ]
    for title, dl, cat, desc, prog in goals_data:
        add_goal(title, dl, cat, desc, prog)

seed_demo_data()

# ─── COLOUR / CHART THEME ─────────────────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0d1117",
    font=dict(family="Inter", color="#8892b0", size=11),
    margin=dict(l=40, r=20, t=36, b=36),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)
AXIS_STYLE = dict(gridcolor="#1a3358", linecolor="#1a3358", tickcolor="#1a3358")

def apply_theme(fig, height=None, **kwargs):
    """Apply CHART_THEME plus axis styles cleanly without keyword conflicts."""
    fig.update_layout(**CHART_THEME, **kwargs)
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    if height:
        fig.update_layout(height=height)
    return fig
HIGH_COL  = "#dc2626"
MED_COL   = "#ffd700"
LOW_COL   = "#57cbff"
DONE_COL  = "#64ffda"
BLUE_COL  = "#1d4ed8"
PRI_COLORS = {"high": HIGH_COL, "medium": MED_COL, "low": LOW_COL}

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 16px'>
        <span style='font-size:32px'>🕉️</span><br>
        <span style='font-family:Noto Sans Devanagari;font-size:13px;font-weight:700;color:#f5c518'>कर्म प्रधान</span><br>
        <span style='font-size:11px;color:#4a5568'>Productivity Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Date selector
    selected_date = st.date_input("📅 Task Date", value=date.today())
    
    # Daily Intention Preview in Sidebar
    sidebar_intention = get_daily_intention(str(selected_date))
    if sidebar_intention and sidebar_intention.get("intention"):
        st.markdown(f"""
        <div style='background:#101828;border:1px solid #1e3a5f;border-left:3px solid #64ffda;border-radius:6px;padding:8px 10px;margin:8px 0 10px'>
            <div style='font-size:10px;color:#64ffda;font-weight:700;text-transform:uppercase;letter-spacing:0.8px'>🧭 Today's Intention</div>
            <div style='font-size:12px;color:#cbd5e1;margin-top:2px;line-height:1.4'>{sidebar_intention['intention']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Add Task ──
    st.markdown("<div class='section-header'>➕ Add New Task</div>", unsafe_allow_html=True)
    all_goals_sb = get_goals()
    goal_choices = [("None (No linked goal)", None)]
    for _, g in all_goals_sb.iterrows():
        goal_choices.append((f"🎯 {g['title']}", int(g['id'])))

    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("Task Name", placeholder="e.g. Complete project report")
        c1, c2 = st.columns(2)
        with c1:
            est_hours = st.number_input("Hours", 0, 12, 0, step=1)
        with c2:
            est_mins  = st.number_input("Minutes", 0, 59, 30, step=5)
        priority  = st.selectbox("Priority", ["high", "medium", "low"],
                                 format_func=lambda x: {"high":"🟠 High","medium":"🟡 Medium","low":"🔵 Low"}[x])
        category  = st.selectbox("Category", ["work","study","health","personal","creative"])
        
        # Phase 3: Goal & Milestone Linkage
        selected_goal_opt = st.selectbox("Link to Long-Term Goal (Optional)", options=goal_choices,
                                         format_func=lambda opt: opt[0])
        chosen_goal_id = selected_goal_opt[1]

        # Milestone selector if a goal is chosen
        chosen_milestone_id = None
        if chosen_goal_id:
            ms_for_goal = get_goal_milestones(chosen_goal_id)
            if not ms_for_goal.empty:
                ms_choices = [("None (General Goal Task)", None)]
                for _, ms_r in ms_for_goal.iterrows():
                    chk = "✅" if ms_r["completed"] else "⏳"
                    ms_choices.append((f"{chk} {ms_r['title']}", int(ms_r["id"])))
                selected_ms_opt = st.selectbox("Attach to Milestone (Optional)", options=ms_choices,
                                               format_func=lambda opt: opt[0])
                chosen_milestone_id = selected_ms_opt[1]

        task_blockers = st.text_input("Known Blockers / Dependencies (Optional)", placeholder="e.g. Waiting on API docs, low energy")

        submitted = st.form_submit_button("Add Task ✅", use_container_width=True)
        if submitted and task_name.strip():
            total_mins = est_hours * 60 + est_mins
            add_task(task_name.strip(), priority, total_mins, category, str(selected_date),
                     goal_id=chosen_goal_id, milestone_id=chosen_milestone_id, blockers=task_blockers.strip())
            st.success("Task added!")
            st.rerun()

    st.divider()
    # Entertainment slot
    st.markdown("<div class='section-header'>🎯 Balance Slot</div>", unsafe_allow_html=True)
    ent_name = st.text_input("Activity", value="Family / Entertainment")
    ent_dur  = st.slider("Duration (hours)", 0.5, 3.0, 1.5, 0.5)
    if st.button("Log Balance Time", use_container_width=True):
        add_task(ent_name, "low", ent_dur * 60, "balance", str(selected_date))
        st.success("Balance time logged!")
        st.rerun()

    st.divider()
    st.markdown("""
    <div style='font-size:11px;color:#4a5568;text-align:center'>
    "जो जस करहि सो तस फल चाखा"<br>
    <i>As you do, so shall you receive</i>
    </div>
    """, unsafe_allow_html=True)

# ─── HERO BANNER ──────────────────────────────────────────────────────────────
today_tasks = get_tasks(str(selected_date))
total_tasks = len(today_tasks)
done_tasks  = int(today_tasks["completed"].sum()) if total_tasks else 0
avg_pct     = float(today_tasks["pct_done"].mean()) if total_tasks else 0.0
high_pending = len(today_tasks[(today_tasks["priority"]=="high") & (today_tasks["completed"]==0)])

# Streak calculation
streak = 0
for i in range(30):
    d = (date.today() - timedelta(days=i)).isoformat()
    conn = get_conn()
    row = conn.execute("SELECT SUM(completed),COUNT(*) FROM tasks WHERE date=?", (d,)).fetchone()
    conn.close()
    if row[1] and row[1] > 0 and row[0] >= row[1] * 0.6:
        streak += 1
    elif i > 0:
        break

active_intention = get_daily_intention(str(selected_date))
intention_pill = f'<span class="hero-pill" style="border-color:rgba(100,255,218,0.5);color:#64ffda;background:rgba(100,255,218,0.1)">🧭 {active_intention["intention"][:35]}...</span>' if (active_intention and active_intention.get("intention")) else ''

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-quote">कर्म प्रधान विश्व रचि राखा, जो जस करहि सो तस फल चाखा</div>
    <div class="hero-sub">"The world is built on the primacy of karma — as you sow, so shall you reap"</div>
    <div class="hero-meta">
        <span class="hero-pill">📅 {selected_date.strftime('%A, %d %B %Y')}</span>
        <span class="hero-pill">🔥 {streak}-day streak</span>
        <span class="hero-pill">⚡ {high_pending} high-priority pending</span>
        {intention_pill}
    </div>
</div>
""", unsafe_allow_html=True)

# ─── METRIC CARDS ─────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Today's Tasks</div>
        <div class="metric-val metric-blue">{total_tasks}</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Completed</div>
        <div class="metric-val metric-green">{done_tasks}</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg. Progress</div>
        <div class="metric-val metric-amber">{avg_pct:.0f}%</div>
    </div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Day Streak 🔥</div>
        <div class="metric-val metric-red">{streak}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

# ─── MAIN TABS ────────────────────────────────────────────────────────────────
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🌟  Mission & Motivation",
    "📋  Today's Tasks",
    "📊  Weekly Summary",
    "📆  Monthly Tracker",
    "🔄  Flexibility & Recovery",
    "🎯  Long-Term Goals",
    "🗓️  1-Month Record",
    "🔬  Performance Diagnosis",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — MISSION & MOTIVATION CENTER (PHASE 2)
# ══════════════════════════════════════════════════════════════════════════════
with tab0:
    profile = get_mission_profile()
    today_intention = get_daily_intention(str(selected_date))
    all_goals_df = get_goals()
    
    # Target date calculation
    target_date_str = profile.get("target_date", "")
    days_to_target = None
    if target_date_str:
        try:
            days_to_target = (datetime.strptime(target_date_str, "%Y-%m-%d").date() - date.today()).days
        except Exception:
            days_to_target = None

    # Top Row: Hero Mission Statement & Identity Banner
    st.markdown(f"""
    <div class="mission-card">
        <div class="mission-title">🌟 Primary Life Mission & Core Purpose</div>
        <div class="mission-statement">{profile.get('life_mission', 'Define your life mission in settings below.')}</div>
        <div style='margin-top:12px;display:flex;flex-wrap:wrap;gap:14px;align-items:center'>
            <span style='background:rgba(29,78,216,0.25);border:1px solid rgba(29,78,216,0.5);border-radius:20px;padding:4px 14px;font-size:12px;color:#bfdbfe'>
                👤 <b>Identity:</b> {profile.get('identity_statement', 'Disciplined Systems Engineer')}
            </span>
            {f"<span style='background:rgba(245,197,24,0.15);border:1px solid rgba(245,197,24,0.3);border-radius:20px;padding:4px 14px;font-size:12px;color:#ffd700'>⏳ <b>Target Countdown:</b> {days_to_target} days remaining ({target_date_str})</span>" if days_to_target is not None else ""}
            <span style='background:rgba(100,255,218,0.15);border:1px solid rgba(100,255,218,0.3);border-radius:20px;padding:4px 14px;font-size:12px;color:#64ffda'>
                🎯 <b>Target:</b> {profile.get('target_outcome', 'Mastery & Freedom')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2-column layout: Left = Daily Intention & Actionable Bridge; Right = Top Goals & Affirmations
    col_m1, col_m2 = st.columns([3, 2], gap="medium")

    with col_m1:
        # Today's Intention & North Star
        st.markdown(f"<div class='section-header'>🧭 Today's Daily Intention & North Star ({selected_date.strftime('%a, %d %b')})</div>", unsafe_allow_html=True)
        
        current_intention_text = today_intention.get("intention", "") if today_intention else ""
        current_why_text = today_intention.get("why_today_matters", "") if today_intention else ""
        current_energy = int(today_intention.get("energy_level", 3)) if today_intention else 3
        current_task_id = today_intention.get("top_priority_task_id", None) if today_intention else None

        with st.form("daily_intention_form"):
            int_c1, int_c2 = st.columns([3, 1])
            with int_c1:
                new_intention = st.text_input("Daily Intention / North Star", value=current_intention_text, 
                                             placeholder="e.g. Relentless focus on GATE Algorithms and Linux internals")
            with int_c2:
                new_energy = st.select_slider("Energy & Focus", options=[1, 2, 3, 4, 5], value=current_energy,
                                              format_func=lambda x: {1:"⚡ 1 Low", 2:"⚡ 2 Fair", 3:"⚡ 3 Good", 4:"⚡ 4 High", 5:"⚡ 5 Peak"}[x])
            
            new_why = st.text_area("Why does today matter for your long-term mission?", value=current_why_text, height=65,
                                   placeholder="e.g. Every day of deliberate practice moves me closer to rank 1st and financial autonomy.")

            # Task Association Dropdown
            task_options = [("None", None)]
            if not today_tasks.empty:
                for _, t_row in today_tasks.iterrows():
                    pri_emoji = "🔴" if t_row["priority"] == "high" else "🟡" if t_row["priority"] == "medium" else "🔵"
                    task_options.append((f"{pri_emoji} {t_row['name']} ({t_row['priority'].title()})", int(t_row["id"])))
            
            curr_index = 0
            if current_task_id:
                for idx, opt in enumerate(task_options):
                    if opt[1] == current_task_id:
                        curr_index = idx
                        break

            chosen_task = st.selectbox("Anchor to Today's Most Important Task", options=task_options, index=curr_index,
                                       format_func=lambda opt: opt[0])

            sub_int = st.form_submit_button("🧭 Save Today's Intention", use_container_width=True)
            if sub_int:
                if new_intention.strip():
                    save_daily_intention(str(selected_date), new_intention.strip(), new_why.strip(), new_energy, chosen_task[1])
                    st.success("Today's intention anchored! Ground yourself in deliberate action.")
                    st.rerun()

        # Actionable Motivation Bridge
        st.markdown("<div class='section-header' style='margin-top:16px'>🌉 Actionable Motivation Bridge</div>", unsafe_allow_html=True)
        unfinished_high = today_tasks[(today_tasks["completed"] == 0) & (today_tasks["priority"].isin(["high", "medium"]))]
        action_task = unfinished_high.iloc[0] if not unfinished_high.empty else (today_tasks[today_tasks["completed"] == 0].iloc[0] if not today_tasks[today_tasks["completed"] == 0].empty else None)
        
        top_goal = all_goals_df.iloc[0] if not all_goals_df.empty else None

        if action_task is not None and top_goal is not None:
            st.markdown(f"""
            <div style='background:#101828;border:1px solid #1d4ed855;border-left:4px solid #1d4ed8;border-radius:10px;padding:16px 20px;margin-bottom:14px'>
                <div style='font-size:12px;font-weight:700;color:#57cbff;text-transform:uppercase;letter-spacing:1px'>🎯 Direct Action Alignment</div>
                <div style='font-size:14px;color:#e2e8f0;margin-top:6px;line-height:1.6'>
                    Your long-term goal <b style='color:#ffd700'>"{top_goal['title']}"</b> matters because you are building practical mastery and autonomy.
                </div>
                <div style='background:#0d1117;border:1px solid #1e3a5f;border-radius:8px;padding:10px 14px;margin-top:10px;display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <span style='font-size:11px;color:#8892b0;text-transform:uppercase'>Next Best Action Today</span><br>
                        <span style='font-size:14px;font-weight:600;color:#64ffda'>⚡ {action_task['name']}</span>
                    </div>
                    <span class='badge badge-high'>{action_task['priority'].upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif done_tasks > 0 and (total_tasks == done_tasks):
            st.markdown(f"""
            <div style='background:#052414;border:1px solid #065f46;border-left:4px solid #64ffda;border-radius:10px;padding:16px 20px;margin-bottom:14px'>
                <div style='font-size:14px;font-weight:700;color:#64ffda'>🏆 All Scheduled Work Completed!</div>
                <div style='font-size:13px;color:#cbd5e1;margin-top:4px'>You have honored your daily commitments. True discipline is compounding your future. Take rest or invest in light reading.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#101828;border:1px solid #1e3a5f;border-radius:10px;padding:14px 18px;margin-bottom:14px;color:#8892b0;font-size:13px'>
                📌 Add tasks for today to generate your live actionable motivation bridge.
            </div>
            """, unsafe_allow_html=True)

        # Four Pillars of Purpose Grid
        st.markdown("<div class='section-header' style='margin-top:16px'>🏛️ Four Pillars of Purpose</div>", unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            st.markdown(f"""
            <div class="pillar-card">
                <div class="pillar-header" style="color:#57cbff">💼 Career Aspirations</div>
                <div style="font-size:13px;color:#cbd5e1;line-height:1.5">{profile.get('career_aspirations', '—')}</div>
            </div>
            <div class="pillar-card" style="margin-top:10px">
                <div class="pillar-header" style="color:#64ffda">🌿 Personal Growth & Discipline</div>
                <div style="font-size:13px;color:#cbd5e1;line-height:1.5">{profile.get('personal_growth', '—')}</div>
            </div>
            """, unsafe_allow_html=True)
        with p2:
            st.markdown(f"""
            <div class="pillar-card">
                <div class="pillar-header" style="color:#ffd700">📚 Learning & Mastery</div>
                <div style="font-size:13px;color:#cbd5e1;line-height:1.5">{profile.get('learning_goals', '—')}</div>
            </div>
            <div class="pillar-card" style="margin-top:10px">
                <div class="pillar-header" style="color:#c084fc">💡 Why It Matters & Enables</div>
                <div style="font-size:13px;color:#cbd5e1;line-height:1.5">{profile.get('why_it_matters', '—')}<br><i style="color:#94a3b8">Enables: {profile.get('what_it_enables', '—')}</i></div>
            </div>
            """, unsafe_allow_html=True)

    with col_m2:
        # Top 3 Goals Spotlight
        st.markdown("<div class='section-header'>🎯 Current Top Goals Spotlight</div>", unsafe_allow_html=True)
        if not all_goals_df.empty:
            top_3_goals = all_goals_df.head(3)
            for _, g_row in top_3_goals.iterrows():
                g_prog = float(g_row["progress"])
                g_dl = g_row["deadline"]
                g_cat = g_row["category"]
                cat_colors = {"career":"#57cbff","project":"#ffd700","health":"#64ffda","learning":"#dc2626","personal":"#c084fc"}
                badge_col = cat_colors.get(g_cat, "#8892b0")
                
                days_left = None
                try:
                    days_left = (datetime.strptime(g_dl, "%Y-%m-%d").date() - date.today()).days
                except:
                    pass

                st.markdown(f"""
                <div style='background:#101828;border:1px solid #1e3a5f;border-radius:10px;padding:14px 16px;margin-bottom:10px'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                        <div>
                            <span style='font-size:14px;font-weight:600;color:#f1f5f9'>{g_row['title']}</span><br>
                            <span style='font-size:11px;color:#8892b0'>📂 {g_cat.title()} &nbsp;·&nbsp; 🗓 {g_dl} {"(" + str(days_left) + "d left)" if days_left is not None else ""}</span>
                        </div>
                        <span style='font-size:16px;font-weight:700;color:{badge_col}'>{g_prog:.0f}%</span>
                    </div>
                    <div class='prog-wrap' style='margin-top:8px;height:6px'>
                        <div style='width:{g_prog}%;background:{badge_col};height:100%;border-radius:3px'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No long-term goals configured yet. Add them in the Long-Term Goals tab.")

        # Personal Affirmations & Meaningful Grounding
        st.markdown("<div class='section-header' style='margin-top:16px'>📜 Personal Affirmations & Grounding</div>", unsafe_allow_html=True)
        
        # Sanskrit quotation card (controlled display)
        if profile.get("show_sanskrit_motto", 1):
            st.markdown("""
            <div style='background:linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);border:1px solid #4338ca;border-radius:10px;padding:16px 18px;margin-bottom:12px;text-align:center'>
                <div style='font-family:Noto Sans Devanagari, sans-serif;font-size:16px;font-weight:700;color:#f5c518;letter-spacing:0.5px'>
                    कर्म प्रधान विश्व रचि राखा, जो जस करहि सो तस फल चाखा
                </div>
                <div style='font-size:11px;color:#a5b4fc;margin-top:4px;font-style:italic'>
                    "The universe is governed by the primacy of action — as you sow, so shall you reap"
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Personal Affirmations list
        raw_affs = profile.get("motivational_statements", "[]")
        try:
            aff_list = json.loads(raw_affs) if isinstance(raw_affs, str) else raw_affs
        except:
            aff_list = [raw_affs]
        
        if aff_list:
            for aff in aff_list:
                if str(aff).strip():
                    st.markdown(f"""
                    <div class="affirmation-pill">
                        ✨ <b>Affirmation:</b> {aff}
                    </div>
                    """, unsafe_allow_html=True)

        # Recent Karma Momentum (Completed wins today)
        st.markdown("<div class='section-header' style='margin-top:16px'>🔥 Recent Karma Momentum</div>", unsafe_allow_html=True)
        done_today_tasks = today_tasks[today_tasks["completed"] == 1]
        if not done_today_tasks.empty:
            for _, d_row in done_today_tasks.head(3).iterrows():
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:10px;background:#06231a;border:1px solid #065f46;border-radius:8px;padding:8px 12px;margin-bottom:6px'>
                    <span style='color:#64ffda;font-size:14px'>✓</span>
                    <span style='font-size:13px;color:#e2e8f0;flex:1'>{d_row['name']}</span>
                    <span style='font-size:11px;color:#64ffda'>{int(d_row['actual_mins'])}m recorded</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background:#101828;border:1px solid #1a3358;border-radius:8px;padding:12px 14px;color:#8892b0;font-size:12px;text-align:center'>
                Ready to take deliberate action today. Your streak: <b style='color:#dc2626'>{streak} days</b> 🔥
            </div>
            """, unsafe_allow_html=True)

        # Constructive Reflection on Recent Consistency
        st.markdown("<div class='section-header' style='margin-top:16px'>🌱 Constructive Consistency Reflection</div>", unsafe_allow_html=True)
        if streak >= 3:
            st.markdown(f"""
            <div style='background:#06231a;border:1px solid #065f46;border-left:3px solid #64ffda;border-radius:8px;padding:12px 14px'>
                <div style='font-size:13px;font-weight:700;color:#64ffda'>🔥 {streak}-Day Active Consistency Streak</div>
                <div style='font-size:12px;color:#cbd5e1;margin-top:4px;line-height:1.5'>
                    You are proving the core philosophy: <i>"Consistency over intensity."</i> Each day you show up strengthens your identity as someone who follows through. Guard against overcommitting—protect this momentum.
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif streak > 0:
            st.markdown(f"""
            <div style='background:#0d1b2a;border:1px solid #1e3a5f;border-left:3px solid #ffd700;border-radius:8px;padding:12px 14px'>
                <div style='font-size:13px;font-weight:700;color:#ffd700'>⚡ Building Daily Momentum (Day {streak})</div>
                <div style='font-size:12px;color:#cbd5e1;margin-top:4px;line-height:1.5'>
                    The hardest part of any streak is the beginning. Anchor your day in your #1 priority task today. Small deliberate actions compound into massive long-term results.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#101828;border:1px solid #1a3358;border-left:3px solid #57cbff;border-radius:8px;padding:12px 14px'>
                <div style='font-size:13px;font-weight:700;color:#57cbff'>🌅 Fresh Ground — New Beginning</div>
                <div style='font-size:12px;color:#cbd5e1;margin-top:4px;line-height:1.5'>
                    <i>"Honest reflection over self-blame."</i> Missed days are merely data points, not verdicts on your potential. Pick the single most important task today and complete it with focus.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Section: Configuration & Profile Editor
    st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
    with st.expander("⚙️ Configure Life Mission, Purpose & Affirmations Profile"):
        st.markdown("<div style='font-size:12px;color:#8892b0;margin-bottom:12px'>Edit your personal mission statement, career aspirations, and motivation settings stored locally in SQLite.</div>", unsafe_allow_html=True)
        with st.form("edit_mission_profile_form"):
            e_mission = st.text_area("Primary Life Mission", value=profile.get("life_mission", ""), height=70)
            e_identity = st.text_input("Identity Statement ('The Person I Want to Become')", value=profile.get("identity_statement", ""))
            
            ec1, ec2 = st.columns(2)
            with ec1:
                e_career = st.text_area("Career Aspirations", value=profile.get("career_aspirations", ""), height=75)
                e_learning = st.text_area("Learning & Technical Development Goals", value=profile.get("learning_goals", ""), height=75)
                e_outcome = st.text_input("Desired Target Outcome", value=profile.get("target_outcome", ""))
            with ec2:
                e_growth = st.text_area("Personal Growth & Consistency Philosophy", value=profile.get("personal_growth", ""), height=75)
                e_why = st.text_area("Why Each Goal Matters to Me & What It Enables", value=profile.get("why_it_matters", ""), height=75)
                
                def_date = date.today() + timedelta(days=365)
                try:
                    if profile.get("target_date"):
                        def_date = datetime.strptime(profile.get("target_date"), "%Y-%m-%d").date()
                except:
                    pass
                e_tdate = st.date_input("Target Date for Long-Term Outcome", value=def_date)

            e_enables = st.text_input("What Achieving These Goals Will Enable", value=profile.get("what_it_enables", ""))
            
            aff_text = "\n".join(aff_list) if isinstance(aff_list, list) else str(aff_list)
            e_aff_text = st.text_area("Personal Affirmations / Motivational Statements (One per line)", value=aff_text, height=85)
            
            opt_c1, opt_c2 = st.columns(2)
            with opt_c1:
                e_show_motto = st.checkbox("Show Sanskrit Motto Banner", value=bool(profile.get("show_sanskrit_motto", 1)))
            with opt_c2:
                e_rot_mode = st.selectbox("Affirmation Rotation Mode", options=["daily", "all"], index=0 if profile.get("quote_rotation_mode") == "daily" else 1)

            save_prof = st.form_submit_button("💾 Save Mission Profile", use_container_width=True)
            if save_prof:
                parsed_affs = [line.strip() for line in e_aff_text.split("\n") if line.strip()]
                updated_dict = {
                    "life_mission": e_mission.strip(),
                    "identity_statement": e_identity.strip(),
                    "career_aspirations": e_career.strip(),
                    "learning_goals": e_learning.strip(),
                    "personal_growth": e_growth.strip(),
                    "why_it_matters": e_why.strip(),
                    "what_it_enables": e_enables.strip(),
                    "target_outcome": e_outcome.strip(),
                    "target_date": str(e_tdate),
                    "motivational_statements": json.dumps(parsed_affs),
                    "show_sanskrit_motto": 1 if e_show_motto else 0,
                    "quote_rotation_mode": e_rot_mode
                }
                update_mission_profile(updated_dict)
                st.success("Personal mission profile updated successfully!")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TODAY'S TASKS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    left_col, right_col = st.columns([3, 2], gap="medium")

    with left_col:
        if total_tasks == 0:
            st.info("No tasks for this date. Use the sidebar to add tasks.")
        else:
            for priority_level, label, css_class, badge_class in [
                ("high",   "🟠 HIGH PRIORITY — Must Do Today", "priority-high", "badge-high"),
                ("medium", "🟡 MEDIUM PRIORITY",               "priority-med",  "badge-med"),
                ("low",    "🔵 LOW PRIORITY",                  "priority-low",  "badge-low"),
            ]:
                level_tasks = today_tasks[today_tasks["priority"] == priority_level]
                if level_tasks.empty:
                    continue

                st.markdown(f"""
                <div style='font-size:11px;font-weight:700;letter-spacing:1.2px;
                            color:{"#dc2626" if priority_level=="high" else "#ffd700" if priority_level=="medium" else "#57cbff"};
                            margin:14px 0 8px;text-transform:uppercase;border-bottom:1px solid #1a3358;padding-bottom:6px'>
                    {label}
                </div>""", unsafe_allow_html=True)

                for _, row in level_tasks.iterrows():
                    tid = int(row["id"])
                    pct = float(row["pct_done"])
                    done = bool(row["completed"])
                    fill_class = "prog-fill-done" if done else f"prog-fill-{priority_level if priority_level!='medium' else 'med'}"
                    bar_color  = DONE_COL if done else PRI_COLORS.get(priority_level, LOW_COL)

                    # Goal link tag if linked
                    linked_goal_name = None
                    if "goal_id" in row and pd.notna(row["goal_id"]) and row["goal_id"]:
                        g_match = all_goals_sb[all_goals_sb["id"] == row["goal_id"]]
                        if not g_match.empty:
                            linked_goal_name = g_match.iloc[0]["title"]

                    with st.container():
                        st.markdown(f"""
                        <div class="{css_class}">
                            <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                                <div>
                                    <span class='task-name' style='{"text-decoration:line-through;opacity:0.5" if done else ""}'>{row['name']}</span>
                                    <span class='badge {badge_class if not done else "badge-done"}' style='margin-left:8px'>
                                        {"✅ Done" if done else priority_level.title()}
                                    </span>
                                    {f"<span class='badge' style='background:#1d4ed822;color:#57cbff;border:1px solid #1d4ed855;margin-left:6px'>🎯 {linked_goal_name[:25]}</span>" if linked_goal_name else ""}
                                    <br>
                                    <span class='task-meta'>📂 {row['category']} &nbsp;·&nbsp; 
                                    ⏱ Est: {int(row['est_mins']//60)}h {int(row['est_mins']%60)}m &nbsp;·&nbsp;
                                    ✅ Actual: {int(row['actual_mins']//60)}h {int(row['actual_mins']%60)}m
                                    {f" &nbsp;·&nbsp; 🚧 <i>{row['blockers']}</i>" if ('blockers' in row and row['blockers']) else ""}
                                    </span>
                                </div>
                                <span style='font-size:18px;font-weight:700;color:{bar_color}'>{pct:.0f}%</span>
                            </div>
                            <div class='prog-wrap' style='margin-top:8px'>
                                <div style='width:{pct}%;background:{bar_color};height:100%;border-radius:4px;
                                            transition:width 0.4s'></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        ec1, ec2, ec3, ec4 = st.columns([2, 2, 2, 1])
                        with ec1:
                            actual_h = st.number_input("Actual hrs", 0, 12, int(row["actual_mins"])//60,
                                                        key=f"ah_{tid}", label_visibility="collapsed")
                        with ec2:
                            actual_m = st.number_input("Actual min", 0, 59, int(row["actual_mins"])%60,
                                                        key=f"am_{tid}", label_visibility="collapsed")
                        with ec3:
                            new_pct = st.slider("% done", 0, 100, int(pct), 5,
                                                key=f"pct_{tid}", label_visibility="collapsed")
                        with ec4:
                            if st.button("💾", key=f"save_{tid}", help="Save updates"):
                                total_actual = actual_h * 60 + actual_m
                                update_task(tid, total_actual, new_pct, 1 if new_pct == 100 else 0)
                                st.rerun()
                            if st.button("🗑", key=f"del_{tid}", help="Delete task"):
                                delete_task(tid)
                                st.rerun()

            # Entertainment / Balance
            balance_tasks = today_tasks[today_tasks["category"] == "balance"]
            if not balance_tasks.empty:
                st.markdown("""
                <div style='font-size:11px;font-weight:700;letter-spacing:1.2px;
                            color:#64ffda;margin:14px 0 8px;text-transform:uppercase;
                            border-bottom:1px solid #1a3358;padding-bottom:6px'>
                    🌿 BALANCE — Entertainment / Family / Rest
                </div>""", unsafe_allow_html=True)
                for _, row in balance_tasks.iterrows():
                    st.markdown(f"""
                    <div class="priority-ent">
                        <span class='task-name'>{row['name']}</span>
                        <span class='badge badge-done' style='margin-left:8px'>Balance</span><br>
                        <span class='task-meta'>⏱ {int(row['est_mins']//60)}h {int(row['est_mins']%60)}m allocated
                        &nbsp;·&nbsp; Prevents burnout ✅</span>
                    </div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='section-header'>📈 Today at a Glance</div>", unsafe_allow_html=True)

        # Donut chart — priority split
        if total_tasks > 0:
            pri_counts = today_tasks.groupby("priority").size().reset_index(name="count")
            color_map  = {"high": HIGH_COL, "medium": MED_COL, "low": LOW_COL}
            fig_donut = go.Figure(go.Pie(
                labels=pri_counts["priority"].str.title(),
                values=pri_counts["count"],
                hole=0.65,
                marker_colors=[color_map.get(p, LOW_COL) for p in pri_counts["priority"]],
                textfont_size=11,
            ))
            apply_theme(fig_donut, height=200,
                                    annotations=[dict(text=f"{done_tasks}/{total_tasks}", x=0.5, y=0.5,
                                                      font_size=20, font_color="#ccd6f6", showarrow=False)])
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

        # Time allocation gauge
        total_est = today_tasks["est_mins"].sum()
        WORK_CAPACITY = 480  # 8 hours
        used_pct = min(total_est / WORK_CAPACITY * 100, 100)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_est / 60,
            delta={"reference": WORK_CAPACITY / 60, "valueformat": ".1f"},
            title={"text": "Scheduled hours", "font": {"color": "#8892b0", "size": 12}},
            number={"suffix": "h", "font": {"size": 24, "color": "#ccd6f6"}},
            gauge={
                "axis": {"range": [0, 10], "tickcolor": "#8892b0"},
                "bar": {"color": BLUE_COL},
                "bgcolor": "#1a3358",
                "steps": [
                    {"range": [0, 6],  "color": "#064e3b"},
                    {"range": [6, 8],  "color": "#1e3a5f"},
                    {"range": [8, 10], "color": "#4a1230"},
                ],
                "threshold": {"line": {"color": HIGH_COL, "width": 2}, "value": 8},
            },
        ))
        apply_theme(fig_gauge, height=200)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        # Completion bar per priority
        st.markdown("<div class='section-header'>Completion by Priority</div>", unsafe_allow_html=True)
        for pri, col in [("high", HIGH_COL), ("medium", MED_COL), ("low", LOW_COL)]:
            subset = today_tasks[today_tasks["priority"] == pri]
            if subset.empty:
                continue
            avg = subset["pct_done"].mean()
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>
                <span style='font-size:12px;color:#8892b0;width:60px'>{pri.title()}</span>
                <div class='prog-wrap' style='flex:1;height:10px'>
                    <div style='width:{avg:.0f}%;background:{col};height:100%;border-radius:5px'></div>
                </div>
                <span style='font-size:12px;color:{col};min-width:34px;text-align:right'>{avg:.0f}%</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — WEEKLY SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    weekly_df = get_weekly_data()

    day_labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%a %d") for d in weekly_df["date"]]
    today_str  = date.today().isoformat()

    bar_colors = []
    for d in weekly_df["date"]:
        if d == today_str:
            bar_colors.append(BLUE_COL)
        elif weekly_df.loc[weekly_df["date"]==d, "done"].values[0] >= weekly_df.loc[weekly_df["date"]==d, "total"].values[0] * 0.8:
            bar_colors.append(DONE_COL)
        else:
            bar_colors.append(HIGH_COL)

    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.markdown("<div class='section-header'>✅ Tasks Completed — Last 7 Days</div>", unsafe_allow_html=True)
        fig_week = go.Figure()
        fig_week.add_trace(go.Bar(
            x=day_labels, y=weekly_df["total"].tolist(),
            name="Total", marker_color=["#1a3358"]*7, opacity=0.6,
        ))
        fig_week.add_trace(go.Bar(
            x=day_labels, y=weekly_df["done"].tolist(),
            name="Completed", marker_color=bar_colors,
        ))
        apply_theme(fig_week, height=280, barmode="overlay",
            title=dict(text="Daily Task Completion", font=dict(color="#ccd6f6", size=13)))
        st.plotly_chart(fig_week, use_container_width=True, config={"displayModeBar": False})

        # Line chart — completion %
        st.markdown("<div class='section-header'>📉 Avg. Completion % Trend</div>", unsafe_allow_html=True)
        fig_pct = go.Figure()
        fig_pct.add_trace(go.Scatter(
            x=day_labels, y=weekly_df["avg_pct"].tolist(),
            mode="lines+markers",
            line=dict(color=MED_COL, width=2),
            marker=dict(size=7, color=MED_COL),
            fill="tozeroy",
            fillcolor="rgba(255,215,0,0.08)",
            name="Completion %",
        ))
        fig_pct.add_hline(y=80, line_dash="dot", line_color=DONE_COL,
                          annotation_text="80% target", annotation_font_color=DONE_COL)
        apply_theme(fig_pct, height=220)
        fig_pct.update_yaxes(range=[0, 105])
        st.plotly_chart(fig_pct, use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown("<div class='section-header'>🔥 7-Day Streak Board</div>", unsafe_allow_html=True)
        streak_html = "<div style='display:flex;gap:4px;flex-wrap:wrap;margin-bottom:12px'>"
        for _, row in weekly_df.iterrows():
            d = row["date"]
            total_t = int(row["total"])
            done_t  = int(row["done"])
            if d == today_str:
                cls = "streak-today"; emoji = "📍"
            elif total_t > 0 and done_t >= total_t * 0.6:
                cls = "streak-done"; emoji = "✓"
            else:
                cls = "streak-miss"; emoji = "·"
            day_abbr = datetime.strptime(d, "%Y-%m-%d").strftime("%a")
            streak_html += f"""
            <div title='{d}: {done_t}/{total_t} done'
                 style='background:{"#064e3b" if cls=="streak-done" else "#1d4ed8" if cls=="streak-today" else "#1a1f2e"};
                        border:1px solid {"#065f46" if cls=="streak-done" else "#2563eb" if cls=="streak-today" else "#2d3748"};
                        border-radius:8px;padding:8px 6px;text-align:center;min-width:40px'>
                <div style='font-size:14px'>{emoji}</div>
                <div style='font-size:10px;color:{"#64ffda" if cls!="streak-miss" else "#4a5568"};margin-top:2px'>{day_abbr}</div>
            </div>"""
        streak_html += "</div>"
        st.markdown(streak_html, unsafe_allow_html=True)

        # Weekly summary metrics
        total_w = int(weekly_df["total"].sum())
        done_w  = int(weekly_df["done"].sum())
        eff     = done_w / total_w * 100 if total_w else 0

        for label, val, col in [
            ("Total tasks this week", total_w, "#57cbff"),
            ("Completed",             done_w,  "#64ffda"),
            ("Weekly efficiency",     f"{eff:.0f}%", MED_COL),
        ]:
            st.markdown(f"""
            <div class='metric-card' style='margin-bottom:8px'>
                <div class='metric-label'>{label}</div>
                <div style='font-size:24px;font-weight:700;color:{col};margin:4px 0'>{val}</div>
            </div>""", unsafe_allow_html=True)

        # Estimation accuracy for the week
        est_acc_df = get_estimation_accuracy(days=7)
        if not est_acc_df.empty:
            st.markdown("<div class='section-header' style='margin-top:16px'>⏱ Estimation Accuracy — This Week</div>", unsafe_allow_html=True)
            avg_ratio = est_acc_df["accuracy_ratio"].mean()
            total_planned_w = int(est_acc_df["planned_mins"].sum())
            total_actual_w  = int(est_acc_df["actual_mins"].sum())
            diff_mins = total_actual_w - total_planned_w
            sign = "+" if diff_mins >= 0 else ""
            acc_color = DONE_COL if 85 <= avg_ratio <= 115 else MED_COL if 70 <= avg_ratio <= 130 else HIGH_COL
            st.markdown(f"""
            <div style='background:#101828;border:1px solid {acc_color}22;border-left:3px solid {acc_color};
                        border-radius:8px;padding:12px 14px;margin-bottom:10px'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <div style='font-size:12px;font-weight:700;color:{acc_color};text-transform:uppercase;letter-spacing:.8px'>Time Estimation Accuracy</div>
                        <div style='font-size:11px;color:#8892b0;margin-top:2px'>Planned: {total_planned_w//60}h {total_planned_w%60}m &nbsp;·&nbsp; Actual: {total_actual_w//60}h {total_actual_w%60}m &nbsp;·&nbsp; Variance: {sign}{diff_mins} min</div>
                    </div>
                    <div style='font-size:26px;font-weight:700;color:{acc_color}'>{avg_ratio:.0f}%</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Motivational insight
        if eff >= 80:
            insight = ("🏆 Excellent week!", "You are on fire! Maintain the momentum.", DONE_COL)
        elif eff >= 60:
            insight = ("💪 Solid progress!", "Good consistency. Push to 80%+ next week.", MED_COL)
        else:
            insight = ("🌱 Keep going!", "Every day is a new opportunity. Start small, go big.", LOW_COL)

        st.markdown(f"""
        <div style='background:#101828;border:1px solid {insight[2]}22;border-left:3px solid {insight[2]};
                    border-radius:8px;padding:12px 14px;margin-top:8px'>
            <div style='font-size:14px;font-weight:600;color:{insight[2]}'>{insight[0]}</div>
            <div style='font-size:12px;color:#8892b0;margin-top:4px'>{insight[1]}</div>
        </div>""", unsafe_allow_html=True)

    # ── Below weekly columns: Category breakdown ──────────────────────────────
    st.markdown("<div class='section-header' style='margin-top:18px'>🗂 Category Time Allocation — Last 7 Days</div>", unsafe_allow_html=True)
    cat_df_7 = get_category_breakdown(days=7)
    if not cat_df_7.empty:
        cat_colors_map = {
            "work": "#1d4ed8", "study": "#ffd700", "health": "#64ffda",
            "personal": "#c084fc", "creative": "#fb923c", "balance": "#34d399"
        }
        c_a, c_b = st.columns(2)
        with c_a:
            fig_cat_bar = go.Figure()
            for _, crow in cat_df_7.iterrows():
                col_c = cat_colors_map.get(str(crow["category"]), "#8892b0")
                fig_cat_bar.add_trace(go.Bar(
                    x=[str(crow["category"]).title()],
                    y=[float(crow["actual_mins"])],
                    name=str(crow["category"]).title(),
                    marker_color=col_c,
                    showlegend=False,
                    hovertemplate=f"{str(crow['category']).title()}<br>Actual: {int(crow['actual_mins']//60)}h {int(crow['actual_mins']%60)}m<extra></extra>"
                ))
            apply_theme(fig_cat_bar, height=220,
                title=dict(text="Actual Time by Category (mins)", font=dict(color="#ccd6f6", size=12)))
            st.plotly_chart(fig_cat_bar, use_container_width=True, config={"displayModeBar": False})
        with c_b:
            fig_cat_pie = go.Figure(go.Pie(
                labels=[str(r["category"]).title() for _, r in cat_df_7.iterrows()],
                values=[float(r["actual_mins"]) for _, r in cat_df_7.iterrows()],
                hole=0.55,
                marker_colors=[cat_colors_map.get(str(r["category"]), "#8892b0") for _, r in cat_df_7.iterrows()],
                textfont_size=10,
                hoverinfo="label+value+percent",
            ))
            apply_theme(fig_cat_pie, height=220, showlegend=True)
            fig_cat_pie.update_layout(legend=dict(orientation="h", y=-0.15, font=dict(size=10)))
            st.plotly_chart(fig_cat_pie, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No category data yet for this week.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MONTHLY TRACKER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    monthly_df = get_monthly_data()

    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.markdown("<div class='section-header'>📅 Monthly Heatmap — Task Activity</div>",
                    unsafe_allow_html=True)

        # Build full month calendar
        today_obj  = date.today()
        month_start = date(today_obj.year, today_obj.month, 1)
        month_end   = date(today_obj.year, today_obj.month + 1 if today_obj.month < 12 else 1,
                           1) - timedelta(days=1)
        all_days_m  = [month_start + timedelta(days=i) for i in range((month_end - month_start).days + 1)]

        # Create week-based grid for heatmap
        weeks, week_row = [], []
        for d in all_days_m:
            if d.weekday() == 0 and week_row:
                weeks.append(week_row); week_row = []
            week_row.append(d)
        if week_row:
            weeks.append(week_row)

        # Fill gaps
        padded_weeks = []
        for w in weeks:
            start_offset = w[0].weekday()
            padded = [None] * start_offset + w
            while len(padded) < 7:
                padded.append(None)
            padded_weeks.append(padded)

        df_dict = {}
        for _, row in monthly_df.iterrows():
            df_dict[row["date"]] = {"done": int(row["done"]), "total": int(row["total"]), "pct": float(row["avg_pct"])}

        # Heatmap z-values
        z_vals, text_vals, hover_vals = [], [], []
        for w in padded_weeks:
            z_row, t_row, h_row = [], [], []
            for d in w:
                if d is None:
                    z_row.append(None); t_row.append(""); h_row.append("")
                else:
                    info = df_dict.get(d.isoformat(), {"done": 0, "total": 0, "pct": 0})
                    z_row.append(info["pct"])
                    t_row.append(str(d.day))
                    h_row.append(f"{d.strftime('%b %d')}<br>Done: {info['done']}/{info['total']}<br>{info['pct']:.0f}%")
            z_vals.append(z_row); text_vals.append(t_row); hover_vals.append(h_row)

        fig_heatmap = go.Figure(go.Heatmap(
            z=z_vals,
            text=text_vals,
            texttemplate="%{text}",
            hovertext=hover_vals,
            hoverinfo="text",
            colorscale=[[0,"#0d1117"],[0.2,"#064e3b"],[0.5,"#0f6e56"],[0.8,"#1d9e75"],[1.0,"#64ffda"]],
            zmin=0, zmax=100,
            showscale=True,
            colorbar=dict(thickness=10, tickfont=dict(color="#8892b0", size=10)),
            xgap=3, ygap=3,
        ))
        apply_theme(fig_heatmap, height=240,
            xaxis=dict(tickvals=list(range(7)), ticktext=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                       gridcolor="#1a3358", linecolor="#1a3358", tickcolor="#1a3358"),
            yaxis=dict(visible=False),
            title=dict(text=f"Completion % Heatmap — {today_obj.strftime('%B %Y')}",
                       font=dict(color="#ccd6f6", size=13)),
        )
        st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": False})

        # Month trend bar
        st.markdown("<div class='section-header'>📊 Daily Done vs Total — This Month</div>",
                    unsafe_allow_html=True)
        if not monthly_df.empty:
            fig_month = make_subplots(specs=[[{"secondary_y": True}]])
            fig_month.add_trace(go.Bar(
                x=monthly_df["date"].tolist(),
                y=monthly_df["total"].tolist(),
                name="Total", marker_color="#1a3358", opacity=0.7,
            ), secondary_y=False)
            fig_month.add_trace(go.Bar(
                x=monthly_df["date"].tolist(),
                y=monthly_df["done"].tolist(),
                name="Done", marker_color=DONE_COL,
            ), secondary_y=False)
            fig_month.add_trace(go.Scatter(
                x=monthly_df["date"].tolist(),
                y=monthly_df["avg_pct"].tolist(),
                mode="lines+markers",
                name="Avg %",
                line=dict(color=MED_COL, width=2),
                marker=dict(size=5),
            ), secondary_y=True)
            apply_theme(fig_month, height=240, barmode="overlay")
            fig_month.update_yaxes(range=[0, 105], secondary_y=True,
                                   ticksuffix="%", gridcolor="#1a3358")
            st.plotly_chart(fig_month, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data for this month yet.")

    with c2:
        st.markdown("<div class='section-header'>📈 Month-over-Month KPIs</div>",
                    unsafe_allow_html=True)

        total_m = int(monthly_df["total"].sum()) if not monthly_df.empty else 0
        done_m  = int(monthly_df["done"].sum())  if not monthly_df.empty else 0
        eff_m   = done_m / total_m * 100 if total_m else 0
        active_days = len(monthly_df[monthly_df["total"] > 0]) if not monthly_df.empty else 0

        kpis = [
            ("Total tasks", total_m, "#57cbff"),
            ("Completed",   done_m,  "#64ffda"),
            ("Efficiency",  f"{eff_m:.0f}%", MED_COL),
            ("Active days", active_days, HIGH_COL),
        ]
        for label, val, col in kpis:
            st.markdown(f"""
            <div class='metric-card' style='margin-bottom:8px'>
                <div class='metric-label'>{label}</div>
                <div style='font-size:24px;font-weight:700;color:{col};margin:4px 0'>{val}</div>
            </div>""", unsafe_allow_html=True)

        # 6-month REAL trend (Phase 4: replaced simulated data)
        st.markdown("<div class='section-header' style='margin-top:14px'>📉 6-Month Efficiency Trend</div>",
                    unsafe_allow_html=True)
        six_m_data = get_six_month_real_data()
        six_months_labels = [d["month"] for d in six_m_data]
        six_month_vals = [d["efficiency"] for d in six_m_data]
        six_month_totals = [d["total"] for d in six_m_data]
        # Build colors: real data = blue, missing (None) = grey
        bar_clrs_6m = [BLUE_COL if v is not None else "#1a3358" for v in six_month_vals]
        display_vals = [v if v is not None else 0 for v in six_month_vals]
        fig_6m = go.Figure()
        fig_6m.add_trace(go.Bar(
            x=six_months_labels, y=display_vals,
            marker_color=bar_clrs_6m,
            name="Efficiency %",
            customdata=six_month_totals,
            hovertemplate="%{x}<br>Efficiency: %{y:.0f}%<br>Total tasks: %{customdata}<extra></extra>"
        ))
        fig_6m.add_trace(go.Scatter(
            x=six_months_labels, y=display_vals,
            mode="lines+markers",
            line=dict(color=DONE_COL, width=2, dash="dot"),
            marker=dict(size=6, color=DONE_COL),
            name="Trend",
            hoverinfo="skip"
        ))
        apply_theme(fig_6m, height=210, barmode="group")
        fig_6m.update_yaxes(range=[0, 110], ticksuffix="%")
        st.plotly_chart(fig_6m, use_container_width=True, config={"displayModeBar": False})
        # Show data completeness note
        has_data = sum(1 for v in six_month_vals if v is not None)
        if has_data < 6:
            st.markdown(f"<div style='font-size:11px;color:#4a5568;margin-top:4px'>📌 Data available for {has_data}/6 months — grey bars indicate months with no recorded tasks.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FLEXIBILITY & RECOVERY
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.markdown("<div class='section-header'>🔄 Flexibility Log — If Plans Fail</div>",
                    unsafe_allow_html=True)
        st.markdown("""
        <div class='flex-note'>
            <b style='color:#64ffda'>Rule:</b> Plans are allowed to bend — but not break.
            Log what went wrong, understand why, then redistribute smartly.
            Consistency over perfection.
        </div>""", unsafe_allow_html=True)

        with st.form("flex_form"):
            what_failed = st.text_area("❌ What task/plan failed today?",
                                       placeholder="e.g. Didn't finish the project report...")
            why_failed  = st.text_area("🤔 Why did it fail?",
                                       placeholder="e.g. Unexpected meeting took 2 hours...")
            realloc     = st.text_area("♻️ How will you reallocate?",
                                       placeholder="e.g. Moving it to tomorrow morning as first task...")
            if st.form_submit_button("📝 Save Reflection", use_container_width=True):
                if what_failed:
                    log_flex(what_failed, why_failed, realloc)
                    st.success("Reflection saved. Every setback is data.")
                    st.rerun()

        # Show past logs
        flex_logs = get_flex_logs()
        if not flex_logs.empty:
            st.markdown("<div class='section-header' style='margin-top:16px'>📚 Past Reflections</div>",
                        unsafe_allow_html=True)
            for _, row in flex_logs.iterrows():
                st.markdown(f"""
                <div class='flex-note' style='margin-bottom:8px'>
                    <span style='color:#8892b0;font-size:11px'>{row['date']}</span><br>
                    <span style='color:#dc2626;font-weight:600'>What failed:</span> {row['what_failed']}<br>
                    <span style='color:#ffd700;font-weight:600'>Why:</span> {row['why_failed'] or '—'}<br>
                    <span style='color:#64ffda;font-weight:600'>Reallocation:</span> {row['reallocation'] or '—'}
                </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-header'>⚖️ Flexibility Rules</div>",
                    unsafe_allow_html=True)

        rules = [
            ("✅ Allowed",     "#64ffda", "Move up to 2 low/medium tasks per day to tomorrow."),
            ("✅ Allowed",     "#64ffda", "Adjust time estimates freely — real data beats guesses."),
            ("⚠️ Caution",     "#ffd700", "If you reschedule the same High Priority task 3× in a row, it triggers a mandatory review."),
            ("⚠️ Caution",     "#ffd700", "Never skip 2 full days in a row — even 1 task counts."),
            ("❌ Not allowed", "#dc2626", "Deleting a High Priority task without a written reason."),
            ("❌ Not allowed", "#dc2626", "Rescheduling all tasks every day — that is not planning, it is avoidance."),
        ]
        for label, col, text in rules:
            st.markdown(f"""
            <div style='background:#101828;border:1px solid {col}22;border-left:3px solid {col};
                        border-radius:8px;padding:10px 14px;margin-bottom:8px'>
                <span style='font-size:12px;font-weight:700;color:{col}'>{label}</span>
                <div style='font-size:12px;color:#a8b2d8;margin-top:4px'>{text}</div>
            </div>""", unsafe_allow_html=True)

        # Plan vs Actual chart (today)
        st.markdown("<div class='section-header' style='margin-top:16px'>⏱ Plan vs Actual — Today</div>",
                    unsafe_allow_html=True)
        if not today_tasks.empty:
            planned_by_pri = today_tasks.groupby("priority")["est_mins"].sum()
            actual_by_pri  = today_tasks.groupby("priority")["actual_mins"].sum()
            pris = ["high", "medium", "low"]
            fig_pva = go.Figure()
            fig_pva.add_trace(go.Bar(
                y=[p.title() for p in pris],
                x=[planned_by_pri.get(p, 0) for p in pris],
                name="Planned", orientation="h",
                marker_color=[PRI_COLORS[p] for p in pris], opacity=0.4,
            ))
            fig_pva.add_trace(go.Bar(
                y=[p.title() for p in pris],
                x=[actual_by_pri.get(p, 0) for p in pris],
                name="Actual", orientation="h",
                marker_color=[PRI_COLORS[p] for p in pris],
            ))
            apply_theme(fig_pva, height=220, barmode="overlay")
            fig_pva.update_xaxes(title="Minutes")
            st.plotly_chart(fig_pva, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — LONG-TERM GOALS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.markdown("<div class='section-header'>🎯 Active Long-Term Goals</div>", unsafe_allow_html=True)

        goals = get_goals()
        if goals.empty:
            st.info("No goals yet. Add your first long-term goal on the right.")
        else:
            for _, g in goals.iterrows():
                gid   = int(g["id"])
                prog  = float(g["progress"])
                dl    = g["deadline"]
                cat   = g["category"]
                status = g.get("status", "active") if "status" in g else "active"
                color_map = {"career":"#57cbff","project":"#ffd700","health":"#64ffda",
                             "learning":"#dc2626","personal":"#c084fc","other":"#8892b0"}
                gcol  = color_map.get(cat, "#8892b0")

                days_left = None
                try:
                    days_left = (datetime.strptime(dl, "%Y-%m-%d").date() - date.today()).days
                except:
                    pass

                # Milestone completion calculation
                ms_df = get_goal_milestones(gid)
                total_ms = len(ms_df)
                done_ms = int(ms_df["completed"].sum()) if total_ms > 0 else 0
                ms_pct = (done_ms / total_ms * 100) if total_ms > 0 else 0

                # Contributing tasks & time invested calculation
                gtasks_df = get_goal_tasks(gid)
                total_gtasks = len(gtasks_df)
                done_gtasks = int(gtasks_df["completed"].sum()) if total_gtasks > 0 else 0
                time_invested_mins = float(gtasks_df["actual_mins"].sum()) if total_gtasks > 0 else 0.0

                # Staleness check: days since last task
                last_task_date_str = gtasks_df["date"].max() if total_gtasks > 0 else None
                days_since_active = None
                if last_task_date_str:
                    try:
                        days_since_active = (date.today() - datetime.strptime(last_task_date_str, "%Y-%m-%d").date()).days
                    except:
                        pass

                is_stale = (days_since_active is not None and days_since_active >= 4 and status == "active")

                # Effort planned vs actual
                planned_effort_mins = float(gtasks_df["est_mins"].sum()) if total_gtasks > 0 else 0.0

                # Overdue milestone count
                overdue_ms = 0
                if total_ms > 0:
                    for _, ms_row in ms_df.iterrows():
                        if not ms_row["completed"] and ms_row["target_date"]:
                            try:
                                if datetime.strptime(ms_row["target_date"], "%Y-%m-%d").date() < date.today():
                                    overdue_ms += 1
                            except:
                                pass

                st.markdown(f"""
                <div class='goal-card' style='border-left: 4px solid {gcol};'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                        <div>
                            <div class='goal-title'>
                                {g['title']}
                                <span class='badge' style='background:{gcol}22;color:{gcol};border:1px solid {gcol}55;margin-left:8px'>{cat.title()}</span>
                                {"<span class='badge badge-high' style='margin-left:6px'>⚠️ Attention Needed (Inactive 4+ days)</span>" if is_stale else ""}
                                {f"<span class='badge badge-high' style='margin-left:6px'>⏰ {overdue_ms} Overdue Milestone{'s' if overdue_ms>1 else ''}</span>" if overdue_ms > 0 else ""}
                            </div>
                            <div class='goal-deadline' style='margin-top:4px'>
                                🗓 Deadline: <b>{dl}</b> &nbsp;·&nbsp;
                                {"⏳ " + str(days_left) + " days left" if days_left is not None else ""} &nbsp;·&nbsp;
                                🚩 Milestones: <b>{done_ms}/{total_ms}</b> ({ms_pct:.0f}%) &nbsp;·&nbsp;
                                ⏱ Invested: <b>{int(time_invested_mins//60)}h {int(time_invested_mins%60)}m</b> (Plan: {int(planned_effort_mins//60)}h {int(planned_effort_mins%60)}m)
                            </div>
                            {f"<div style='font-size:12px;color:#a8b2d8;margin-top:6px'><b>Outcome:</b> {g['desired_outcome']}</div>" if g.get("desired_outcome") else ""}
                            {f"<div style='font-size:12px;color:#8892b0;margin-top:2px'><b>Motivation:</b> {g['motivation']}</div>" if g.get("motivation") else ""}
                            {f"<div style='font-size:12px;color:#ffd700;margin-top:2px'><b>⚡ Next Action:</b> {g['next_action']}</div>" if g.get("next_action") else ""}
                            {f"<div style='font-size:12px;color:#ef4444;margin-top:2px'><b>🚧 Blockers:</b> {g['blockers']}</div>" if g.get("blockers") else ""}
                        </div>
                        <div style='text-align:right'>
                            <span style='font-size:22px;font-weight:700;color:{gcol}'>{prog:.0f}%</span>
                            <div style='font-size:10px;color:#8892b0'>{ 'Verified from Milestones' if total_ms > 0 else 'Manual Estimate' }</div>
                        </div>
                    </div>
                    <div class='prog-wrap' style='margin-top:12px;height:8px'>
                        <div style='width:{prog}%;background:linear-gradient(90deg,{gcol},{gcol}88);
                                    height:100%;border-radius:4px;transition:width 0.4s'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Quick Progress & Milestone Syncer
                gu1, gu2, gu3, gu4 = st.columns([3, 1.2, 1.2, 1])
                with gu1:
                    new_prog = st.slider("Progress %", 0, 100, int(prog), 5,
                                         key=f"gprog_{gid}", label_visibility="collapsed")
                with gu2:
                    if st.button("💾 Save %", key=f"gsave_{gid}"):
                        update_goal_progress(gid, new_prog)
                        st.rerun()
                with gu3:
                    sync_label = f"⚡ Sync ({ms_pct:.0f}%)" if total_ms > 0 else "⚡ Sync"
                    if st.button(sync_label, key=f"gsync_{gid}", help="Set progress to calculated milestone completion %"):
                        if total_ms > 0:
                            update_goal_progress(gid, round(ms_pct, 1))
                            st.rerun()
                with gu4:
                    if st.button("🗑 Del", key=f"gdel_{gid}"):
                        delete_goal(gid)
                        st.rerun()

                # Milestone Management & Contributing Tasks Expander
                with st.expander(f"🚩 Milestones, Tasks & Details for '{g['title']}'"):
                    m_tab1, m_tab2, m_tab3 = st.tabs(["Milestones Breakdown", "Contributing Tasks", "Edit Goal Details"])

                    with m_tab1:
                        if not ms_df.empty:
                            for _, ms in ms_df.iterrows():
                                mid = int(ms["id"])
                                m_done = bool(ms["completed"])
                                is_ms_overdue = False
                                if not m_done and ms["target_date"]:
                                    try:
                                        is_ms_overdue = datetime.strptime(ms["target_date"], "%Y-%m-%d").date() < date.today()
                                    except:
                                        pass

                                mc1, mc2, mc3 = st.columns([4, 1.2, 0.8])
                                with mc1:
                                    overdue_tag = "<span style='color:#ef4444;font-size:11px;font-weight:600'>[OVERDUE]</span> " if is_ms_overdue else ""
                                    st.markdown(f"""
                                    <div style='display:flex;align-items:center;gap:8px'>
                                        <span style='font-size:14px'>{"✅" if m_done else "⏳"}</span>
                                        <span style='font-size:13px;color:{"#64ffda" if m_done else "#ccd6f6"};{"text-decoration:line-through;opacity:0.6" if m_done else ""}'>{ms['title']}</span>
                                        <span style='font-size:11px;color:#8892b0'>({overdue_tag}{ms['target_date'] or 'No date'})</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with mc2:
                                    toggle_label = "Mark Pending" if m_done else "Mark Done"
                                    if st.button(toggle_label, key=f"ms_tog_{mid}"):
                                        toggle_milestone(mid, not m_done)
                                        # Auto sync goal progress if milestones exist
                                        new_done = done_ms + (-1 if m_done else 1)
                                        auto_pct = round((new_done / total_ms) * 100, 1)
                                        update_goal_progress(gid, auto_pct)
                                        st.rerun()
                                with mc3:
                                    if st.button("🗑", key=f"ms_del_{mid}", help="Delete milestone"):
                                        delete_milestone(mid)
                                        st.rerun()
                        else:
                            st.info("No milestones added yet. Break down this goal into actionable checkpoints below.")

                        # Add new milestone form
                        with st.form(f"add_ms_form_{gid}", clear_on_submit=True):
                            st.markdown("<div style='font-size:12px;font-weight:600;color:#64ffda;margin-top:6px'>➕ Add New Milestone</div>", unsafe_allow_html=True)
                            ms_title = st.text_input("Milestone Title", placeholder="e.g. Complete Discrete Mathematics modules")
                            ms_target = st.date_input("Target Date", value=date.today() + timedelta(days=45), key=f"ms_date_{gid}")
                            if st.form_submit_button("Add Milestone", use_container_width=True):
                                if ms_title.strip():
                                    add_milestone(gid, ms_title.strip(), str(ms_target))
                                    st.success("Milestone added!")
                                    st.rerun()

                    with m_tab2:
                        if not gtasks_df.empty:
                            st.markdown(f"<div style='font-size:12px;color:#8892b0;margin-bottom:8px'>Total: <b>{total_gtasks} tasks</b> ({done_gtasks} completed) &nbsp;·&nbsp; Effort: <b>{int(time_invested_mins//60)}h {int(time_invested_mins%60)}m actual</b> / {int(planned_effort_mins//60)}h {int(planned_effort_mins%60)}m planned</div>", unsafe_allow_html=True)
                            for _, t in gtasks_df.head(10).iterrows():
                                t_done = bool(t["completed"])
                                st.markdown(f"""
                                <div style='background:#0d1117;border:1px solid #1a3358;border-radius:6px;padding:6px 10px;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center'>
                                    <div>
                                        <span style='color:{"#64ffda" if t_done else "#ffd700"}'>{"✓" if t_done else "·"}</span>
                                        <span style='font-size:12px;color:#ccd6f6;{"text-decoration:line-through;opacity:0.5" if t_done else ""}'>{t['name']}</span>
                                        <span style='font-size:10px;color:#8892b0'>({t['date']})</span>
                                        {f"<span style='font-size:10px;color:#ef4444'> &nbsp;·&nbsp; 🚧 {t['blockers']}</span>" if ('blockers' in t and t['blockers']) else ""}
                                    </div>
                                    <span style='font-size:11px;color:#8892b0'>{int(t['actual_mins'])}m actual / {int(t['est_mins'])}m plan</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No tasks have been linked to this goal yet. When adding daily tasks in the sidebar, select this goal in the dropdown.")

                    with m_tab3:
                        with st.form(f"edit_goal_details_{gid}"):
                            st.markdown("<div style='font-size:12px;font-weight:600;color:#57cbff'>✏️ Update Goal Details & Alignment</div>", unsafe_allow_html=True)
                            eg_title = st.text_input("Goal Title", value=g['title'])
                            eg_desc  = st.text_area("Description & Scope", value=g.get('description', ''), height=60)
                            
                            egc1, egc2 = st.columns(2)
                            with egc1:
                                cur_cat_idx = ["career","project","health","learning","personal","other"].index(cat) if cat in ["career","project","health","learning","personal","other"] else 0
                                eg_cat = st.selectbox("Category", ["career","project","health","learning","personal","other"], index=cur_cat_idx, key=f"eg_cat_{gid}")
                                eg_dl_val = date.today() + timedelta(days=90)
                                try:
                                    eg_dl_val = datetime.strptime(dl, "%Y-%m-%d").date()
                                except:
                                    pass
                                eg_dl = st.date_input("Deadline", value=eg_dl_val, key=f"eg_dl_{gid}")
                            with egc2:
                                eg_mot = st.text_input("Core Motivation", value=g.get('motivation', ''))
                                eg_out = st.text_input("Desired Outcome", value=g.get('desired_outcome', ''))

                            eg_next = st.text_input("Recommended Next Action", value=g.get('next_action', ''))
                            eg_block = st.text_input("Current Blockers", value=g.get('blockers', ''))
                            
                            if st.form_submit_button("💾 Save Goal Changes", use_container_width=True):
                                update_goal_details(
                                    goal_id=gid,
                                    title=eg_title.strip(),
                                    deadline=str(eg_dl),
                                    category=eg_cat,
                                    description=eg_desc.strip(),
                                    progress=float(g['progress']),
                                    motivation=eg_mot.strip(),
                                    desired_outcome=eg_out.strip(),
                                    success_criteria=g.get('success_criteria', ''),
                                    status=status,
                                    blockers=eg_block.strip(),
                                    next_action=eg_next.strip()
                                )
                                st.success("Goal updated!")
                                st.rerun()

    with c2:
        st.markdown("<div class='section-header'>➕ Add New Long-Term Goal</div>", unsafe_allow_html=True)
        with st.form("add_goal_form", clear_on_submit=True):
            g_title = st.text_input("Goal Title", placeholder="e.g. Master Distributed Systems")
            g_desc  = st.text_area("Description & Scope", height=60, placeholder="Concrete description of what mastery entails...")
            g_cat   = st.selectbox("Category", ["career","project","health","learning","personal","other"])
            g_dl    = st.date_input("Target Deadline", value=date.today() + timedelta(days=180))
            g_out   = st.text_input("Desired Outcome", placeholder="e.g. Architect and deploy high-availability clusters")
            g_mot   = st.text_input("Core Motivation ('Why this matters')", placeholder="e.g. Foundation for senior systems engineering roles")
            g_next  = st.text_input("Recommended Next Action", placeholder="e.g. Read Raft consensus algorithm paper")
            g_prog  = st.slider("Current Progress %", 0, 100, 0, 5)
            
            if st.form_submit_button("🎯 Add Long-Term Goal", use_container_width=True):
                if g_title.strip():
                    add_goal(g_title.strip(), str(g_dl), g_cat, g_desc, g_prog,
                             motivation=g_mot.strip(), desired_outcome=g_out.strip(), next_action=g_next.strip())
                    st.success("Goal added!")
                    st.rerun()

        # Goal radar chart
        goals = get_goals()
        if len(goals) >= 3:
            st.markdown("<div class='section-header' style='margin-top:16px'>🕸 Multi-Dimensional Goal Radar</div>",
                        unsafe_allow_html=True)
            names = goals["title"].str[:18].tolist()
            progs = goals["progress"].tolist()
            names_closed = names + [names[0]]
            progs_closed = progs + [progs[0]]
            fig_radar = go.Figure(go.Scatterpolar(
                r=progs_closed,
                theta=names_closed,
                fill="toself",
                fillcolor="rgba(100,255,218,0.12)",
                line=dict(color=DONE_COL, width=2),
                marker=dict(size=6, color=DONE_COL),
            ))
            apply_theme(fig_radar, height=280,
                polar=dict(
                    bgcolor="#0d1117",
                    radialaxis=dict(range=[0, 100], tickfont=dict(size=9, color="#8892b0"),
                                    gridcolor="#1a3358", linecolor="#1a3358"),
                    angularaxis=dict(tickfont=dict(size=10, color="#ccd6f6"), gridcolor="#1a3358"),
                ),
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

        # Strategy Bridge Callout
        st.markdown("""
        <div style='background:#101828;border:1px solid #0f6e5633;border-left:3px solid #64ffda;
                    border-radius:8px;padding:14px 16px;margin-top:8px'>
            <div style='font-size:13px;font-weight:600;color:#64ffda'>🌉 The Execution Hierarchy</div>
            <div style='font-size:12px;color:#a8b2d8;margin-top:6px;line-height:1.6'>
                <b>Life Mission</b> → <b>Long-Term Goal</b> → <b>Milestones</b> → <b>Daily Tasks</b>.
                <br><br>
                Break large aspirations into 2–4 checkpoints. Link daily micro-tasks to goals in the sidebar.
                If a goal has no linked activity for <b>4+ days</b>, it triggers an attention alert.
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — 1-MONTH RECORD
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    today_obj = date.today()

    # ── Month / Year selector ──
    sel_c1, sel_c2, sel_c3 = st.columns([1, 1, 4])
    with sel_c1:
        sel_year  = st.selectbox("Year",  list(range(today_obj.year - 2, today_obj.year + 1)),
                                 index=2, key="mr_year")
    with sel_c2:
        month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                       "Jul","Aug","Sep","Oct","Nov","Dec"]
        sel_month = st.selectbox("Month", list(range(1, 13)),
                                 index=today_obj.month - 1,
                                 format_func=lambda m: month_names[m-1],
                                 key="mr_month")

    mr_df, mr_start, mr_end = get_month_record(sel_year, sel_month)
    month_label = f"{month_names[sel_month-1]} {sel_year}"

    # ── Top KPI strip ──────────────────────────────────────────────────────
    total_m  = int(mr_df["total"].sum())
    done_m   = int(mr_df["done"].sum())
    left_m   = int(mr_df["left_tasks"].sum())
    eff_m    = round(done_m / total_m * 100, 1) if total_m else 0
    active_d = int((mr_df["total"] > 0).sum())
    days_in  = (mr_end - mr_start).days + 1
    best_day_row = mr_df.loc[mr_df["done"].idxmax()] if total_m else None
    best_day_str = datetime.strptime(best_day_row["date"], "%Y-%m-%d").strftime("%d %b") if best_day_row is not None and best_day_row["done"] > 0 else "—"
    best_day_cnt = int(best_day_row["done"]) if best_day_row is not None else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpi_data = [
        (k1, "Total Tasks",     total_m,          "#57cbff"),
        (k2, "✅ Done",          done_m,           "#64ffda"),
        (k3, "⏳ Left / Pending", left_m,           "#dc2626"),
        (k4, "Efficiency",      f"{eff_m}%",       "#ffd700"),
        (k5, "Active Days",     f"{active_d}/{days_in}", "#c084fc"),
        (k6, f"Best Day ({best_day_str})", best_day_cnt, "#fb923c"),
    ]
    for col, label, val, color in kpi_data:
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div style='font-size:26px;font-weight:700;color:{color};margin:4px 0'>{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

    # ── Row 1: Calendar grid + stacked bar ────────────────────────────────
    row1_l, row1_r = st.columns([3, 2], gap="medium")

    with row1_l:
        st.markdown(f"<div class='section-header'>📅 Daily Calendar — Done vs Left — {month_label}</div>",
                    unsafe_allow_html=True)

        # Build calendar grid
        first_weekday = mr_start.weekday()   # 0=Mon
        cal_days = [None] * first_weekday
        for i in range((mr_end - mr_start).days + 1):
            cal_days.append(mr_start + timedelta(days=i))
        while len(cal_days) % 7 != 0:
            cal_days.append(None)

        # Build lookup
        day_data = {row["date"]: row for _, row in mr_df.iterrows()}

        # Render calendar HTML
        cal_html = """
        <style>
        .cal-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
        .cal-head { text-align:center; font-size:11px; font-weight:600;
                    color:#4a5568; padding:4px 0; text-transform:uppercase; letter-spacing:.5px; }
        .cal-cell { border-radius:8px; padding:8px 6px; text-align:center;
                    border:1px solid #1a3358; min-height:72px; position:relative; }
        .cal-empty { border:none; background:transparent; }
        .cal-num  { font-size:12px; font-weight:600; color:#8892b0; }
        .cal-done { font-size:18px; font-weight:700; }
        .cal-left { font-size:11px; margin-top:2px; }
        .cal-bar  { height:4px; border-radius:2px; margin-top:6px; overflow:hidden;
                    background:#1a3358; }
        .cal-bar-fill { height:100%; border-radius:2px; }
        </style>
        <div class='cal-grid'>
        """
        for day_name in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]:
            cal_html += f"<div class='cal-head'>{day_name}</div>"

        for d in cal_days:
            if d is None:
                cal_html += "<div class='cal-cell cal-empty'></div>"
                continue
            ds     = d.isoformat()
            is_today = (d == today_obj)
            info   = day_data.get(ds)
            done_c = int(info["done"])       if info is not None else 0
            left_c = int(info["left_tasks"]) if info is not None else 0
            total_c= int(info["total"])      if info is not None else 0
            pct    = float(info["avg_pct"])  if info is not None else 0

            if is_today:
                bg = "#0d2340"; border = "2px solid #1d4ed8"
            elif total_c == 0:
                bg = "#0d1117"; border = "1px solid #1a3358"
            elif pct >= 80:
                bg = "#052414"; border = "1px solid #065f46"
            elif pct >= 40:
                bg = "#1a1400"; border = "1px solid #7c5c00"
            else:
                bg = "#1a0505"; border = "1px solid #7f1d1d"

            done_col_c = "#64ffda" if pct >= 80 else "#ffd700" if pct >= 40 else "#dc2626"
            left_col_c = "#dc2626" if left_c > 0 else "#64ffda"
            bar_w      = int(pct)

            cal_html += f"""
            <div class='cal-cell' style='background:{bg};border:{border}'>
                <div class='cal-num'>{d.day}{"📍" if is_today else ""}</div>
                <div class='cal-done' style='color:{done_col_c}'>{done_c}</div>
                <div class='cal-left' style='color:{left_col_c}'>
                    {"⏳ "+str(left_c)+" left" if left_c > 0 else ("✅" if total_c > 0 else "—")}
                </div>
                <div class='cal-bar'>
                    <div class='cal-bar-fill' style='width:{bar_w}%;background:{done_col_c}'></div>
                </div>
            </div>"""

        cal_html += "</div>"
        st.markdown(cal_html, unsafe_allow_html=True)

        st.markdown("""
        <div style='display:flex;gap:16px;margin-top:10px;font-size:11px;color:#4a5568'>
            <span>🟢 ≥80% done</span>
            <span>🟡 40–79% done</span>
            <span>🔴 &lt;40% done</span>
            <span>⬛ No tasks</span>
            <span>📍 Today</span>
        </div>""", unsafe_allow_html=True)

    with row1_r:
        st.markdown(f"<div class='section-header'>📊 Done vs Left — Each Day</div>",
                    unsafe_allow_html=True)

        active_df = mr_df[mr_df["total"] > 0].copy()
        if not active_df.empty:
            x_labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%d %b")
                        for d in active_df["date"]]
            fig_dvl = go.Figure()
            fig_dvl.add_trace(go.Bar(
                x=x_labels, y=active_df["done"].tolist(),
                name="Done ✅",
                marker_color=DONE_COL,
                marker_line_width=0,
            ))
            fig_dvl.add_trace(go.Bar(
                x=x_labels, y=active_df["left_tasks"].tolist(),
                name="Left ⏳",
                marker_color="#dc2626",
                marker_line_width=0,
            ))
            apply_theme(fig_dvl, height=320, barmode="stack",
                        title=dict(text="Tasks per Active Day", font=dict(color="#ccd6f6", size=12)))
            fig_dvl.update_xaxes(tickangle=-45, tickfont=dict(size=9))
            st.plotly_chart(fig_dvl, use_container_width=True, config={"displayModeBar": False})

            # Mini legend
            st.markdown(f"""
            <div style='display:flex;gap:16px;font-size:12px;margin-top:4px'>
                <span style='color:{DONE_COL}'>■ Done: {done_m}</span>
                <span style='color:#dc2626'>■ Left: {left_m}</span>
                <span style='color:#8892b0'>Total: {total_m}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("No task data for this month yet.")

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── Row 2: Efficiency trend + Priority breakdown ───────────────────────
    row2_l, row2_r = st.columns([3, 2], gap="medium")

    with row2_l:
        st.markdown(f"<div class='section-header'>📈 Daily Completion % Trend — {month_label}</div>",
                    unsafe_allow_html=True)

        if not active_df.empty:
            x_all = [datetime.strptime(d, "%Y-%m-%d").strftime("%d %b") for d in mr_df["date"]]
            pct_all = mr_df["avg_pct"].tolist()
            colors_bar = [
                DONE_COL if p >= 80 else MED_COL if p >= 40 else "#dc2626" if p > 0 else "#1a3358"
                for p in pct_all
            ]
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=x_all, y=pct_all,
                marker_color=colors_bar,
                name="Completion %",
                hovertemplate="%{x}<br>%{y:.0f}%<extra></extra>",
            ))
            fig_trend.add_trace(go.Scatter(
                x=x_all, y=pct_all,
                mode="lines",
                line=dict(color="#c084fc", width=2, dash="dot"),
                name="Trend",
                hoverinfo="skip",
            ))
            fig_trend.add_hline(y=80, line_dash="dash", line_color=DONE_COL,
                                annotation_text="80% goal",
                                annotation_font_color=DONE_COL,
                                annotation_font_size=10)
            apply_theme(fig_trend, height=260)
            fig_trend.update_yaxes(range=[0, 110], ticksuffix="%")
            fig_trend.update_xaxes(tickangle=-45, tickfont=dict(size=9))
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data yet for this month.")

    with row2_r:
        st.markdown(f"<div class='section-header'>🎯 Priority Breakdown — {month_label}</div>",
                    unsafe_allow_html=True)

        high_total = int(mr_df["high_total"].sum())
        high_done  = int(mr_df["high_done"].sum())
        med_total  = int(mr_df["med_total"].sum())
        med_done   = int(mr_df["med_done"].sum())
        low_total  = int(mr_df["low_total"].sum())
        low_done   = int(mr_df["low_done"].sum())

        for pri_label, pri_done, pri_total, col in [
            ("🔴 High Priority",   high_done, high_total, HIGH_COL),
            ("🟡 Medium Priority", med_done,  med_total,  MED_COL),
            ("🔵 Low Priority",    low_done,  low_total,  LOW_COL),
        ]:
            pct_pri = round(pri_done / pri_total * 100) if pri_total else 0
            left_pri = pri_total - pri_done
            st.markdown(f"""
            <div style='background:#101828;border:1px solid #1e3a5f;border-radius:10px;
                        padding:12px 14px;margin-bottom:8px'>
                <div style='display:flex;justify-content:space-between;margin-bottom:6px'>
                    <span style='font-size:13px;font-weight:600;color:#ccd6f6'>{pri_label}</span>
                    <span style='font-size:12px;color:{col};font-weight:700'>{pct_pri}%</span>
                </div>
                <div style='display:flex;justify-content:space-between;font-size:11px;color:#8892b0;margin-bottom:6px'>
                    <span>✅ Done: <b style='color:{col}'>{pri_done}</b></span>
                    <span>⏳ Left: <b style='color:#dc2626'>{left_pri}</b></span>
                    <span>Total: {pri_total}</span>
                </div>
                <div style='background:#1a3358;border-radius:4px;height:8px;overflow:hidden'>
                    <div style='width:{pct_pri}%;background:{col};height:100%;border-radius:4px'></div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Donut done vs left
        if total_m > 0:
            fig_pie = go.Figure(go.Pie(
                labels=["Done ✅", "Left ⏳"],
                values=[done_m, left_m],
                hole=0.6,
                marker_colors=[DONE_COL, "#dc2626"],
                textfont_size=11,
                hoverinfo="label+value+percent",
            ))
            apply_theme(fig_pie, height=200,
                showlegend=True,
                annotations=[dict(text=f"{eff_m}%", x=0.5, y=0.5,
                                  font_size=22, font_color="#ccd6f6", showarrow=False)],
            )
            fig_pie.update_layout(legend=dict(orientation="h", y=-0.1, font=dict(size=11)))
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── Row 3: Per-day detail table ───────────────────────────────────────
    st.markdown(f"<div class='section-header'>📋 Full Day-by-Day Record — {month_label}</div>",
                unsafe_allow_html=True)

    if not mr_df[mr_df["total"] > 0].empty:
        table_df = mr_df[mr_df["total"] > 0].copy()
        table_df["Day"] = table_df["date"].apply(
            lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y"))
        table_df["Total"]      = table_df["total"].astype(int)
        table_df["Done ✅"]    = table_df["done"].astype(int)
        table_df["Left ⏳"]   = table_df["left_tasks"].astype(int)
        table_df["Progress"]   = table_df["avg_pct"].apply(lambda x: f"{x:.0f}%")
        table_df["Est. Time"]  = table_df["total_est_mins"].apply(
            lambda m: f"{int(m)//60}h {int(m)%60}m")
        table_df["Actual Time"]= table_df["total_actual_mins"].apply(
            lambda m: f"{int(m)//60}h {int(m)%60}m")
        table_df["Status"] = table_df["avg_pct"].apply(
            lambda p: "🏆 Excellent" if p >= 80 else "💪 Good" if p >= 60 else "⚠️ Partial" if p > 0 else "📭 No data")

        display_cols = ["Day","Total","Done ✅","Left ⏳","Progress","Est. Time","Actual Time","Status"]
        st.dataframe(
            table_df[display_cols].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Day":         st.column_config.TextColumn("Day", width="medium"),
                "Total":       st.column_config.NumberColumn("Total",    width="small"),
                "Done ✅":     st.column_config.NumberColumn("Done ✅",  width="small"),
                "Left ⏳":    st.column_config.NumberColumn("Left ⏳",  width="small"),
                "Progress":    st.column_config.TextColumn("Progress",   width="small"),
                "Est. Time":   st.column_config.TextColumn("Est. Time",  width="small"),
                "Actual Time": st.column_config.TextColumn("Actual",     width="small"),
                "Status":      st.column_config.TextColumn("Status",     width="medium"),
            },
        )

        # Export CSV
        csv_data = table_df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Month Report (CSV)",
            data=csv_data,
            file_name=f"karma_record_{sel_year}_{sel_month:02d}.csv",
            mime="text/csv",
        )
    else:
        st.info(f"No task data recorded for {month_label}. Start adding tasks from the sidebar!")

    # ── Row 4: Best / worst day callout ───────────────────────────────────
    if total_m > 0:
        best_row  = mr_df.loc[mr_df["done"].idxmax()]
        worst_row = mr_df[mr_df["total"] > 0].loc[mr_df[mr_df["total"] > 0]["done"].idxmin()] if active_d > 0 else None

        r4c1, r4c2, r4c3 = st.columns(3)
        with r4c1:
            bd = datetime.strptime(best_row["date"], "%Y-%m-%d").strftime("%A, %d %b")
            st.markdown(f"""
            <div style='background:#052414;border:1px solid #065f46;border-left:4px solid {DONE_COL};
                        border-radius:10px;padding:14px 16px;margin-top:12px'>
                <div style='font-size:11px;color:#8892b0;text-transform:uppercase;letter-spacing:.8px'>🏆 Best Day</div>
                <div style='font-size:16px;font-weight:700;color:{DONE_COL};margin:6px 0'>{bd}</div>
                <div style='font-size:13px;color:#a8b2d8'>{int(best_row["done"])} tasks completed</div>
            </div>""", unsafe_allow_html=True)

        with r4c2:
            avg_daily = round(done_m / active_d, 1) if active_d else 0
            st.markdown(f"""
            <div style='background:#0d1a30;border:1px solid #1e3a5f;border-left:4px solid {BLUE_COL};
                        border-radius:10px;padding:14px 16px;margin-top:12px'>
                <div style='font-size:11px;color:#8892b0;text-transform:uppercase;letter-spacing:.8px'>📊 Daily Average</div>
                <div style='font-size:16px;font-weight:700;color:{BLUE_COL};margin:6px 0'>{avg_daily} tasks/day</div>
                <div style='font-size:13px;color:#a8b2d8'>Across {active_d} active days</div>
            </div>""", unsafe_allow_html=True)

        with r4c3:
            days_left_in_month = (mr_end - today_obj).days
            projected = round(done_m + avg_daily * days_left_in_month) if days_left_in_month > 0 else done_m
            st.markdown(f"""
            <div style='background:#1a1400;border:1px solid #7c5c00;border-left:4px solid {MED_COL};
                        border-radius:10px;padding:14px 16px;margin-top:12px'>
                <div style='font-size:11px;color:#8892b0;text-transform:uppercase;letter-spacing:.8px'>🔮 Projected Month Total</div>
                <div style='font-size:16px;font-weight:700;color:{MED_COL};margin:6px 0'>~{projected} tasks</div>
                <div style='font-size:13px;color:#a8b2d8'>{days_left_in_month} days remaining</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — PERFORMANCE DIAGNOSIS (PHASE 4)
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d1b2a,#16213e);border:1px solid #1a3358;
                border-left:4px solid #c084fc;border-radius:12px;padding:18px 22px;margin-bottom:18px'>
        <div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#c084fc'>🔬 Evidence-Based Performance Diagnosis</div>
        <div style='font-size:15px;font-weight:600;color:#f8fafc;margin-top:6px'>Why Am I Not Getting Results?</div>
        <div style='font-size:12px;color:#8892b0;margin-top:4px;line-height:1.5'>
            This section analyzes your recorded data to surface <b>observed patterns</b>, <b>possible bottlenecks</b>,
            and <b>evidence-backed recovery suggestions</b>. All conclusions are based only on your actual task records.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Analysis period selector ──
    diag_c0, diag_c0b, _ = st.columns([1, 1, 3])
    with diag_c0:
        diag_period = st.selectbox("Analysis Period", [7, 14, 30, 60, 90],
                                   index=2, format_func=lambda x: f"Last {x} days",
                                   key="diag_period")

    an_df, an_start, an_end = get_analytics_data(days=diag_period)
    period_label = f"{an_start.strftime('%d %b')} – {an_end.strftime('%d %b %Y')}"

    if an_df.empty:
        st.info(f"No task data recorded in the last {diag_period} days. Add tasks to generate a diagnosis.")
    else:
        # ── Core metrics for the period ──────────────────────────────────────
        total_an = len(an_df)
        done_an = int(an_df["completed"].sum())
        completion_rate = round(done_an / total_an * 100, 1) if total_an > 0 else 0
        avg_pct_an = round(float(an_df["pct_done"].mean()), 1)
        total_planned_an = float(an_df["est_mins"].sum())
        total_actual_an  = float(an_df["actual_mins"].sum())
        days_with_tasks = an_df["date"].nunique()
        days_with_full_completion = 0
        for d_val, grp in an_df.groupby("date"):
            if grp["completed"].sum() >= len(grp) * 0.6:
                days_with_full_completion += 1
        consistency_rate = round(days_with_full_completion / diag_period * 100, 1)

        # High priority completion
        high_df = an_df[an_df["priority"] == "high"]
        high_rate = round(high_df["completed"].mean() * 100, 1) if not high_df.empty else 0
        med_df  = an_df[an_df["priority"] == "medium"]
        med_rate  = round(med_df["completed"].mean() * 100, 1) if not med_df.empty else 0
        low_df  = an_df[an_df["priority"] == "low"]
        low_rate  = round(low_df["completed"].mean() * 100, 1) if not low_df.empty else 0

        # Estimation accuracy
        est_acc_full = get_estimation_accuracy(days=diag_period)
        avg_acc_ratio = round(est_acc_full["accuracy_ratio"].mean(), 1) if not est_acc_full.empty else 0

        # ── KPI strip ────────────────────────────────────────────────────────
        st.markdown(f"<div style='font-size:11px;color:#4a5568;margin-bottom:10px'>Period: <b style='color:#8892b0'>{period_label}</b></div>", unsafe_allow_html=True)
        dk1, dk2, dk3, dk4, dk5, dk6 = st.columns(6)
        diag_kpis = [
            (dk1, "Tasks Planned",     total_an,          "#57cbff"),
            (dk2, "Tasks Completed",   done_an,           "#64ffda"),
            (dk3, "Completion Rate",   f"{completion_rate}%", MED_COL if completion_rate >= 60 else HIGH_COL),
            (dk4, "Consistency",       f"{consistency_rate}%", DONE_COL if consistency_rate >= 60 else MED_COL),
            (dk5, "High-Pri Done",     f"{high_rate}%",    HIGH_COL),
            (dk6, "Est. Accuracy",     f"{avg_acc_ratio}%", DONE_COL if 85 <= avg_acc_ratio <= 115 else MED_COL),
        ]
        for col_kpi, lbl, val, clr in diag_kpis:
            with col_kpi:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>{lbl}</div>
                    <div style='font-size:22px;font-weight:700;color:{clr};margin:4px 0'>{val}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

        # ── Two-column layout ─────────────────────────────────────────────────
        diag_left, diag_right = st.columns([3, 2], gap="medium")

        with diag_left:
            # ── Rolling Consistency Chart ──────────────────────────────────
            st.markdown("<div class='section-header'>📈 Rolling 7-Day Consistency Rate</div>", unsafe_allow_html=True)
            roll_df = get_rolling_consistency(days=max(diag_period, 30))
            active_roll = roll_df[roll_df["active"]].copy()
            if not active_roll.empty:
                fig_roll = go.Figure()
                fig_roll.add_trace(go.Bar(
                    x=roll_df["date"].tolist(),
                    y=roll_df["completion_rate"].tolist(),
                    name="Daily completion %",
                    marker_color="#1a3358",
                    opacity=0.5,
                ))
                fig_roll.add_trace(go.Scatter(
                    x=roll_df["date"].tolist(),
                    y=roll_df["rolling_7d"].tolist(),
                    mode="lines",
                    name="7-day rolling avg",
                    line=dict(color=DONE_COL, width=2.5),
                ))
                fig_roll.add_hline(y=60, line_dash="dot", line_color=MED_COL,
                                   annotation_text="60% streak threshold",
                                   annotation_font_color=MED_COL, annotation_font_size=10)
                apply_theme(fig_roll, height=240)
                fig_roll.update_yaxes(range=[0, 110], ticksuffix="%")
                fig_roll.update_xaxes(tickangle=-45, tickfont=dict(size=9))
                st.plotly_chart(fig_roll, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Not enough active days to show consistency trend.")

            # ── Estimation Accuracy Scatter ────────────────────────────────
            st.markdown("<div class='section-header' style='margin-top:16px'>⏱ Planned vs Actual Time — Accuracy Deep Dive</div>", unsafe_allow_html=True)
            if not est_acc_full.empty:
                fig_acc = go.Figure()
                acc_colors = [
                    DONE_COL if 85 <= r <= 115 else MED_COL if 70 <= r <= 130 else HIGH_COL
                    for r in est_acc_full["accuracy_ratio"]
                ]
                fig_acc.add_trace(go.Scatter(
                    x=est_acc_full["date"].tolist(),
                    y=est_acc_full["planned_mins"].tolist(),
                    mode="lines+markers",
                    name="Planned",
                    line=dict(color="#1a3358", width=2),
                    marker=dict(size=5, color="#4a6fa5"),
                ))
                fig_acc.add_trace(go.Scatter(
                    x=est_acc_full["date"].tolist(),
                    y=est_acc_full["actual_mins"].tolist(),
                    mode="lines+markers",
                    name="Actual",
                    line=dict(color=MED_COL, width=2),
                    marker=dict(size=5, color=MED_COL),
                    fill="tonexty",
                    fillcolor="rgba(255,215,0,0.06)",
                ))
                apply_theme(fig_acc, height=230)
                fig_acc.update_xaxes(tickangle=-45, tickfont=dict(size=9))
                fig_acc.update_yaxes(title="Minutes")
                st.plotly_chart(fig_acc, use_container_width=True, config={"displayModeBar": False})

                # Accuracy summary row
                over_estimated = int((est_acc_full["accuracy_ratio"] < 85).sum())
                under_estimated = int((est_acc_full["accuracy_ratio"] > 115).sum())
                accurate = len(est_acc_full) - over_estimated - under_estimated
                st.markdown(f"""
                <div style='display:flex;gap:10px;margin-top:6px'>
                    <div style='flex:1;background:#101828;border:1px solid #064e3b;border-radius:8px;padding:10px 12px;text-align:center'>
                        <div style='font-size:18px;font-weight:700;color:{DONE_COL}'>{accurate}</div>
                        <div style='font-size:10px;color:#8892b0;margin-top:2px'>Accurate days<br>(within ±15%)</div>
                    </div>
                    <div style='flex:1;background:#101828;border:1px solid #1a3358;border-radius:8px;padding:10px 12px;text-align:center'>
                        <div style='font-size:18px;font-weight:700;color:#57cbff'>{over_estimated}</div>
                        <div style='font-size:10px;color:#8892b0;margin-top:2px'>Over-estimated<br>(did more than planned)</div>
                    </div>
                    <div style='flex:1;background:#101828;border:1px solid #7f1d1d;border-radius:8px;padding:10px 12px;text-align:center'>
                        <div style='font-size:18px;font-weight:700;color:{HIGH_COL}'>{under_estimated}</div>
                        <div style='font-size:10px;color:#8892b0;margin-top:2px'>Under-estimated<br>(took more time)</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("No estimation data available. Add estimated minutes to tasks for accuracy tracking.")

            # ── Priority completion trend ───────────────────────────────────
            st.markdown("<div class='section-header' style='margin-top:18px'>🎯 Priority-Wise Completion Rates</div>", unsafe_allow_html=True)
            pri_data = [
                ("🔴 High",   len(high_df), int(high_df["completed"].sum()), high_rate,   HIGH_COL),
                ("🟡 Medium", len(med_df),  int(med_df["completed"].sum()),  med_rate,    MED_COL),
                ("🔵 Low",    len(low_df),  int(low_df["completed"].sum()),  low_rate,    LOW_COL),
            ]
            for p_lbl, p_total, p_done, p_rate, p_col in pri_data:
                if p_total == 0:
                    continue
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>
                    <span style='font-size:12px;color:#ccd6f6;min-width:80px'>{p_lbl}</span>
                    <div class='prog-wrap' style='flex:1;height:12px'>
                        <div style='width:{p_rate}%;background:{p_col};height:100%;border-radius:6px'></div>
                    </div>
                    <span style='font-size:12px;color:{p_col};min-width:60px;text-align:right'>{p_rate}% ({p_done}/{p_total})</span>
                </div>""", unsafe_allow_html=True)

        with diag_right:
            # ── Diagnostic Report ─────────────────────────────────────────
            st.markdown("<div class='section-header'>🧠 Evidence-Based Diagnostic Report</div>", unsafe_allow_html=True)

            findings = []

            # Finding 1: Low overall completion
            if completion_rate < 60:
                findings.append({
                    "severity": "high",
                    "icon": "⚠️",
                    "title": "Low Overall Completion Rate",
                    "evidence": f"Only {completion_rate}% of planned tasks were completed over {diag_period} days.",
                    "likely_cause": "Possible bottleneck: over-planning relative to actual capacity, or low follow-through on listed tasks.",
                    "confidence": "Strongly supported" if completion_rate < 40 else "Moderately supported",
                    "suggestion": f"Experiment: Reduce daily task list by 20% for one week and compare completion rate."
                })
            elif completion_rate >= 80:
                findings.append({
                    "severity": "good",
                    "icon": "🏆",
                    "title": "Strong Task Completion",
                    "evidence": f"Completion rate of {completion_rate}% over {diag_period} days — well above the 60% consistency threshold.",
                    "likely_cause": "Observed pattern: effective planning and follow-through.",
                    "confidence": "Strongly supported",
                    "suggestion": "Maintain current planning approach. Consider increasing goal challenge level."
                })

            # Finding 2: High-priority lagging
            if high_rate < 60 and not high_df.empty:
                findings.append({
                    "severity": "high",
                    "icon": "🔴",
                    "title": "High-Priority Tasks Under-Completed",
                    "evidence": f"Only {high_rate}% of high-priority tasks were completed ({int(high_df['completed'].sum())}/{len(high_df)} tasks).",
                    "likely_cause": "Possible bottleneck: interruptions, unclear scope, or tasks marked high-priority but not actionable.",
                    "confidence": "Moderately supported",
                    "suggestion": "Ensure each high-priority task has a clear, concrete next action. Check blockers field for recurring issues."
                })

            # Finding 3: Estimation accuracy
            if avg_acc_ratio > 130 and not est_acc_full.empty:
                findings.append({
                    "severity": "medium",
                    "icon": "⏰",
                    "title": "Systematic Time Under-Estimation",
                    "evidence": f"Actual time averaged {avg_acc_ratio:.0f}% of planned time — tasks consistently taking longer than estimated.",
                    "likely_cause": "Observed pattern: tasks are harder or more complex than initially assessed. Known as 'planning fallacy'.",
                    "confidence": "Moderately supported",
                    "suggestion": f"Apply a 1.3× buffer to future time estimates. If average is {avg_acc_ratio:.0f}%, planned 60 min tasks likely take ~{int(60 * avg_acc_ratio / 100)} min."
                })
            elif avg_acc_ratio < 70 and avg_acc_ratio > 0 and not est_acc_full.empty:
                findings.append({
                    "severity": "low",
                    "icon": "📊",
                    "title": "Actual Time Below Planned",
                    "evidence": f"Actual time was only {avg_acc_ratio:.0f}% of planned — possibly tasks completed faster, or actual_mins not always recorded.",
                    "likely_cause": "Possible explanations: tasks completed efficiently, or actual time logging is inconsistent.",
                    "confidence": "Possible — needs more data",
                    "suggestion": "Verify that actual_mins is recorded consistently for every completed task."
                })

            # Finding 4: Low consistency
            if consistency_rate < 50:
                findings.append({
                    "severity": "high",
                    "icon": "📉",
                    "title": "Inconsistent Active Days",
                    "evidence": f"You had ≥60% completion on only {days_with_full_completion}/{diag_period} days ({consistency_rate}%).",
                    "likely_cause": "Possible bottleneck: irregular work patterns, energy variance, or recurring interruptions on specific days.",
                    "confidence": "Strongly supported" if consistency_rate < 30 else "Moderately supported",
                    "suggestion": "Identify 2–3 days per week where consistency is lowest. Check flex_log for recurring root causes."
                })

            # Finding 5: Category imbalance
            cat_df_an = get_category_breakdown(days=diag_period)
            if not cat_df_an.empty:
                study_row = cat_df_an[cat_df_an["category"] == "study"]
                work_row = cat_df_an[cat_df_an["category"] == "work"]
                if not study_row.empty and not work_row.empty:
                    study_mins = float(study_row.iloc[0]["actual_mins"])
                    work_mins = float(work_row.iloc[0]["actual_mins"])
                    if work_mins > 0 and study_mins / (work_mins + study_mins) < 0.15:
                        findings.append({
                            "severity": "medium",
                            "icon": "📚",
                            "title": "Study Time Allocation Low",
                            "evidence": f"Study tasks received {study_mins:.0f} min actual vs {work_mins:.0f} min work in this period.",
                            "likely_cause": "Observed pattern: learning activities may be deprioritized in favor of immediate work tasks.",
                            "confidence": "Possible",
                            "suggestion": "Block at least one dedicated study session per day. Link study tasks to your learning goals."
                        })

            # Flex log patterns
            _, flex_df_an = get_blockers_analysis(days=diag_period)
            if not flex_df_an.empty and len(flex_df_an) >= 3:
                findings.append({
                    "severity": "medium",
                    "icon": "🔄",
                    "title": f"Recurring Flexibility Events ({len(flex_df_an)} in period)",
                    "evidence": f"{len(flex_df_an)} reflection entries recorded in the last {diag_period} days — indicating repeated plan failures.",
                    "likely_cause": "Possible bottleneck: structural planning issue, recurring interruptions, or workload exceeding capacity.",
                    "confidence": "Moderately supported",
                    "suggestion": "Review common themes in Flexibility & Recovery tab. Address the root cause that appears most frequently."
                })

            # No findings = good
            if not findings:
                findings.append({
                    "severity": "good",
                    "icon": "✅",
                    "title": "No Critical Issues Detected",
                    "evidence": f"Completion rate: {completion_rate}%, Consistency: {consistency_rate}%, High-priority rate: {high_rate}% — all within acceptable thresholds.",
                    "likely_cause": "Your current planning and execution patterns are functioning well.",
                    "confidence": "Supported by recorded data",
                    "suggestion": "Continue current approach. Consider increasing the challenge level on long-term goals."
                })

            severity_colors = {"high": HIGH_COL, "medium": MED_COL, "low": LOW_COL, "good": DONE_COL}
            severity_bg = {"high": "#2d0a0a", "medium": "#2d2000", "low": "#0a1a2d", "good": "#052414"}

            for f in findings:
                sev_col = severity_colors.get(f["severity"], "#8892b0")
                sev_bg  = severity_bg.get(f["severity"], "#101828")
                st.markdown(f"""
                <div style='background:{sev_bg};border:1px solid {sev_col}33;border-left:4px solid {sev_col};
                            border-radius:10px;padding:14px 16px;margin-bottom:12px'>
                    <div style='font-size:13px;font-weight:700;color:{sev_col}'>{f['icon']} {f['title']}</div>
                    <div style='font-size:12px;color:#a8b2d8;margin-top:6px'><b>Evidence:</b> {f['evidence']}</div>
                    <div style='font-size:12px;color:#8892b0;margin-top:4px'><b>Observed pattern:</b> {f['likely_cause']}</div>
                    <div style='font-size:11px;color:#4a5568;margin-top:3px'>Confidence: <i>{f['confidence']}</i></div>
                    <div style='background:#0d1117;border:1px solid #1e3a5f;border-radius:6px;padding:8px 12px;margin-top:8px;
                                font-size:12px;color:#64ffda'>
                        💡 <b>Suggested experiment:</b> {f['suggestion']}
                    </div>
                </div>""", unsafe_allow_html=True)

            # ── Root-Cause Self-Assessment ─────────────────────────────────
            st.markdown("<div class='section-header' style='margin-top:16px'>📝 Root-Cause Reflection Logger</div>", unsafe_allow_html=True)
            with st.form("root_cause_form", clear_on_submit=True):
                rc_cat = st.selectbox("What category best describes why tasks were missed?", [
                    "Unrealistic planning", "Poor time estimation", "Unexpected work",
                    "Distraction", "Lack of clarity", "Missing prerequisite / skill",
                    "Low energy or inadequate rest", "Avoidance or procrastination",
                    "Competing priorities", "External dependency", "Technical issue", "Other"
                ], key="rc_cat")
                rc_note = st.text_area("Brief reflection (what would change the outcome?)",
                                       placeholder="e.g. I consistently underestimate how long code reviews take...",
                                       height=70, key="rc_note")
                rc_experiment = st.text_input("Small experiment to test next week",
                                              placeholder="e.g. Block 1h calendar for reviews each morning",
                                              key="rc_exp")
                if st.form_submit_button("💾 Log Root-Cause Reflection", use_container_width=True):
                    if rc_note.strip():
                        log_flex(f"[Root-cause: {rc_cat}]", rc_note.strip(), rc_experiment.strip() or "TBD")
                        st.success("Root-cause reflection saved to Flexibility Log.")
                        st.rerun()

        # ── Category breakdown deep dive ───────────────────────────────────────
        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-header'>🗂 Category Breakdown — Last {diag_period} Days</div>", unsafe_allow_html=True)
        cat_df_full = get_category_breakdown(days=diag_period)
        if not cat_df_full.empty:
            cat_table_rows = []
            for _, cr in cat_df_full.iterrows():
                cr_rate = round(cr["done_tasks"] / cr["total_tasks"] * 100, 1) if cr["total_tasks"] > 0 else 0
                cat_table_rows.append({
                    "Category": str(cr["category"]).title(),
                    "Tasks": int(cr["total_tasks"]),
                    "Done": int(cr["done_tasks"]),
                    "Completion": f"{cr_rate:.0f}%",
                    "Planned (h)": f"{int(cr['planned_mins'])//60}h {int(cr['planned_mins'])%60}m",
                    "Actual (h)": f"{int(cr['actual_mins'])//60}h {int(cr['actual_mins'])%60}m",
                    "Avg Progress": f"{cr['avg_pct']:.0f}%"
                })
            cat_table_df = pd.DataFrame(cat_table_rows)
            st.dataframe(cat_table_df, use_container_width=True, hide_index=True,
                column_config={
                    "Category":    st.column_config.TextColumn("Category",     width="medium"),
                    "Tasks":       st.column_config.NumberColumn("Tasks",      width="small"),
                    "Done":        st.column_config.NumberColumn("Done ✅",    width="small"),
                    "Completion":  st.column_config.TextColumn("Completion",   width="small"),
                    "Planned (h)": st.column_config.TextColumn("Planned",      width="small"),
                    "Actual (h)":  st.column_config.TextColumn("Actual",       width="small"),
                    "Avg Progress":st.column_config.TextColumn("Avg Progress", width="small"),
                })
        else:
            st.info("No category data for this period.")

        # ── Recovery recommendations callout ───────────────────────────────────
        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
        low_consistency = consistency_rate < 50
        low_completion  = completion_rate < 60
        low_high_pri    = high_rate < 60 and not high_df.empty
        bad_estimation  = avg_acc_ratio > 130 and avg_acc_ratio > 0

        rec_items = []
        if low_completion and low_consistency:
            rec_items.append(("🔴 Priority Recovery", HIGH_COL, "Both completion rate and consistency are below threshold. Start with a 'minimum viable day' plan: commit to just 1–2 essential tasks, complete them, then add more if energy allows."))
        if low_high_pri:
            rec_items.append(("🟡 High-Priority Focus", MED_COL, f"High-priority task completion is {high_rate}%. Audit your high-priority list — each item should be specific, actionable, and completable in one session. Remove anything vague."))
        if bad_estimation:
            rec_items.append(("⏱ Estimation Calibration", LOW_COL, f"You consistently underestimate task durations (avg {avg_acc_ratio:.0f}% of planned). For the next 2 weeks, multiply all time estimates by 1.3× and observe the difference."))
        if not low_completion and not low_consistency and not low_high_pri:
            rec_items.append(("✅ Maintain Momentum", DONE_COL, "Your metrics are healthy. Focus on advancing long-term goal milestones and ensuring daily tasks are linked to goals for maximum strategic alignment."))

        if rec_items:
            st.markdown("<div class='section-header'>💡 Recovery & Improvement Recommendations</div>", unsafe_allow_html=True)
            for r_title, r_col, r_text in rec_items:
                st.markdown(f"""
                <div style='background:#101828;border:1px solid {r_col}33;border-left:4px solid {r_col};
                            border-radius:10px;padding:14px 16px;margin-bottom:10px'>
                    <div style='font-size:13px;font-weight:700;color:{r_col}'>{r_title}</div>
                    <div style='font-size:12px;color:#a8b2d8;margin-top:6px;line-height:1.6'>{r_text}</div>
                </div>""", unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;padding:14px 0;border-top:1px solid #1a3358'>
    <span style='font-size:12px;color:#4a5568'>
        🕉️ &nbsp;
        <span style='font-family:Noto Sans Devanagari;color:#f5c51888'>कर्म प्रधान</span>
        &nbsp;·&nbsp; Karma-Driven Productivity Dashboard
        &nbsp;·&nbsp; Built with Streamlit + Plotly
        &nbsp;·&nbsp; <span style='color:#c084fc88'>Phase 4: Analytics & Diagnosis Active</span>
    </span>
</div>
""", unsafe_allow_html=True)