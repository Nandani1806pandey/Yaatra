import sqlite3
import unittest
import os
import tempfile
from datetime import date

class TestPhase2Mission(unittest.TestCase):
    def setUp(self):
        self.fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.fd)
        conn = sqlite3.connect(self.db_path)
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
            CREATE TABLE IF NOT EXISTS long_term_goals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                deadline    TEXT,
                progress    REAL DEFAULT 0,
                category    TEXT DEFAULT 'career',
                description TEXT DEFAULT '',
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
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_mission_profile_seeding_and_retrieval(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO mission_profile (
                id, life_mission, career_aspirations, learning_goals, personal_growth,
                identity_statement, why_it_matters, what_it_enables, target_outcome, target_date
            ) VALUES (
                1,
                'Master engineering disciplines and gain complete financial independence.',
                'Become a top-tier systems engineer.',
                'Master distributed systems, Linux, and algorithms.',
                'Consistency over intensity.',
                'A disciplined and thoughtful engineer.',
                'Because steady action builds character.',
                'Total autonomy and mastery.',
                'GATE Rank 1st and stable career',
                '2027-02-01'
            )
        """)
        conn.commit()
        
        row = c.execute("SELECT life_mission, career_aspirations, target_date FROM mission_profile WHERE id=1").fetchone()
        self.assertIsNotNone(row)
        self.assertIn("Master engineering", row[0])
        self.assertIn("systems engineer", row[1])
        self.assertEqual(row[2], '2027-02-01')
        conn.close()

    def test_mission_profile_update(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO mission_profile (id, life_mission) VALUES (1, 'Initial mission')")
        conn.commit()
        
        c.execute("""
            UPDATE mission_profile SET
                life_mission = 'Updated mission of excellence',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """)
        conn.commit()
        
        updated = c.execute("SELECT life_mission FROM mission_profile WHERE id=1").fetchone()[0]
        self.assertEqual(updated, 'Updated mission of excellence')
        conn.close()

    def test_daily_intention_upsert(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        today_str = date.today().isoformat()
        
        c.execute("""
            INSERT INTO daily_intentions (date, intention, why_today_matters, energy_level)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                intention = excluded.intention,
                why_today_matters = excluded.why_today_matters,
                energy_level = excluded.energy_level
        """, (today_str, "Deep work on distributed systems", "Key milestone for GATE", 5))
        conn.commit()
        
        row = c.execute("SELECT intention, energy_level FROM daily_intentions WHERE date=?", (today_str,)).fetchone()
        self.assertEqual(row, ("Deep work on distributed systems", 5))
        
        # Upsert test on same date
        c.execute("""
            INSERT INTO daily_intentions (date, intention, why_today_matters, energy_level)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                intention = excluded.intention,
                why_today_matters = excluded.why_today_matters,
                energy_level = excluded.energy_level
        """, (today_str, "Updated intention: focus on SQL and Linux", "Solid foundation", 4))
        conn.commit()
        
        row_updated = c.execute("SELECT intention, energy_level FROM daily_intentions WHERE date=?", (today_str,)).fetchone()
        self.assertEqual(row_updated, ("Updated intention: focus on SQL and Linux", 4))
        conn.close()

    def test_actionable_motivation_bridge(self):
        sample_goals = [
            {"id": 1, "title": "Rank 1st In Gate Exam", "category": "learning", "description": "Stand up for what you believe in"},
            {"id": 2, "title": "Learn Ansible and docker", "category": "learning", "description": "More you learn more you earn"}
        ]
        sample_tasks = [
            {"id": 101, "name": "Solve 20 GATE algorithms problems", "priority": "high", "completed": 0},
            {"id": 102, "name": "Setup docker container for DB", "priority": "medium", "completed": 0}
        ]
        
        top_task = sample_tasks[0]
        matched_goal = sample_goals[0]
        
        message = f"Your goal '{matched_goal['title']}' matters because you are building true mastery. Complete today's task: '{top_task['name']}'."
        self.assertIn("Rank 1st In Gate Exam", message)
        self.assertIn("Solve 20 GATE algorithms problems", message)

if __name__ == "__main__":
    unittest.main()
