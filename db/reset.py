"""
Database Reset Helper.
Satisfies SPEC §8, EVALS §2, and Stage 10 database reset requirement.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def reset_db():
    """Resets customer_support database tables and re-seeds deterministic EVALS §2 rows."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        dbname=os.getenv("POSTGRES_DB", "customer_support")
    )
    seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")
    with open(seed_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_db()
    print("Database reset and re-seeded successfully.")
