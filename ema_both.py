import json, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

ENDPOINTS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
    "https://api.binance.us",
]
SYMBOLS = ["ETHUSDT", "SOLUSDT"]        # SOL is newer, so it shows the "short history" case
PERIOD = 200
TIMEFRAMES = [("1d", 500), ("1w", 400)]  # (interval, max candles to fetch)

def get_klines(symbol, interval, limit):
    for base in ENDPOINTS:
        url = f"{base}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                return base, json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  {base} -> HTTP {e.code}")
        except Exception as e:
            print(f"  {base} -> error: {e}")
    return None, None

def ema(closes, n):
    """EMA starting from the first close available."""
    a = 2 / (n + 1)
    out = [closes[0]]
    for c in closes[1:]:
        out.append(a * c + (1 - a) * out[-1])
    return out

now_ms = int(time.time() * 1000)
failed = False

for symbol in SYMBOLS:
    for interval, limit in TIMEFRAMES:
        print(f"\n{symbol} {interval}:")
        base, candles = get_klines(symbol, interval, limit)
        if not candles:
            print("  FAILED on all endpoints")
            failed = True
            continue

        n = len(candles)
        if n < PERIOD:
            quality = "NOT ENOUGH HISTORY (EMA 200 unreliable)"
        elif n < limit:
            quality = "EXACT (full history used)"
        else:
            quality = "APPROX (history was cut at the limit)"

        closes = [float(c[4]) for c in candles]
        e = ema(closes, PERIOD)
        print(f"  {n} candles from {base} -> {quality}")
        print(f"  {'date (UTC)':<12}{'close':>12}{'EMA ' + str(PERIOD):>14}  status")
        for i in range(n - 3, n):
            d = datetime.fromtimestamp(candles[i][0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            status = "closed" if candles[i][6] < now_ms else "LIVE"
            print(f"  {d:<12}{closes[i]:>12.2f}{e[i]:>14.2f}  {status}")

if failed:
    sys.exit(1)
