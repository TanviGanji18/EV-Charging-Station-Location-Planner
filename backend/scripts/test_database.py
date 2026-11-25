import os
import psycopg

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env", override=True)

try:
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
        connect_timeout=10
    ) as conn:

        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database();")

            print("DATABASE CONNECTION SUCCESSFUL")
            print("Database:", cursor.fetchone()[0])

except psycopg.OperationalError as error:
    print("DATABASE CONNECTION FAILED")
    print(error)
    