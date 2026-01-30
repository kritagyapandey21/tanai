import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

API_KEY = os.getenv("API_KEY")
TIMEFRAME = "1min"

ASIA_PAIRS = [
    "USD/JPY",
    "AUD/USD",
    "NZD/USD",
    "AUD/JPY",
    "NZD/JPY",
    "USD/CHF"
]

LONDON_PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "EUR/GBP",
    "EUR/JPY",
    "GBP/JPY",
    "USD/CHF"
]

NEWYORK_PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/CAD",
    "EUR/JPY",
    "GBP/JPY",
    "AUD/USD"
]

DEFAULT_PAIRS = [
    "EUR/USD",
    "USD/JPY",
    "GBP/USD",
    "AUD/USD",
    "USD/CAD",
    "USD/CHF"
]