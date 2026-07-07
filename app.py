import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

DB_PATH = "data/market_intelligence.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT * FROM exchange_rates
        ORDER BY date ASC
    """, conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

st.title("🇳🇬 Nigerian Naira Exchange Rate Dashboard")
st.write(f"Showing **{len(df)} days** of exchange rate data")
st.dataframe(df)

st.subheader("NGN per USD Over Time")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["date"], df["ngn_per_usd"], color="#378ADD", linewidth=2, marker="o", markersize=4)
ax.set_ylabel("₦ per $1 USD")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.tick_params(axis="x", rotation=30)
plt.tight_layout()

st.pyplot(fig)