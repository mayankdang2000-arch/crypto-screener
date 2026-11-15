import json, sys, urllib.request, urllib.error

ENDPOINTS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",  # public market data only, usually not blocked
    "https://api.binance.us",
]
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

for base in ENDPOINTS:
    url = f"{base}/api/v3/ticker/price"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.load(r)
        prices = {d["symbol"]: d["price"] for d in data}
        print(f"OK from {base} - {len(prices)} symbols fetched")
        for s in SYMBOLS:
            print(s, prices.get(s))
        break
    except urllib.error.HTTPError as e:
        print(f"{base} -> HTTP {e.code}")
    except Exception as e:
        print(f"{base} -> error: {e}")
else:
    print("All endpoints failed")
    sys.exit(1)
