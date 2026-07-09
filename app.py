import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DB_PATH = "data/market_intelligence.db"

def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("""
            SELECT * FROM exchange_rates
            ORDER BY date ASC
        """, conn)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="NGN Exchange Rate Intelligence",
    page_icon="🇳🇬",
    layout="wide"
)

# ---- HEADER ----
st.title("Nigerian Naira Exchange Rate Intelligence")
st.caption("Helping Nigerian importers decide when to buy foreign currency")
last_updated = df["date"].max().strftime("%d %B %Y")
st.caption(f"Last updated: {last_updated}")

st.divider()

# ---- KEY METRICS ----
today = df.iloc[-1]
week_ago = df.iloc[-7] if len(df) >= 7 else df.iloc[0]

today_rate = today["ngn_per_usd"]
week_ago_rate = week_ago["ngn_per_usd"]
weekly_change = ((today_rate - week_ago_rate) / week_ago_rate) * 100

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Today's USD Rate", f"₦{today_rate:,.2f}")

with col2:
    st.metric("7-Day Change", f"{weekly_change:+.2f}%",
              delta=f"{weekly_change:+.2f}%",
              delta_color="inverse")

with col3:
    st.metric("Highest This Month", f"₦{df['ngn_per_usd'].max():,.2f}")

with col4:
    st.metric("Lowest This Month", f"₦{df['ngn_per_usd'].min():,.2f}")

st.divider()

# ---- DECISION CARD ----
st.subheader("Should You Buy Dollars Today?")

monthly_avg = df["ngn_per_usd"].mean()

if today_rate < monthly_avg:
    st.success(f"✅ TODAY IS A GOOD DAY TO BUY. The current rate (₦{today_rate:,.2f}) is below the 30-day average (₦{monthly_avg:,.2f}). You are buying cheaper than usual.")
else:
    st.warning(f"⚠️ CONSIDER WAITING. The current rate (₦{today_rate:,.2f}) is above the 30-day average (₦{monthly_avg:,.2f}). You are buying more expensive than usual.")

st.divider()

# ---- HISTORICAL CHART ----
st.subheader("How the Naira Has Moved Against the Dollar")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["date"], df["ngn_per_usd"], 
        color="#378ADD", linewidth=2, marker="o", markersize=4)
ax.axhline(y=monthly_avg, color="#FF6B6B", 
           linewidth=1.5, linestyle="--", label=f"30-day avg: ₦{monthly_avg:,.2f}")
ax.set_ylabel("₦ per $1 USD")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.tick_params(axis="x", rotation=30)
ax.legend()
plt.tight_layout()

st.pyplot(fig)

st.caption("💡 When the line is below the red dotted average — that's a cheaper day to buy dollars.")

st.divider()

# ---- IMPORT COST CALCULATOR ----
st.subheader("Import Cost Calculator")
st.write("How much will your supplier payment cost in Naira?")

usd_amount = st.number_input("Enter USD amount you need to pay:", 
                              min_value=0.0, value=10000.0, step=500.0)

if usd_amount > 0:
    cost_today = usd_amount * today_rate
    cost_week_ago = usd_amount * week_ago_rate
    difference = cost_today - cost_week_ago

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Cost Today", f"₦{cost_today:,.0f}")
    with col2:
        st.metric("Cost 7 Days Ago", f"₦{cost_week_ago:,.0f}")
    with col3:
        st.metric("Difference", f"₦{abs(difference):,.0f}",
                  delta=f"{'cheaper' if difference < 0 else 'more expensive'} than last week")

st.divider()

# ---- BUSINESS INSIGHTS ----
st.subheader("📊 What This Means For Your Business")

# Insight 1 - Weekly trend
if weekly_change < 0:
    st.info(f"📉 **The Naira has strengthened {abs(weekly_change):.2f}% this week.** "
            f"Importing goods is cheaper than it was 7 days ago.")
else:
    st.info(f"📈 **The Naira has weakened {weekly_change:.2f}% this week.** "
            f"Importing goods is more expensive than it was 7 days ago.")

# Insight 2 - Compare today vs monthly average
diff_from_avg = ((today_rate - monthly_avg) / monthly_avg) * 100
if diff_from_avg < 0:
    st.success(f"✅ **Today's rate is {abs(diff_from_avg):.2f}% below the 30-day average.** "
               f"This is a relatively good time to convert Naira to dollars.")
else:
    st.warning(f"⚠️ **Today's rate is {diff_from_avg:.2f}% above the 30-day average.** "
               f"You are paying more than usual to buy dollars right now.")

# Insight 3 - Best day this month
best_day = df.loc[df["ngn_per_usd"].idxmin()]
st.info(f"📅 **The cheapest day to buy dollars this month was "
        f"{best_day['date'].strftime('%d %B %Y')} at ₦{best_day['ngn_per_usd']:,.2f}.** "
        f"Compared to today, that's ₦{today_rate - best_day['ngn_per_usd']:,.2f} cheaper per dollar.")