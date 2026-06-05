import pandas as pd
import json
import glob
import os

def load_all_raw_files():
    files = glob.glob("data/raw/rates_*.json")

    if not files:
        print("No raw files found. Run fetch_data.py first!")
        return None

    all_records = []

    for filepath in files:
        with open(filepath, "r") as f:
            raw = json.load(f)

        rates = raw.get("conversion_rates", {})

        # Parse the full date string the API returns
        raw_date = raw.get("time_last_update_utc", "")
        parsed_date = pd.to_datetime(raw_date, format="%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")

        record = {
            "date": parsed_date,
            "USD": rates.get("USD"),
            "EUR": rates.get("EUR"),
            "GBP": rates.get("GBP"),
            "GHS": rates.get("GHS"),
            "ZAR": rates.get("ZAR"),
            "source_file": os.path.basename(filepath),
        }
        all_records.append(record)

    df = pd.DataFrame(all_records)
    print(f"Loaded {len(df)} records from {len(files)} files")
    return df

def clean_and_transform(df):
    # Convert date column to proper datetime format
    df["date"] = pd.to_datetime(df["date"])

    # Sort by date oldest to newest
    df = df.sort_values("date").reset_index(drop=True)

    # Remove duplicate dates
    df = df.drop_duplicates(subset="date", keep="last")

    # Add NGN per 1 USD/EUR/GBP (easier for Nigerians to read)
    df["NGN_per_USD"] = (1 / df["USD"]).round(2)
    df["NGN_per_EUR"] = (1 / df["EUR"]).round(2)
    df["NGN_per_GBP"] = (1 / df["GBP"]).round(2)

    # Add day of week
    df["day_of_week"] = df["date"].dt.day_name()

    # Daily percentage change
    df["usd_pct_change"] = df["NGN_per_USD"].pct_change().round(4) * 100

    # 7-day rolling average
    df["usd_7day_avg"] = df["NGN_per_USD"].rolling(window=7).mean().round(2)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nYour cleaned data:")
    print(df[["date", "NGN_per_USD", "NGN_per_EUR", "NGN_per_GBP", "day_of_week"]].to_string(index=False))

    return df

def save_processed(df):
    output_path = "data/processed/exchange_rates_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"\nClean data saved to: {output_path}")

def basic_stats(df):
    print("\n=== Summary Statistics: NGN per USD ===")
    print(df["NGN_per_USD"].describe().round(2))
    print(f"\nHighest rate recorded: N{df['NGN_per_USD'].max():,.2f}")
    print(f"Lowest rate recorded:  N{df['NGN_per_USD'].min():,.2f}")
    print(f"Average rate:          N{df['NGN_per_USD'].mean():,.2f}")

if __name__ == "__main__":
    df = load_all_raw_files()
    if df is not None:
        df_clean = clean_and_transform(df)
        save_processed(df_clean)
        basic_stats(df_clean)