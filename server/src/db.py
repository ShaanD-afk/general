import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_URL = os.getenv("DB_URL")


@contextmanager
def get_db():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def query_db(query, args=(), one=False, commit=False):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, args)
    if commit:
        if one:
            result = cur.fetchone()
        else:
            result = cur.fetchall()
        conn.commit()
    else:
        if one:
            result = cur.fetchone()
        else:
            result = cur.fetchall()
    conn.close()
    return result
