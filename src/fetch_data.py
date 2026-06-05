import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EXCHANGE_API_KEY")
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/NGN"

def fetch_exchange_rates():
    print("Fetching rates from API...")
    response = requests.get(BASE_URL)

    if response.status_code != 200:
        print(f"Error: API returned {response.status_code}")
        return None

    data = response.json()

    if data.get("result") != "success":
        print("API error:", data.get("error-type"))
        return None

    print(f"Success! Fetched rates for: {data['base_code']}")
    print(f"Last updated: {data['time_last_update_utc']}")
    return data

def save_raw_data(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/raw/rates_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Raw data saved to: {filename}")
    return filename

def extract_key_rates(data):
    currencies = ["USD", "EUR", "GBP", "GHS", "ZAR", "KES"]
    rates = data["conversion_rates"]

    filtered = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "base": "NGN",
    }

    for currency in currencies:
        if currency in rates:
            filtered[currency] = rates[currency]

    return filtered

if __name__ == "__main__":
    raw_data = fetch_exchange_rates()
    if raw_data:
        save_raw_data(raw_data)
        key_rates = extract_key_rates(raw_data)
        print("\nKey rates extracted:")
        for k, v in key_rates.items():
            print(f"  {k}: {v}")