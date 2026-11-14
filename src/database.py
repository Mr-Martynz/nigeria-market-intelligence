import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # on your PC, this loads DATABASE_URL from the .env file

def create_connection():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Check your .env file.")
    conn = psycopg2.connect(url)
    print("Connected to Neon database.")
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id             SERIAL PRIMARY KEY,
            date           DATE NOT NULL UNIQUE,
            ngn_per_usd    DOUBLE PRECISION,
            ngn_per_eur    DOUBLE PRECISION,
            ngn_per_gbp    DOUBLE PRECISION,
            usd_pct_change DOUBLE PRECISION,
            usd_7day_avg   DOUBLE PRECISION,
            day_of_week    TEXT,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("Table 'exchange_rates' is ready.")

def to_none_if_nan(value):
    # Pandas uses NaN for "missing". A database wants NULL (None in Python).
    return None if pd.isna(value) else value

def insert_from_dataframe(conn, df):
    cursor = conn.cursor()
    inserted = 0
    try:
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO exchange_rates
                    (date, ngn_per_usd, ngn_per_eur, ngn_per_gbp,
                     usd_pct_change, usd_7day_avg, day_of_week)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE SET
                    ngn_per_usd    = EXCLUDED.ngn_per_usd,
                    ngn_per_eur    = EXCLUDED.ngn_per_eur,
                    ngn_per_gbp    = EXCLUDED.ngn_per_gbp,
                    usd_pct_change = EXCLUDED.usd_pct_change,
                    usd_7day_avg   = EXCLUDED.usd_7day_avg,
                    day_of_week    = EXCLUDED.day_of_week
            """, (
                str(row["date"])[:10],
                to_none_if_nan(row.get("NGN_per_USD")),
                to_none_if_nan(row.get("NGN_per_EUR")),
                to_none_if_nan(row.get("NGN_per_GBP")),
                to_none_if_nan(row.get("usd_pct_change")),
                to_none_if_nan(row.get("usd_7day_avg")),
                to_none_if_nan(row.get("day_of_week")),
            ))
            inserted += 1
        conn.commit()
        print(f"Inserted {inserted} rows into the database.")
    except Exception as e:
        conn.rollback()  # undo everything if any row failed
        print(f"Insert failed, nothing was saved: {e}")

def run_analysis_queries(conn):
    print("\n=== SQL ANALYSIS ===")

    print("\n-- Latest readings --")
    df = pd.read_sql_query("""
        SELECT date, ngn_per_usd, day_of_week
        FROM exchange_rates
        ORDER BY date DESC
        LIMIT 10
    """, conn)
    print(df.to_string(index=False))

    print("\n-- Monthly averages --")
    df = pd.read_sql_query("""
        SELECT
            to_char(date, 'YYYY-MM')                AS month,
            ROUND(AVG(ngn_per_usd)::numeric, 2)     AS avg_rate,
            ROUND(MIN(ngn_per_usd)::numeric, 2)     AS min_rate,
            ROUND(MAX(ngn_per_usd)::numeric, 2)     AS max_rate,
            COUNT(*)                                AS num_readings
        FROM exchange_rates
        GROUP BY month
        ORDER BY month DESC
    """, conn)
    print(df.to_string(index=False))

    print("\n-- Most volatile days --")
    df = pd.read_sql_query("""
        SELECT date, ngn_per_usd, usd_pct_change
        FROM exchange_rates
        WHERE usd_pct_change IS NOT NULL
        ORDER BY ABS(usd_pct_change) DESC
        LIMIT 5
    """, conn)
    if df.empty:
        print("Not enough data yet.")
    else:
        print(df.to_string(index=False))

if __name__ == "__main__":
    conn = create_connection()
    create_tables(conn)

    df = pd.read_csv("data/processed/exchange_rates_clean.csv")
    insert_from_dataframe(conn, df)
    run_analysis_queries(conn)
    conn.close()
    print("\nDatabase connection closed.")