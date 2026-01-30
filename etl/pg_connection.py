"""Подключение к Postgres: NEON_DATABASE_URL или PG_HOST/PG_PORT/..."""
import os
import psycopg2


def get_pg_connection():
    url = os.getenv("NEON_DATABASE_URL")
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=os.getenv("PG_DB", "neondb"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        sslmode=os.getenv("PG_SSLMODE", "require"),
    )
