from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logger.error("Telegram BOT_TOKEN not found in environment variables")
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Binance API configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    logger.error("Binance API credentials not found in environment variables")
    raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET environment variables are required")