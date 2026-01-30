import time
import requests
import urllib3
from datetime import datetime, timedelta
from strategy import compute_signal
from data import get_candles  # <-- Import get_candles directly
from config import (
    BOT_TOKEN, CHANNEL_ID,
    ASIA_PAIRS, LONDON_PAIRS, NEWYORK_PAIRS, DEFAULT_PAIRS
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHANNEL_ID, "text": msg})

# ---------- SESSION SELECTION ----------
def current_session_pairs():
    hour = datetime.utcnow().hour

    if hour >= 23 or hour < 7:
        return ASIA_PAIRS
    if 7 <= hour < 13:
        return LONDON_PAIRS
    if 13 <= hour < 20:
        return NEWYORK_PAIRS

    return DEFAULT_PAIRS

# ---------- HOT PAIR MEMORY ----------
HOT_PAIRS = {}
LAST_SIGNAL_TIME = {}    # pair -> timestamp

HOT_DECAY = 0.85
PAIR_COOLDOWN = 10 * 60  # 10 minutes

def decay_hot():
    for p in list(HOT_PAIRS.keys()):
        HOT_PAIRS[p] *= HOT_DECAY
        if HOT_PAIRS[p] < 0.3:
            del HOT_PAIRS[p]

def mark_hot(pair):
    HOT_PAIRS[pair] = HOT_PAIRS.get(pair, 0) + 1
    LAST_SIGNAL_TIME[pair] = time.time()

def can_trade(pair):
    last = LAST_SIGNAL_TIME.get(pair)
    if not last:
        return True
    return (time.time() - last) > PAIR_COOLDOWN

def priority_pairs(session_pairs):
    hot = sorted(
        [p for p in session_pairs if p in HOT_PAIRS],
        key=lambda x: HOT_PAIRS[x],
        reverse=True
    )
    normal = [p for p in session_pairs if p not in hot]
    return hot + normal

# ---------- MAIN LOOP ----------
print("🚀 TOXA SIGNAL BOT STARTED (OPTIMIZED 5/H MODE)")
send("✅ Bot is online and scanning the market for signals...")

while True:
    decay_hot()

    session_pairs = current_session_pairs()
    pairs = priority_pairs(session_pairs)

    for pair in pairs:
        if not can_trade(pair):
            continue

        time.sleep(10)   # 🔥 6 API calls per minute

        signal = compute_signal(pair)
        if not signal or signal[0] is None:
            continue

        direction, entry_price = signal
        mark_hot(pair)

        # Calculate entry time in IST (UTC+5:30)
        entry_time_utc = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(minutes=1)
        entry_time_ist = entry_time_utc + timedelta(hours=5, minutes=30)
        entry_time_str = entry_time_ist.strftime('%H:%M:%S')

        send(f"""
👑 TANIX AI 24/7 👑
━━━━━━━━━━━━━━
🔮 TOXA SIGNAL 🟡
━━━━━━━━━━━━━━

📌 Pair: {pair}
⏱️ Timeframe: 1 Minute
🕒 Entry Time: {entry_time_str} (IST)
📍 Direction: {'🔼 UP' if direction=='UP' else '🔽 DOWN'}

━━━━━━━━━━━━━━
⚠️ In case of LOSS, apply 1-Step Martingale
💲 Follow Proper Money Management
""".strip())

        # Wait for the trade candle to start, then for it to close
        time.sleep(60)  # Wait for the next minute to begin

        # --- RESULT CHECK ---
        # Wait another 60 seconds for the trade candle to complete
        time.sleep(60)

        # Fetch the latest candles to get the result
        exit_candles = get_candles(pair)
        if not exit_candles:
            send(f"⚠️ Could not retrieve result for {pair}. Data API may be down.")
            continue

        # The most recent candle is the one we traded on. We need its open and close.
        trade_candle = exit_candles[0]
        open_price = float(trade_candle['open'])
        exit_price = float(trade_candle['close'])

        # Correct Win/Loss Logic: Compare the trade candle's close to its own open.
        win = (direction == "UP" and exit_price > open_price) or \
              (direction == "DOWN" and exit_price < open_price)

        if win:
            send("✅ RESULT: WIN 🟢🔥")
            mark_hot(pair) # Reinforce good signal
        else:
            
            # --- MARTINGALE LOGIC ---
            # The entry for the Martingale is the closing price of the losing trade
            time.sleep(60) # Wait for the Martingale candle to close

            mtg_candles = get_candles(pair)
            if not mtg_candles:
                send(f"⚠️ Could not retrieve Martingale result for {pair}.")
                continue
            
            # Martingale trade candle
            mtg_candle = mtg_candles[0]
            mtg_open_price = float(mtg_candle['open'])
            mtg_exit_price = float(mtg_candle['close'])
            
            # Martingale wins if it moves in the original direction
            mtg_win = (direction == "UP" and mtg_exit_price > mtg_open_price) or \
                      (direction == "DOWN" and mtg_exit_price < mtg_open_price)

            if mtg_win:
                send("✅ RESULT: WIN (MTG) 🟢🔥")
            else:
                send("❌ LOSS 🔴")

        time.sleep(120)  # cooldown after trade
