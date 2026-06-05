import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import sqlite3

DB_PATH = "data/market_intelligence.db"

def load_from_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT * FROM exchange_rates
        ORDER BY date ASC
    """, conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df

def create_dashboard(df):
    sns.set_theme(style="whitegrid", palette="muted")

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        "Nigerian Naira (NGN) Exchange Rate Intelligence Dashboard",
        fontsize=16, fontweight="bold"
    )

    # ---- Chart 1: NGN per USD over time ----
    ax1 = axes[0, 0]
    ax1.plot(df["date"], df["ngn_per_usd"],
             color="#378ADD", linewidth=2, marker="o", markersize=4)
    ax1.set_title("NGN per USD Over Time")
    ax1.set_ylabel("N per $1 USD")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax1.tick_params(axis="x", rotation=30)

    # ---- Chart 2: NGN per EUR and GBP ----
    ax2 = axes[0, 1]
    ax2.plot(df["date"], df["ngn_per_eur"],
             color="#1D9E75", linewidth=2, marker="o", markersize=4, label="EUR")
    ax2.plot(df["date"], df["ngn_per_gbp"],
             color="#D85A30", linewidth=2, marker="o", markersize=4, label="GBP")
    ax2.set_title("NGN per EUR and GBP Over Time")
    ax2.set_ylabel("N per 1 unit")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax2.tick_params(axis="x", rotation=30)
    ax2.legend()

    # ---- Chart 3: Bar chart of NGN/USD per reading ----
    ax3 = axes[1, 0]
    ax3.bar(df["date"].dt.strftime("%d %b"), df["ngn_per_usd"],
            color="#7F77DD", alpha=0.85, edgecolor="white")
    ax3.set_title("NGN/USD Rate per Day")
    ax3.set_ylabel("N per $1 USD")
    ax3.tick_params(axis="x", rotation=45)

    # ---- Chart 4: All three currencies compared ----
    ax4 = axes[1, 1]
    bar_width = 0.25
    x = range(len(df))
    ax4.bar([i - bar_width for i in x], df["ngn_per_usd"],
            width=bar_width, label="USD", color="#378ADD", alpha=0.85)
    ax4.bar(list(x), df["ngn_per_eur"],
            width=bar_width, label="EUR", color="#1D9E75", alpha=0.85)
    ax4.bar([i + bar_width for i in x], df["ngn_per_gbp"],
            width=bar_width, label="GBP", color="#D85A30", alpha=0.85)
    ax4.set_title("USD vs EUR vs GBP Comparison")
    ax4.set_ylabel("NGN per 1 unit")
    ax4.set_xticks(list(x))
    ax4.set_xticklabels(df["date"].dt.strftime("%d %b"), rotation=45)
    ax4.legend()

    plt.tight_layout()

    output_path = "data/processed/dashboard.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Dashboard saved to: {output_path}")
    plt.show()

if __name__ == "__main__":
    df = load_from_db()
    print(f"Loaded {len(df)} rows for visualisation")
    create_dashboard(df)