import sqlite3
import unittest
import os
import tempfile
from datetime import date

class TestPhase3GoalsHierarchy(unittest.TestCase):
    def setUp(self):
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.fd)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS long_term_goals (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                title            TEXT NOT NULL,
                deadline         TEXT,
                progress         REAL DEFAULT 0,
                category         TEXT DEFAULT 'career',
                description      TEXT DEFAULT '',
                motivation       TEXT DEFAULT '',
                start_date       TEXT DEFAULT '',
                desired_outcome  TEXT DEFAULT '',
                success_criteria TEXT DEFAULT '',
                status           TEXT DEFAULT 'active',
                blockers         TEXT DEFAULT '',
                next_action      TEXT DEFAULT '',
                review_frequency TEXT DEFAULT 'weekly',
                created_at       TEXT DEFAULT CURRENT_TIMESTAMP
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
                goal_id     INTEGER DEFAULT NULL,
                milestone_id INTEGER DEFAULT NULL,
                blockers    TEXT DEFAULT '',
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(goal_id) REFERENCES long_term_goals(id) ON DELETE SET NULL,
                FOREIGN KEY(milestone_id) REFERENCES goal_milestones(id) ON DELETE SET NULL
            );
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_milestone_crud_and_completion_rate(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Insert goal
        c.execute("INSERT INTO long_term_goals (title, deadline, category) VALUES (?, ?, ?)",
                  ("Rank 1st In Gate Exam", "2027-02-01", "learning"))
        goal_id = c.lastrowid

        # Insert 3 milestones
        c.execute("INSERT INTO goal_milestones (goal_id, title, target_date, completed) VALUES (?, ?, ?, 1)",
                  (goal_id, "Complete Discrete Maths & Algorithms", "2026-06-30"))
        c.execute("INSERT INTO goal_milestones (goal_id, title, target_date, completed) VALUES (?, ?, ?, 0)",
                  (goal_id, "Complete Operating Systems & DBMS", "2026-09-30"))
        c.execute("INSERT INTO goal_milestones (goal_id, title, target_date, completed) VALUES (?, ?, ?, 0)",
                  (goal_id, "Mock Test Series & PYQs", "2027-01-15"))
        conn.commit()

        # Calculate milestone completion %
        m_rows = c.execute("SELECT completed FROM goal_milestones WHERE goal_id=?", (goal_id,)).fetchall()
        total_m = len(m_rows)
        done_m = sum(row[0] for row in m_rows)
        pct = (done_m / total_m) * 100

        self.assertEqual(total_m, 3)
        self.assertEqual(done_m, 1)
        self.assertAlmostEqual(pct, 33.333, places=2)
        conn.close()

    def test_task_to_goal_linkage(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO long_term_goals (title, deadline) VALUES ('Learn Ansible and docker', '2026-06-18')")
        goal_id = c.lastrowid

        c.execute("INSERT INTO goal_milestones (goal_id, title) VALUES (?, 'Docker Compose & Multi-stage builds')", (goal_id,))
        m_id = c.lastrowid

        # Create tasks linked to this goal and milestone
        c.execute("INSERT INTO tasks (date, name, priority, goal_id, milestone_id, completed, est_mins, actual_mins) VALUES (?, ?, ?, ?, ?, 1, 60, 50)",
                  ("2026-10-30", "Write Dockerfile for Streamlit app", "high", goal_id, m_id))
        c.execute("INSERT INTO tasks (date, name, priority, goal_id, milestone_id, completed, est_mins, actual_mins) VALUES (?, ?, ?, ?, ?, 0, 45, 0)",
                  ("2026-10-30", "Test multi-stage build optimization", "medium", goal_id, m_id))
        conn.commit()

        # Query tasks for the goal
        tasks_linked = c.execute("SELECT name, completed, actual_mins FROM tasks WHERE goal_id=?", (goal_id,)).fetchall()
        self.assertEqual(len(tasks_linked), 2)
        total_actual_time = sum(t[2] for t in tasks_linked)
        self.assertEqual(total_actual_time, 50)
        conn.close()

    def test_goal_activity_staleness(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO long_term_goals (title, deadline) VALUES ('Inactive Goal Test', '2026-12-31')")
        goal_id = c.lastrowid
        
        # Link a task 5 days ago
        c.execute("INSERT INTO tasks (date, name, priority, goal_id) VALUES ('2026-10-25', 'Old task', 'low', ?)", (goal_id,))
        conn.commit()

        latest_task_date = c.execute("SELECT MAX(date) FROM tasks WHERE goal_id=?", (goal_id,)).fetchone()[0]
        self.assertEqual(latest_task_date, '2026-10-25')
        conn.close()

    def test_overdue_milestones_and_effort_metrics(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO long_term_goals (title, deadline) VALUES ('GATE Exam Prep', '2027-02-01')")
        goal_id = c.lastrowid

        # Insert past target_date uncompleted milestone (overdue) and future completed milestone
        c.execute("INSERT INTO goal_milestones (goal_id, title, target_date, completed) VALUES (?, 'Engineering Math Phase 1', '2026-01-01', 0)", (goal_id,))
        c.execute("INSERT INTO goal_milestones (goal_id, title, target_date, completed) VALUES (?, 'Theory of Computation', '2026-12-01', 1)", (goal_id,))

        # Insert tasks with planned vs actual minutes
        c.execute("INSERT INTO tasks (date, name, priority, goal_id, est_mins, actual_mins, blockers) VALUES ('2026-10-30', 'Calculus Revision', 'high', ?, 120, 150, 'Integration doubt')", (goal_id,))
        c.execute("INSERT INTO tasks (date, name, priority, goal_id, est_mins, actual_mins) VALUES ('2026-10-30', 'Linear Algebra', 'medium', ?, 90, 80)", (goal_id,))
        conn.commit()

        # Check overdue milestone count
        today_str = date.today().isoformat()
        overdue_count = c.execute("SELECT COUNT(*) FROM goal_milestones WHERE goal_id=? AND completed=0 AND target_date < ?", (goal_id, today_str)).fetchone()[0]
        self.assertEqual(overdue_count, 1)

        # Check planned vs actual totals
        effort_row = c.execute("SELECT SUM(est_mins), SUM(actual_mins) FROM tasks WHERE goal_id=?", (goal_id,)).fetchone()
        self.assertEqual(effort_row[0], 210)
        self.assertEqual(effort_row[1], 230)
        conn.close()

if __name__ == "__main__":
    unittest.main()

