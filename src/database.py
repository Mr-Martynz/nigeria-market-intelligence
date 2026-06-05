import sqlite3
import pandas as pd

DB_PATH = "data/market_intelligence.db"

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to database: {DB_PATH}")
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            date           TEXT NOT NULL,
            ngn_per_usd    REAL,
            ngn_per_eur    REAL,
            ngn_per_gbp    REAL,
            usd_pct_change REAL,
            usd_7day_avg   REAL,
            day_of_week    TEXT,
            created_at     TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date)
        )
    """)
    conn.commit()
    print("Table 'exchange_rates' is ready.")

def insert_from_dataframe(conn, df):
    cursor = conn.cursor()
    inserted = 0

    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO exchange_rates
                    (date, ngn_per_usd, ngn_per_eur, ngn_per_gbp,
                     usd_pct_change, usd_7day_avg, day_of_week)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row["date"])[:10],
                row.get("NGN_per_USD"),
                row.get("NGN_per_EUR"),
                row.get("NGN_per_GBP"),
                row.get("usd_pct_change"),
                row.get("usd_7day_avg"),
                row.get("day_of_week"),
            ))
            inserted += 1
        except Exception as e:
            print(f"Skipped row {row['date']}: {e}")

    conn.commit()
    print(f"Inserted {inserted} rows into the database.")

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
            substr(date, 1, 7)         AS month,
            ROUND(AVG(ngn_per_usd), 2) AS avg_rate,
            ROUND(MIN(ngn_per_usd), 2) AS min_rate,
            ROUND(MAX(ngn_per_usd), 2) AS max_rate,
            COUNT(*)                   AS num_readings
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
        print("Not enough data yet — run fetch_data.py a few more days to see this!")
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