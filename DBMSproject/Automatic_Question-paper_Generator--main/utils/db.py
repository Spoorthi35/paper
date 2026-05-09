"""
Database Connection Helper
--------------------------
Supports both MySQL and SQLite backends.
Uses SQLite by default for zero-setup development.
Set USE_MYSQL=true in config to switch to MySQL.
"""

import sqlite3
import os
from config import Config

# Database file path for SQLite
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'smartqgen.db')


def get_db():
    """Get a database connection (SQLite)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # Enable FK support
    return conn


def dict_from_row(row):
    """Convert a sqlite3.Row to a dict."""
    if row is None:
        return None
    return dict(row)


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Execute a SQL query with automatic connection management.

    Args:
        query (str): SQL query string with %s placeholders (auto-converted to ?).
        params (tuple): Parameters for the query.
        fetchone (bool): Return single row as dict.
        fetchall (bool): Return all rows as list of dicts.
        commit (bool): Commit the transaction.

    Returns:
        dict | list[dict] | int | None
    """
    # Convert MySQL-style %s placeholders to SQLite-style ?
    query = query.replace('%s', '?')

    # Convert MySQL-specific syntax to SQLite equivalents
    query = _adapt_query(query)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())

        if fetchone:
            row = cursor.fetchone()
            result = dict_from_row(row)
        elif fetchall:
            rows = cursor.fetchall()
            result = [dict_from_row(r) for r in rows]
        elif commit:
            conn.commit()
            result = cursor.lastrowid
        else:
            result = cursor.rowcount

        return result

    except Exception as e:
        if commit:
            conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def execute_many(query, data_list, commit=True):
    """Execute a query with multiple parameter sets."""
    query = query.replace('%s', '?')
    query = _adapt_query(query)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.executemany(query, data_list)
        if commit:
            conn.commit()
        return cursor.rowcount
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def _adapt_query(query):
    """
    Adapt MySQL-specific SQL syntax to SQLite.
    Handles common differences between the two dialects.
    """
    import re

    # Remove ENUM - SQLite doesn't support it, treat as TEXT
    query = re.sub(r"ENUM\([^)]+\)", "TEXT", query, flags=re.IGNORECASE)

    # Convert FIELD() ordering to CASE WHEN (used in dashboard)
    field_match = re.search(r"ORDER BY FIELD\((\w+),\s*(.+?)\)", query, re.IGNORECASE)
    if field_match:
        col = field_match.group(1)
        values = [v.strip().strip("'\"") for v in field_match.group(2).split(",")]
        case_parts = [f"WHEN '{v}' THEN {i}" for i, v in enumerate(values)]
        case_expr = f"CASE {col} " + " ".join(case_parts) + " END"
        query = query[:field_match.start()] + "ORDER BY " + case_expr + query[field_match.end():]

    # DATE_SUB -> date() function
    query = re.sub(
        r"DATE_SUB\(CURDATE\(\),\s*INTERVAL\s+(\?)\s+YEAR\)",
        r"date('now', '-' || \1 || ' years')",
        query, flags=re.IGNORECASE
    )

    # CURDATE() -> date('now')
    query = re.sub(r"CURDATE\(\)", "date('now')", query, flags=re.IGNORECASE)

    # NOW() -> datetime('now')
    query = re.sub(r"NOW\(\)", "datetime('now')", query, flags=re.IGNORECASE)

    return query
