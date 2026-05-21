import requests

GOLD_API_URL = "https://www.goldapi.io/api/XAU/INR"

API_KEY = "goldapi-7020c5e30a9863c09e95c9d971e28bb9-io"


def get_live_gold_price():

    try:

        headers = {
            "x-access-token": API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.get(
            GOLD_API_URL,
            headers=headers
        )

        data = response.json()

        print("LIVE GOLD API RESPONSE:", data)

        # PRICE PER OUNCE
        ounce_price = data["price"]

        # CONVERT OUNCE → GRAM
        price_per_gram = ounce_price / 31.1035

        # SAFETY FALLBACK
        if price_per_gram < 1000:
            return 14000

        return round(price_per_gram, 2)

    except Exception as e:

        print("GOLD PRICE ERROR:", e)

        # FALLBACK PRICE
        return 14000