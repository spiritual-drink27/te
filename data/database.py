"""
database.py – All SQLite interactions for the GHG Tracker.

Responsibilities:
  - Schema creation & migration
  - User (profile) CRUD
  - Daily emission insert / upsert / retrieval
  - Aggregation helpers (weekly, monthly)
  - Leaderboard queries
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent / "data" / "ghg_tracker.db"


# ─────────────────────────────────────────────
#  Connection helper
# ─────────────────────────────────────────────
@contextmanager
def _db():
    """Context-managed SQLite connection with WAL mode for concurrency."""
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  Schema
# ─────────────────────────────────────────────
def _has_unique_constraint() -> bool:
    """Check if daily_emissions already has the UNIQUE(employee_id, date) constraint."""
    with _db() as conn:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='daily_emissions'"
        ).fetchall()
        # A real UNIQUE constraint shows up as a unique index in sqlite_master
        for row in rows:
            if row[0] and "UNIQUE" in row[0].upper():
                return True
        # Also check if the table was created with inline UNIQUE
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE name='daily_emissions'"
        ).fetchone()
        return row is not None and "UNIQUE" in (row[0] or "").upper()


def _migrate_daily_emissions():
    """
    Migrate old daily_emissions table (no UNIQUE constraint) to a new one
    that has UNIQUE(employee_id, date), deduplicating by keeping the latest
    created_at per (employee_id, date).
    """
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS daily_emissions_new (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id             TEXT NOT NULL,
                date                    TEXT NOT NULL,
                commute_emission        REAL DEFAULT 0,
                ac_emission             REAL DEFAULT 0,
                pc_emission             REAL DEFAULT 0,
                meal_emission           REAL DEFAULT 0,
                printer_emission        REAL DEFAULT 0,
                official_visit_emission REAL DEFAULT 0,
                total_emission          REAL DEFAULT 0,
                created_at              TEXT DEFAULT (datetime('now')),
                UNIQUE(employee_id, date)
            );

            INSERT OR REPLACE INTO daily_emissions_new
                (employee_id, date, commute_emission, ac_emission, pc_emission,
                 meal_emission, printer_emission, official_visit_emission,
                 total_emission, created_at)
            SELECT employee_id, date, commute_emission, ac_emission, pc_emission,
                   meal_emission, printer_emission, official_visit_emission,
                   total_emission, created_at
            FROM daily_emissions
            ORDER BY created_at ASC;

            DROP TABLE daily_emissions;
            ALTER TABLE daily_emissions_new RENAME TO daily_emissions;

            CREATE INDEX IF NOT EXISTS idx_daily_emp_date
                ON daily_emissions(employee_id, date);
        """)


def init_db():
    """Create tables if they don't exist; migrate old schemas; add new columns."""
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                employee_id      TEXT PRIMARY KEY,
                name             TEXT NOT NULL,
                department       TEXT,
                transport_mode   TEXT,
                fuel_type        TEXT DEFAULT 'Petrol',
                mileage          REAL DEFAULT 0,
                commute_distance REAL DEFAULT 0,
                room_occupants   INTEGER DEFAULT 1,
                pc_type          TEXT,
                ac_tonnage       TEXT,
                meal_type        TEXT,
                printer_type     TEXT,
                created_at       TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS daily_emissions (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id             TEXT NOT NULL,
                date                    TEXT NOT NULL,
                commute_emission        REAL DEFAULT 0,
                ac_emission             REAL DEFAULT 0,
                pc_emission             REAL DEFAULT 0,
                meal_emission           REAL DEFAULT 0,
                printer_emission        REAL DEFAULT 0,
                official_visit_emission REAL DEFAULT 0,
                total_emission          REAL DEFAULT 0,
                created_at              TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_daily_emp_date
                ON daily_emissions(employee_id, date);
        """)

    # Non-destructive column migrations for existing databases
    _add_column_if_missing("users", "fuel_type", "TEXT DEFAULT 'Petrol'")

    # Migrate to UNIQUE constraint if not already done
    if not _has_unique_constraint():
        _migrate_daily_emissions()


def _add_column_if_missing(table: str, column: str, definition: str):
    with _db() as conn:
        cols = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
        if column not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


# ─────────────────────────────────────────────
#  Users / Profile
# ─────────────────────────────────────────────
def save_user(employee_id, name, department, transport_mode, fuel_type,
              mileage, commute_distance, room_occupants, pc_type,
              ac_tonnage, meal_type, printer_type):
    with _db() as conn:
        conn.execute("""
            INSERT INTO users
                (employee_id, name, department, transport_mode, fuel_type,
                 mileage, commute_distance, room_occupants, pc_type,
                 ac_tonnage, meal_type, printer_type)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(employee_id) DO UPDATE SET
                name             = excluded.name,
                department       = excluded.department,
                transport_mode   = excluded.transport_mode,
                fuel_type        = excluded.fuel_type,
                mileage          = excluded.mileage,
                commute_distance = excluded.commute_distance,
                room_occupants   = excluded.room_occupants,
                pc_type          = excluded.pc_type,
                ac_tonnage       = excluded.ac_tonnage,
                meal_type        = excluded.meal_type,
                printer_type     = excluded.printer_type
        """, (employee_id, name, department, transport_mode, fuel_type,
              mileage, commute_distance, room_occupants, pc_type,
              ac_tonnage, meal_type, printer_type))


def get_user(employee_id: str) -> dict | None:
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE employee_id = ?", (employee_id,)
        ).fetchone()
    return dict(row) if row else None


def get_all_users() -> pd.DataFrame:
    with _db() as conn:
        return pd.read_sql_query("SELECT * FROM users", conn)


# ─────────────────────────────────────────────
#  Daily Emissions
# ─────────────────────────────────────────────
def upsert_emission(employee_id, date, commute, ac, pc, meal, printer,
                    official_visit, total):
    """Insert or replace emission record for a given employee+date."""
    with _db() as conn:
        conn.execute("""
            INSERT INTO daily_emissions
                (employee_id, date, commute_emission, ac_emission, pc_emission,
                 meal_emission, printer_emission, official_visit_emission, total_emission)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(employee_id, date) DO UPDATE SET
                commute_emission        = excluded.commute_emission,
                ac_emission             = excluded.ac_emission,
                pc_emission             = excluded.pc_emission,
                meal_emission           = excluded.meal_emission,
                printer_emission        = excluded.printer_emission,
                official_visit_emission = excluded.official_visit_emission,
                total_emission          = excluded.total_emission,
                created_at              = datetime('now')
        """, (employee_id, date, commute, ac, pc, meal, printer,
              official_visit, total))


def get_emissions(employee_id: str) -> pd.DataFrame:
    """Return all daily emission rows for one employee, oldest first."""
    with _db() as conn:
        return pd.read_sql_query("""
            SELECT date,
                   commute_emission, ac_emission, pc_emission,
                   meal_emission, printer_emission, official_visit_emission,
                   total_emission
            FROM daily_emissions
            WHERE employee_id = ?
            ORDER BY date ASC
        """, conn, params=(employee_id,))


def get_today_emission(employee_id: str, today: str) -> dict | None:
    with _db() as conn:
        row = conn.execute("""
            SELECT * FROM daily_emissions
            WHERE employee_id = ? AND date = ?
        """, (employee_id, today)).fetchone()
    return dict(row) if row else None


def get_weekly_emission(employee_id: str) -> pd.DataFrame:
    """Last 7 days of emissions for one employee."""
    with _db() as conn:
        return pd.read_sql_query("""
            SELECT date, total_emission,
                   commute_emission, ac_emission, pc_emission,
                   meal_emission, printer_emission, official_visit_emission
            FROM daily_emissions
            WHERE employee_id = ?
              AND date >= date('now', '-6 days')
            ORDER BY date ASC
        """, conn, params=(employee_id,))


def get_monthly_emission(employee_id: str) -> pd.DataFrame:
    with _db() as conn:
        return pd.read_sql_query("""
            SELECT strftime('%Y-%m', date) AS month,
                   SUM(total_emission) AS total_emission
            FROM daily_emissions
            WHERE employee_id = ?
            GROUP BY month
            ORDER BY month ASC
        """, conn, params=(employee_id,))


# ─────────────────────────────────────────────
#  Leaderboard
# ─────────────────────────────────────────────
def get_daily_leaderboard(today: str) -> pd.DataFrame:
    with _db() as conn:
        return pd.read_sql_query("""
            SELECT u.name, u.department,
                   COALESCE(d.total_emission, 0) AS daily_emission
            FROM users u
            LEFT JOIN daily_emissions d
                ON u.employee_id = d.employee_id AND d.date = ?
            ORDER BY daily_emission ASC
        """, conn, params=(today,))


def get_weekly_leaderboard() -> pd.DataFrame:
    with _db() as conn:
        return pd.read_sql_query("""
            SELECT u.name, u.department,
                   COALESCE(SUM(d.total_emission), 0) AS weekly_emission
            FROM users u
            LEFT JOIN daily_emissions d
                ON u.employee_id = d.employee_id
               AND d.date >= date('now', '-6 days')
            GROUP BY u.employee_id
            ORDER BY weekly_emission ASC
        """, conn)
