import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_db():
    conn = psycopg2.connect(
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT,
        database=Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )
    return conn

def execute(query, params=None):
    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if 'RETURNING' in query.upper():
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            return result[0] if result else None
        else:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            cursor.close()
            return None
    finally:
        conn.close()

def fetchone(query, params=None):
    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    finally:
        conn.close()

def fetchall(query, params=None):
    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows] if rows else []
    finally:
        conn.close()
