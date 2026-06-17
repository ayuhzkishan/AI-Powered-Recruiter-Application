import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def reset_and_create_tables():
    schema_path = Path(__file__).parent / "schema.sql"
    schema_sql = schema_path.read_text()

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            # Drop in reverse dependency order
            cur.execute("""
                DROP TABLE IF EXISTS match_records CASCADE;
                DROP TABLE IF EXISTS ai_analysis CASCADE;
                DROP TABLE IF EXISTS job_descriptions CASCADE;
                DROP TABLE IF EXISTS candidates CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
            """)
            conn.commit()
            print("Old tables dropped.")

            # Recreate from schema
            cur.execute(schema_sql)
        conn.commit()
        print("Tables created successfully from schema.sql")
    finally:
        conn.close()


if __name__ == "__main__":
    reset_and_create_tables()
