import pandas as pd
from datetime import datetime
from data import get_candles

def in_trading_session():
    hour = datetime.utcnow().hour
    return 7 <= hour <= 20   # broader active window

def compute_signal(pair):
    candles = get_candles(pair)
    if not candles or len(candles) < 20:
        return None, None

    df = pd.DataFrame(candles)

    try:
        df["open"]  = df["open"].astype(float)
        df["high"]  = df["high"].astype(float)
        df["low"]   = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
    except:
        return None, None

    # EMA
    df["ema9"] = df["close"].ewm(span=9).mean()
    df["ema21"] = df["close"].ewm(span=21).mean()

    # MACD
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    
    # ✅ FIXED: Avoid division by zero
    if loss.iloc[-1] == 0:
        rs = 0
    else:
        rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # Stochastic Oscillator
    low_14 = df['low'].rolling(14).min()
    high_14 = df['high'].rolling(14).max()
    df['%K'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['%D'] = df['%K'].rolling(3).mean()

    last = df.iloc[-1]

    if not in_trading_session():
        return None, None

    # BUY (IMPROVED)
    if (last.ema9 > last.ema21 and 
        last.macd > last.macd_signal and
        last.rsi > 55 and 
        last['%K'] > last['%D'] and 
        last['%K'] < 75):
        return "UP", last.close

    # SELL (IMPROVED)
    if (last.ema9 < last.ema21 and
        last.macd < last.macd_signal and
        last.rsi < 45 and
        last['%K'] < last['%D'] and
        last['%K'] > 25):
        return "DOWN", last.close

    return None, None
