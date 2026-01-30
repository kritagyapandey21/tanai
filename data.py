import requests
import time
from config import API_KEY, TIMEFRAME

def get_candles(pair, retries=3):
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={pair}&interval={TIMEFRAME}"
        f"&apikey={API_KEY}&outputsize=30"   # ✅ FIXED: Increased to 30
    )

    headers = {
        "Accept-Encoding": "gzip, deflate"
    }

    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                verify=False
            )

            if response.status_code != 200:
                time.sleep(2)
                continue

            data = response.json()
            return data.get("values", [])

        except Exception as e:
            if attempt == retries - 1:
                print(f"⚠️ Data fetch failed for {pair}: {e}")
                return []
            time.sleep(2)
