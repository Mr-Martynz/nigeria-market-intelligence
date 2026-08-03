import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob
import json

def load_data():
    files = glob.glob("data/raw/rates_*.json")

    if not files:
        return pd.DataFrame()

    all_records = []
    for filepath in files:
        with open(filepath, "r") as f:
            raw = json.load(f)

        rates = raw.get("conversion_rates", {})
        raw_date = raw.get("time_last_update_utc", "")
        parsed_date = pd.to_datetime(raw_date, format="%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")

        record = {
            "date": parsed_date,
            "USD": rates.get("USD"),
            "EUR": rates.get("EUR"),
            "GBP": rates.get("GBP"),
        }
        all_records.append(record)

    df = pd.DataFrame(all_records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df.drop_duplicates(subset="date", keep="last")

    df["ngn_per_usd"] = (1 / df["USD"]).round(2)
    df["ngn_per_eur"] = (1 / df["EUR"]).round(2)
    df["ngn_per_gbp"] = (1 / df["GBP"]).round(2)
    df["day_of_week"] = df["date"].dt.day_name()
    df["usd_pct_change"] = df["ngn_per_usd"].pct_change().round(4) * 100
    df["usd_7day_avg"] = df["ngn_per_usd"].rolling(window=7).mean().round(2)

    return df

df = load_data()

if df.empty:
    st.error("No exchange rate data available. Please run the data pipeline first.")
    st.stop()

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

last_30 = df.tail(30)
monthly_avg = last_30["ngn_per_usd"].mean()

last_7 = df.tail(7)
rising_days = (last_7["ngn_per_usd"].diff() > 0).sum()
falling_days = (last_7["ngn_per_usd"].diff() < 0).sum()

if rising_days >= 5:
    confidence = "Low confidence"
    confidence_reason = f"USD has risen {rising_days} of the last 7 days — trend is moving against you"
elif falling_days >= 5:
    confidence = "High confidence"
    confidence_reason = f"USD has fallen {falling_days} of the last 7 days — trend is in your favour"
else:
    confidence = "Moderate confidence"
    confidence_reason = f"USD has risen {rising_days} and fallen {falling_days} of the last 7 days — market is mixed"

if today_rate < monthly_avg:
    st.success(f"✅ TODAY IS A GOOD DAY TO BUY. The current rate (₦{today_rate:,.2f}) is below the 30-day average (₦{monthly_avg:,.2f}). You are buying cheaper than usual.")
else:
    st.warning(f"⚠️ CONSIDER WAITING. The current rate (₦{today_rate:,.2f}) is above the 30-day average (₦{monthly_avg:,.2f}). You are buying more expensive than usual.")

st.caption(f"📊 {confidence}: {confidence_reason}.")

# ---- HISTORICAL CHART ----
st.subheader("How the Naira Has Moved Against the Dollar")

range_option = st.selectbox(
    "Time range:",
    ["7 Days", "30 Days", "90 Days", "1 Year"],
    index=1
)

range_days = {"7 Days": 7, "30 Days": 30, "90 Days": 90, "1 Year": 365}[range_option]
cutoff_date = df["date"].max() - pd.Timedelta(days=range_days)
chart_df = df[df["date"] >= cutoff_date]

chart_avg = chart_df["ngn_per_usd"].mean()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(chart_df["date"], chart_df["ngn_per_usd"],
        color="#378ADD", linewidth=2, marker="o", markersize=4)
ax.axhline(y=chart_avg, color="#FF6B6B",
           linewidth=1.5, linestyle="--", label=f"{range_option} avg: ₦{chart_avg:,.2f}")
ax.set_ylabel("₦ per $1 USD")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.tick_params(axis="x", rotation=30)
ax.legend()
plt.tight_layout()

st.pyplot(fig)

st.caption("💡 When the line is below the red dotted average — that's a cheaper day to buy dollars.")

# ---- IMPORT COST CALCULATOR ----
st.subheader("Import Cost Calculator")
st.write("How much will your supplier payment cost in Naira?")

currency = st.selectbox("Select currency:", ["USD", "EUR", "GBP"])

rate_column = f"ngn_per_{currency.lower()}"
today_selected_rate = today[rate_column]
week_ago_selected_rate = week_ago[rate_column]

amount = st.number_input(f"Enter {currency} amount you need to pay:", 
                          min_value=0.0, value=10000.0, step=500.0)

if amount > 0:
    cost_today = amount * today_selected_rate
    cost_week_ago = amount * week_ago_selected_rate
    difference = cost_today - cost_week_ago

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Cost Today", f"₦{cost_today:,.0f}")
    with col2:
        st.metric("Cost 7 Days Ago", f"₦{cost_week_ago:,.0f}")

    pct_diff = (difference / cost_week_ago) * 100

    with col3:
        st.metric("Difference", f"₦{abs(difference):,.0f}",
                delta=f"{pct_diff:+.2f}% vs last week",
                delta_color="inverse")

st.divider()

# ---- BUSINESS INSIGHTS ----
st.subheader("📊 What This Means For Your Business")

if weekly_change < 0:
    st.info(f"📉 **The Naira has strengthened {abs(weekly_change):.2f}% this week.** "
            f"Importing goods is cheaper than it was 7 days ago.")
else:
    st.info(f"📈 **The Naira has weakened {weekly_change:.2f}% this week.** "
            f"Importing goods is more expensive than it was 7 days ago.")

diff_from_avg = ((today_rate - monthly_avg) / monthly_avg) * 100
if diff_from_avg < 0:
    st.success(f"✅ **Today's rate is {abs(diff_from_avg):.2f}% below the 30-day average.** "
               f"This is a relatively good time to convert Naira to dollars.")
else:
    st.warning(f"⚠️ **Today's rate is {diff_from_avg:.2f}% above the 30-day average.** "
               f"You are paying more than usual to buy dollars right now.")

best_day = df.loc[df["ngn_per_usd"].idxmin()]
st.info(f"📅 **The cheapest day to buy dollars this month was "
        f"{best_day['date'].strftime('%d %B %Y')} at ₦{best_day['ngn_per_usd']:,.2f}.** "
        f"Compared to today, that's ₦{today_rate - best_day['ngn_per_usd']:,.2f} cheaper per dollar.")