# 🇳🇬 Nigerian Naira Exchange Rate Intelligence

**Live app:** https://nigeria-market-intelligence.streamlit.app

A business intelligence dashboard helping Nigerian importers decide when 
to buy foreign currency, powered by a fully automated data pipeline.

## The Problem

Nigerian businesses that import goods and pay foreign suppliers in USD, 
EUR, or GBP are exposed to daily currency volatility. A business owner 
paying a $10,000 supplier invoice on the wrong day can lose hundreds of 
thousands of naira compared to paying just a week earlier or later — 
often without realizing it.

Most business owners have no easy way to track these trends or know 
whether today is a good day to convert Naira to foreign currency.

## What It Does

- Tracks live NGN exchange rates against USD, EUR, and GBP
- Automatically collects new data every day with zero manual intervention
- Gives a plain-English recommendation: buy today, or wait?
- Calculates exactly how much a supplier payment will cost in Naira, 
  and compares it to costs from previous days
- Shows historical trends and identifies the cheapest days to convert 
  currency
- Includes a confidence score based on recent rate movement

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python + Pandas | Data cleaning & analysis |
| SQLite (SQL) | Local data storage & querying |
| Streamlit | Live interactive dashboard |
| ExchangeRate-API | Live data source |
| Matplotlib | Visualisation |
| GitHub Actions | Automated daily data collection |

## How It Works

**Data Collection**  
A GitHub Actions workflow runs every day at 7am UTC, calling the 
ExchangeRate-API and saving the raw response as a JSON file. Nothing 
is ever deleted — every day's raw data is kept as a permanent record.

**Processing**  
The raw JSON files are cleaned and transformed with Pandas — calculating 
daily percentage changes, 7-day rolling averages, and converting rates 
into an NGN-per-unit format that's easier for Nigerians to read.

**Analysis & Decision Logic**  
The dashboard compares today's rate against the 30-day average and 
recent trend direction to generate a simple recommendation: is today 
a good day to buy foreign currency, or should you wait?

**Visualization**  
An interactive Streamlit dashboard displays the current rate, historical 
trends, and a supplier payment cost calculator — all built to be 
understood in under 30 seconds by someone with no data background.

## Key Insights

Based on data collected since June 2026:

- The Naira has ranged between ₦1,357 and ₦1,382 per USD
- The most volatile single-day movement recorded was a 0.59% swing
- Monthly averages show a gradual weakening trend from June to July
- A $10,000 supplier payment can vary by over ₦100,000 depending on 
  timing alone

## Run It Yourself

```bash
# Install dependencies
pip install -r requirements.txt

# Add your API key to a .env file
# EXCHANGE_API_KEY=your_key_here

# Run the data pipeline
python src/fetch_data.py
python src/clean_data.py
python src/database.py

# Launch the dashboard
streamlit run app.py
```

## Roadmap

- [x] Automated daily data collection via GitHub Actions
- [x] SQL-based local data storage and analysis
- [x] Live Streamlit dashboard with decision logic
- [x] Deployed to Streamlit Community Cloud
- [ ] Migrate to Supabase/PostgreSQL for faster cloud performance
- [ ] Add currency rate alerts (email/WhatsApp)
- [ ] Add supplier payment planning tool
- [ ] Add GHS and ZAR currency support

## Author

Built by [@Mr-Martynz](https://github.com/Mr-Martynz)