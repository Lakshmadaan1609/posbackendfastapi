import os
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Optional

# Load environment variables first
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "zokomomo"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# Connection pool (optional, for better performance)
connection_pool: Optional[pool.ThreadedConnectionPool] = None


def get_db_connection():
    """
    Create a new database connection using psycopg2
    Returns a connection object
    """
    try:
        # Otherwise use individual config values
        conn = psycopg2.connect(**DB_CONFIG)
    
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def get_db_connection_pool(min_conn=1, max_conn=10):
    """
    Create a connection pool for better performance
    """
    global connection_pool
    
    if connection_pool is None:
        try:
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                connection_pool = pool.ThreadedConnectionPool(
                    min_conn, max_conn, database_url
                )
            else:
                connection_pool = pool.ThreadedConnectionPool(
                    min_conn, max_conn, **DB_CONFIG
                )
        except psycopg2.Error as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    return connection_pool


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database connections with automatic cleanup
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        if commit:
            conn.commit()
        else:
            conn.rollback()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def test_connection():
    """
    Test database connection
    Returns dict with connection status
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return {
            "status": "connected",
            "database_version": version[0]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def close_connection_pool():
    """
    Close all connections in the pool
    """
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        connection_pool = None
