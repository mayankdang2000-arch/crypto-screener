import json, sys, urllib.request, urllib.error
from datetime import datetime, timezone

ENDPOINTS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
    "https://api.binance.us",
]
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVAL = "1h"   # 1m, 5m, 15m, 1h, 4h, 1d ...
LIMIT = 200       # number of candles (max 1000)

def ts(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

def get_klines(symbol):
    for base in ENDPOINTS:
        url = f"{base}/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                return base, json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  {base} -> HTTP {e.code}")
        except Exception as e:
            print(f"  {base} -> error: {e}")
    return None, None

failed = False
for sym in SYMBOLS:
    print(f"\n{sym}:")
    base, candles = get_klines(sym)
    if not candles:
        print("  FAILED on all endpoints")
        failed = True
        continue
    first, last = candles[0], candles[-1]
    print(f"  OK from {base}: {len(candles)} candles ({INTERVAL})")
    print(f"  first candle: {ts(first[0])} UTC, close {first[4]}")
    print(f"  last candle:  {ts(last[0])} UTC, close {last[4]}, volume {last[5]}")

if failed:
    sys.exit(1)
