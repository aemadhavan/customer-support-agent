"""
Database connection and user authentication helper.
Satisfies SPEC §8 and TECHNICAL Stage 3 login requirement.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        dbname=os.getenv("POSTGRES_DB", "customer_support")
    )

def authenticate_user(email: str, password: str = None) -> bool:
    """Verifies user exists in users table (and matches demo password if provided)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if password:
                cur.execute("SELECT user_id, full_name FROM users WHERE email = %s AND password = %s", (email, password))
            else:
                cur.execute("SELECT user_id, full_name FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return row is not None
    except Exception as e:
        print(f"Database error during authentication: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def get_user_info(email: str) -> dict:
    """Fetches user details (user_id, full_name, is_premium_customer)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT email, full_name, is_premium_customer FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            if row:
                return {
                    "user_id": row[0],
                    "full_name": row[1] or "",
                    "is_premium": bool(row[2])
                }
            return None
    except Exception:
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()

