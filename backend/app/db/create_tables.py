import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def create_tables():
    schema_path = Path(__file__).parent / "schema.sql"
    schema_sql = schema_path.read_text()

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
        print("Tables created successfully")
    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
