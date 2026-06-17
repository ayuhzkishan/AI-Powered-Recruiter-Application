import psycopg2
from psycopg2 import pool
import json
from app.core.config import settings

# Connection pool — reuses connections instead of opening a new one per request
_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=settings.DATABASE_URL,
)


def get_conn():
    """Borrow a connection from the pool."""
    return _pool.getconn()


def release_conn(conn):
    """Return a connection to the pool."""
    _pool.putconn(conn)


def execute_one(query: str, params: tuple = ()):
    """
    Run a query and return one row as a dict.

    THE RULE: `query` is always a fixed string with %s placeholders.
              `params` is always a tuple of values — never string-formatted in.

    SAFE:   execute_one("SELECT * FROM users WHERE email = %s", (email,))
    UNSAFE: execute_one(f"SELECT * FROM users WHERE email = '{email}'")  ← NEVER DO THIS
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)  # psycopg2 escapes params automatically
            row = cur.fetchone()
            if row and cur.description:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None
    finally:
        release_conn(conn)


def execute_many(query: str, params: tuple = ()):
    """Run a query and return all rows as list of dicts."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            if rows and cur.description:
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
    finally:
        release_conn(conn)


def execute_write(query: str, params: tuple = ()):
    """Run an INSERT / UPDATE / DELETE and commit."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_conn(conn)


def execute_returning(query: str, params: tuple = ()):
    """Run an INSERT ... RETURNING and get back the new row as dict."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            if row and cur.description:
                columns = [desc[0] for desc in cur.description]
                result = dict(zip(columns, row))
            else:
                result = None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        release_conn(conn)
