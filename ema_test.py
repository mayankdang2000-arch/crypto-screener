import json, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

ENDPOINTS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
    "https://api.binance.us",
]
SYMBOL = "ETHUSDT"
INTERVAL = "1d"
LIMIT = 500      # days of history used for the calculation
PERIOD = 200     # EMA length

def get_klines():
    for base in ENDPOINTS:
        url = f"{base}/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit={LIMIT}"
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                return base, json.load(r)
        except urllib.error.HTTPError as e:
            print(f"{base} -> HTTP {e.code}")
        except Exception as e:
            print(f"{base} -> error: {e}")
    return None, None

def ema_first_close(closes, n):
    """EMA starting from the very first close."""
    a = 2 / (n + 1)
    out = [closes[0]]
    for c in closes[1:]:
        out.append(a * c + (1 - a) * out[-1])
    return out

def ema_sma_seed(closes, n):
    """EMA whose first value (at candle n) is the SMA of the first n closes."""
    a = 2 / (n + 1)
    out = [None] * (n - 1)
    out.append(sum(closes[:n]) / n)
    for c in closes[n:]:
        out.append(a * c + (1 - a) * out[-1])
    return out

base, candles = get_klines()
if not candles:
    print("FAILED on all endpoints")
    sys.exit(1)

closes = [float(c[4]) for c in candles]
e1 = ema_first_close(closes, PERIOD)
e2 = ema_sma_seed(closes, PERIOD)
now_ms = int(time.time() * 1000)

print(f"{SYMBOL} {INTERVAL} from {base}: {len(candles)} candles, EMA {PERIOD}")
print(f"{'date (UTC)':<12}{'close':>12}{'EMA(first close)':>20}{'EMA(SMA seed)':>16}  status")
for i in range(len(candles) - 6, len(candles)):
    d = datetime.fromtimestamp(candles[i][0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    status = "closed" if candles[i][6] < now_ms else "LIVE (still forming)"
    print(f"{d:<12}{closes[i]:>12.2f}{e1[i]:>20.2f}{e2[i]:>16.2f}  {status}")
