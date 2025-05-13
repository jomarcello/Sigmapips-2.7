# Import necessary modules for improved logging
import os
import sys
import json
import logging
import logging.config
from datetime import datetime

# Setup detailed logging configuration
def setup_logging(log_level=None):
    """Configure structured logging for the application"""
    log_level = log_level or os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate a log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/trading_bot_{timestamp}.log"
    
    # Define logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": log_file,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": True
            },
            "trading_bot": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False
            },
            "trading_bot.services": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False
            }
        }
    }
    
    # Apply the configuration
    logging.config.dictConfig(logging_config)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level {log_level}, writing to {log_file}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running on platform: {sys.platform}")
    
    # Log environment variables (excluding sensitive information)
    safe_env = {}
    for key, value in os.environ.items():
        if any(sensitive in key.lower() for sensitive in ['key', 'token', 'secret', 'password', 'pwd']):
            safe_env[key] = f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "[REDACTED]"
        else:
            safe_env[key] = value
    
    logger.debug(f"Environment variables: {json.dumps(safe_env, indent=2)}")
    
    return logger

# Initialize logging early in the application startup
logger = setup_logging()

import os
import json
import asyncio
import traceback
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime, timedelta
import logging
import copy
import re
import time
import random

from fastapi import FastAPI, Request, HTTPException, status
from telegram import Bot, Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto, InputMediaAnimation, InputMediaDocument, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    CallbackContext,
    MessageHandler,
    filters,
    PicklePersistence
)
from telegram.error import TelegramError, BadRequest
import httpx
import telegram.error  # Add this import for BadRequest error handling

from trading_bot.services.database.db import Database
from trading_bot.services.chart_service.chart import ChartService
from trading_bot.services.sentiment_service.sentiment import MarketSentimentService
from trading_bot.services.calendar_service import EconomicCalendarService
from trading_bot.services.payment_service.stripe_service import StripeService
from trading_bot.services.payment_service.stripe_config import get_subscription_features
from trading_bot.services.telegram_service.states import (
    MENU, ANALYSIS, SIGNALS, CHOOSE_MARKET, CHOOSE_INSTRUMENT, CHOOSE_STYLE,
    CHOOSE_ANALYSIS, SIGNAL_DETAILS,
    CALLBACK_MENU_ANALYSE, CALLBACK_MENU_SIGNALS, CALLBACK_ANALYSIS_TECHNICAL,
    CALLBACK_ANALYSIS_SENTIMENT, CALLBACK_ANALYSIS_CALENDAR, CALLBACK_SIGNALS_ADD,
    CALLBACK_SIGNALS_MANAGE, CALLBACK_BACK_MENU
)
import trading_bot.services.telegram_service.gif_utils as gif_utils

# Initialize logger
logger = logging.getLogger(__name__)

# Major currencies to focus on
MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "NZD", "CAD"]

# Currency to flag emoji mapping
CURRENCY_FLAG = {
    "USD": "🇺🇸",
    "EUR": "🇪🇺",
    "GBP": "🇬🇧",
    "JPY": "🇯🇵",
    "CHF": "🇨🇭",
    "AUD": "🇦🇺",
    "NZD": "🇳🇿",
    "CAD": "🇨🇦"
}

# Map of instruments to their corresponding currencies
INSTRUMENT_CURRENCY_MAP = {
    # Special case for global view
    "GLOBAL": MAJOR_CURRENCIES,
    
    # Forex
    "EURUSD": ["EUR", "USD"],
    "GBPUSD": ["GBP", "USD"],
    "USDJPY": ["USD", "JPY"],
    "USDCHF": ["USD", "CHF"],
    "AUDUSD": ["AUD", "USD"],
    "NZDUSD": ["NZD", "USD"],
    "USDCAD": ["USD", "CAD"],
    "EURGBP": ["EUR", "GBP"],
    "EURJPY": ["EUR", "JPY"],
    "GBPJPY": ["GBP", "JPY"],
    
    # Indices (mapped to their related currencies)
    "US30": ["USD"],
    "US100": ["USD"],
    "US500": ["USD"],
    "UK100": ["GBP"],
    "GER40": ["EUR"],
    "FRA40": ["EUR"],
    "ESP35": ["EUR"],
    "JP225": ["JPY"],
    "AUS200": ["AUD"],
    
    # Commodities (mapped to USD primarily)
    "XAUUSD": ["USD", "XAU"],  # Gold
    "XAGUSD": ["USD", "XAG"],  # Silver
    "USOIL": ["USD"],          # Oil (WTI)
    "UKOIL": ["USD", "GBP"],   # Oil (Brent)
    
    # Crypto
    "BTCUSD": ["USD", "BTC"],
    "ETHUSD": ["USD", "ETH"],
    "LTCUSD": ["USD", "LTC"],
    "XRPUSD": ["USD", "XRP"]
}

# Callback data constants
CALLBACK_ANALYSIS_TECHNICAL = "analysis_technical"
CALLBACK_ANALYSIS_SENTIMENT = "analysis_sentiment"
CALLBACK_ANALYSIS_CALENDAR = "analysis_calendar"
CALLBACK_BACK_MENU = "back_menu"
CALLBACK_BACK_ANALYSIS = "back_to_analysis"
CALLBACK_BACK_MARKET = "back_market"
CALLBACK_BACK_INSTRUMENT = "back_instrument"
CALLBACK_BACK_SIGNALS = "back_signals"
CALLBACK_SIGNALS_ADD = "signals_add"
CALLBACK_SIGNALS_MANAGE = "signals_manage"
CALLBACK_MENU_ANALYSE = "menu_analyse"
CALLBACK_MENU_SIGNALS = "menu_signals"

# States
MENU = 0
CHOOSE_ANALYSIS = 1
CHOOSE_SIGNALS = 2
CHOOSE_MARKET = 3
CHOOSE_INSTRUMENT = 4
CHOOSE_STYLE = 5
SHOW_RESULT = 6
CHOOSE_TIMEFRAME = 7
SIGNAL_DETAILS = 8
SIGNAL = 9
SUBSCRIBE = 10
BACK_TO_MENU = 11  # Add this line

# Messages
WELCOME_MESSAGE = """
🚀 <b>Sigmapips AI - Main Menu</b> 🚀

Choose an option to access advanced trading support:

📊 Services:
• <b>Technical Analysis</b> – Real-time chart analysis and key levels

• <b>Market Sentiment</b> – Understand market trends and sentiment

• <b>Economic Calendar</b> – Stay updated on market-moving events

• <b>Trading Signals</b> – Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = """
🚀 <b>Welcome to Sigmapips AI!</b> 🚀

To access all features, you need a subscription:

📊 <b>Trading Signals Subscription - $29.99/month</b>
• Access to all trading signals (Forex, Crypto, Commodities, Indices)
• Advanced timeframe analysis (1m, 15m, 1h, 4h)
• Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = """
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = """
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("🔍 Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("📊 Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("📈 Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("🧠 Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("📅 Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("⬅️ Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("➕ Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("⚙️ Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("⬅️ Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_analysis")]
]

# Forex keyboard voor technical analyse
FOREX_KEYBOARD = [
    [
        InlineKeyboardButton("EURUSD", callback_data="instrument_EURUSD_chart"),
        InlineKeyboardButton("GBPUSD", callback_data="instrument_GBPUSD_chart"),
        InlineKeyboardButton("USDJPY", callback_data="instrument_USDJPY_chart")
    ],
    [
        InlineKeyboardButton("AUDUSD", callback_data="instrument_AUDUSD_chart"),
        InlineKeyboardButton("USDCAD", callback_data="instrument_USDCAD_chart"),
        InlineKeyboardButton("EURGBP", callback_data="instrument_EURGBP_chart")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Forex keyboard voor sentiment analyse
FOREX_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("EURUSD", callback_data="instrument_EURUSD_sentiment"),
        InlineKeyboardButton("GBPUSD", callback_data="instrument_GBPUSD_sentiment"),
        InlineKeyboardButton("USDJPY", callback_data="instrument_USDJPY_sentiment")
    ],
    [
        InlineKeyboardButton("AUDUSD", callback_data="instrument_AUDUSD_sentiment"),
        InlineKeyboardButton("USDCAD", callback_data="instrument_USDCAD_sentiment"),
        InlineKeyboardButton("EURGBP", callback_data="instrument_EURGBP_sentiment")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Forex keyboard voor kalender analyse
FOREX_CALENDAR_KEYBOARD = [
    [
        InlineKeyboardButton("EURUSD", callback_data="instrument_EURUSD_calendar"),
        InlineKeyboardButton("GBPUSD", callback_data="instrument_GBPUSD_calendar"),
        InlineKeyboardButton("USDJPY", callback_data="instrument_USDJPY_calendar")
    ],
    [
        InlineKeyboardButton("AUDUSD", callback_data="instrument_AUDUSD_calendar"),
        InlineKeyboardButton("USDCAD", callback_data="instrument_USDCAD_calendar"),
        InlineKeyboardButton("EURGBP", callback_data="instrument_EURGBP_calendar")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("📈 Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("🧠 Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("📅 Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Forex keyboard for signals
FOREX_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("EURUSD", callback_data="instrument_EURUSD_signals"),
        InlineKeyboardButton("GBPUSD", callback_data="instrument_GBPUSD_signals"),
        InlineKeyboardButton("USDJPY", callback_data="instrument_USDJPY_signals")
    ],
    [
        InlineKeyboardButton("USDCAD", callback_data="instrument_USDCAD_signals"),
        InlineKeyboardButton("EURGBP", callback_data="instrument_EURGBP_signals")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (1m)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (15m)", callback_data="style_scalp")],
    [InlineKeyboardButton("📊 Intraday (1h)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (4h)", callback_data="style_swing")],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "1m",
    "scalp": "15m",
    "intraday": "1h",
    "swing": "4h"
}

# Mapping of instruments to their allowed timeframes - updated 2023-03-23
INSTRUMENT_TIMEFRAME_MAP = {
    # H1 timeframe only
    "AUDJPY": "H1", 
    "AUDCHF": "H1",
    "EURCAD": "H1",
    "EURGBP": "H1",
    "GBPCHF": "H1",
    "HK50": "H1",
    "NZDJPY": "H1",
    "USDCHF": "H1",
    "USDJPY": "H1",  # USDJPY toegevoegd voor signaalabonnementen
    "XRPUSD": "H1",
    
    # H4 timeframe only
    "AUDCAD": "H4",
    "AU200": "H4", 
    "CADCHF": "H4",
    "EURCHF": "H4",
    "EURUSD": "H4",
    "GBPCAD": "H4",
    "LINKUSD": "H4",
    "NZDCHF": "H4",
    
    # M15 timeframe only
    "DOGEUSD": "M15",
    "GBPNZD": "M15",
    "NZDUSD": "M15",
    "SOLUSD": "M15",
    "UK100": "M15",
    "XAUUSD": "M15",
    
    # M30 timeframe only
    "BNBUSD": "M30",
    "DOTUSD": "M30",
    "ETHUSD": "M30",
    "EURAUD": "M30",
    "EURJPY": "M30",
    "GBPAUD": "M30",
    "GBPUSD": "M30",
    "NZDCAD": "M30",
    "US30": "M30",
    "US500": "M30",
    "USDCAD": "M30",
    "XLMUSD": "M30",
    "XTIUSD": "M30",
    "DE40": "M30",
    "BTCUSD": "M30",  # Added for consistency with CRYPTO_KEYBOARD_SIGNALS
    "US100": "M30",   # Added for consistency with INDICES_KEYBOARD_SIGNALS
    "XAGUSD": "M15",  # Added for consistency with COMMODITIES_KEYBOARD_SIGNALS
    "USOIL": "M30"    # Added for consistency with COMMODITIES_KEYBOARD_SIGNALS
    
    # Removed as requested: EU50, FR40, LTCUSD
}

# Map common timeframe notations
TIMEFRAME_DISPLAY_MAP = {
    "M15": "15 Minutes",
    "M30": "30 Minutes", 
    "H1": "1 Hour",
    "H4": "4 Hours"
}

# Voeg deze functie toe aan het begin van bot.py, na de imports
def _detect_market(instrument: str) -> str:
    """Detecteer market type gebaseerd op instrument"""
    instrument = instrument.upper()
    
    # Commodities eerst checken
    commodities = [
        "XAUUSD",  # Gold
        "XAGUSD",  # Silver
        "WTIUSD",  # Oil WTI
        "BCOUSD",  # Oil Brent
        "USOIL",   # Oil WTI (alternative symbol)
    ]
    if instrument in commodities:
        logger.info(f"Detected {instrument} as commodity")
        return "commodities"
    
    # Crypto pairs
    crypto_base = ["BTC", "ETH", "XRP", "SOL", "BNB", "ADA", "DOT", "LINK"]
    if any(c in instrument for c in crypto_base):
        logger.info(f"Detected {instrument} as crypto")
        return "crypto"
    
    # Major indices
    indices = [
        "US30", "US500", "US100",  # US indices
        "UK100", "DE40", "FR40",   # European indices
        "JP225", "AU200", "HK50"   # Asian indices
    ]
    if instrument in indices:
        logger.info(f"Detected {instrument} as index")
        return "indices"
    
    # Forex pairs als default
    logger.info(f"Detected {instrument} as forex")
    return "forex"

# Voeg dit toe als decorator functie bovenaan het bestand na de imports
def require_subscription(func):
    """Check if user has an active subscription"""
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Check subscription status
        is_subscribed = await self.db.is_user_subscribed(user_id)
        
        # Check if payment has failed
        payment_failed = await self.db.has_payment_failed(user_id)
        
        if is_subscribed and not payment_failed:
            # User has subscription, proceed with function
            return await func(self, update, context, *args, **kwargs)
        else:
            if payment_failed:
                # Show payment failure message
                failed_payment_text = f"""
❗ <b>Subscription Payment Failed</b> ❗

Your subscription payment could not be processed and your service has been deactivated.

To continue using Sigmapips AI and receive trading signals, please reactivate your subscription by clicking the button below.
                """
                
                # Use direct URL link for reactivation
                reactivation_url = "https://buy.stripe.com/9AQcPf3j63HL5JS145"
                
                # Create button for reactivation
                keyboard = [
                    [InlineKeyboardButton("🔄 Reactivate Subscription", url=reactivation_url)]
                ]
            else:
                # Show subscription screen with the welcome message from the screenshot
                failed_payment_text = f"""
🚀 <b>Welcome to Sigmapips AI!</b> 🚀

<b>Discover powerful trading signals for various markets:</b>
• <b>Forex</b> - Major and minor currency pairs
• <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
• <b>Indices</b> - Global market indices
• <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
✅ Real-time trading signals

✅ Multi-timeframe analysis (1m, 15m, 1h, 4h)

✅ Advanced chart analysis

✅ Sentiment indicators

✅ Economic calendar integration

<b>Start today with a FREE 14-day trial!</b>
                """
                
                # Use direct URL link instead of callback for the trial button
                reactivation_url = "https://buy.stripe.com/3cs3eF9Hu9256NW9AA"
                
                # Create button for trial
                keyboard = [
                    [InlineKeyboardButton("🔥 Start 14-day FREE Trial", url=reactivation_url)]
                ]
            
            # Handle both message and callback query updates
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text=failed_payment_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    text=failed_payment_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            return MENU
    
    return wrapper

# API keys with robust sanitization
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()  # Changed from DeepSeek to OpenAI

# Only using OpenAI's o4-mini now
# No Tavily API key needed anymore
logger.info("Using only OpenAI o4-mini for Market Sentiment service")

# Log OpenAI API key (partially masked)
if OPENAI_API_KEY:
    # Better masking for privacy and security
    masked_key = f"sk-p...{OPENAI_API_KEY[-4:]}" if len(OPENAI_API_KEY) > 8 else "sk-p..."
    logger.info(f"Using OpenAI API key: {masked_key}")
    
    # Validate the key format
    from trading_bot.config import validate_openai_key
    if not validate_openai_key(OPENAI_API_KEY):
        logger.warning("OpenAI API key format is invalid. AI services may not work correctly.")
else:
    logger.warning("No OpenAI API key configured. AI services will be disabled.")
    
# Set environment variables for the API keys with sanitization
os.environ["PERPLEXITY_API_KEY"] = PERPLEXITY_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  # Changed from DeepSeek to OpenAI
# No Tavily environment needed

class TelegramService:
    def __init__(self, db: Database, stripe_service=None, bot_token: Optional[str] = None, proxy_url: Optional[str] = None, lazy_init: bool = False):
        """Initialize the bot with given database and config."""
        # Database connection
        self.db = db
        
        # Setup configuration 
        self.stripe_service = stripe_service
        self.user_signals = {}
        self.signals_dir = "data/signals"
        self.signals_enabled_val = True
        self.polling_started = False
        self.admin_users = [1093307376]  # Add your Telegram ID here for testing
        self._signals_enabled = True  # Enable signals by default
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
        # GIF utilities for UI
        self.gif_utils = gif_utils  # Initialize gif_utils as an attribute
        
        # Setup the bot and application
        self.bot = None
        self.application = None
        
        # Telegram Bot configuratie
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.token = self.bot_token  # Aliased for backward compatibility
        self.proxy_url = proxy_url or os.getenv("TELEGRAM_PROXY_URL", "")
        
        # Configure custom request handler with improved connection settings
        request = HTTPXRequest(
            connection_pool_size=50,  # Increase from 20 to 50
            connect_timeout=15.0,     # Increase from 10.0 to 15.0
            read_timeout=45.0,        # Increase from 30.0 to 45.0
            write_timeout=30.0,       # Increase from 20.0 to 30.0
            pool_timeout=60.0,        # Increase from 30.0 to 60.0
        )
        
        # Initialize the bot directly with connection pool settings
        self.bot = Bot(token=self.bot_token, request=request)
        self.application = None  # Will be initialized in setup()
        
        # Webhook configuration
        self.webhook_url = os.getenv("WEBHOOK_URL", "")
        self.webhook_path = "/webhook"  # Always use this path
        if self.webhook_url.endswith("/"):
            self.webhook_url = self.webhook_url[:-1]  # Remove trailing slash
            
        logger.info(f"Bot initialized with webhook URL: {self.webhook_url} and path: {self.webhook_path}")
        
        # Initialize API services
        self.chart_service = ChartService()  # Initialize chart service
        # Lazy load services only when needed
        self._calendar_service = None
        self._sentiment_service = None
        
        # Don't use asyncio.create_task here - it requires a running event loop
        # We'll initialize chart service later when the event loop is running
        
        # Bot application initialization
        self.persistence = None
        self.bot_started = False
        
        # Cache for sentiment analysis
        self.sentiment_cache = {}
        self.sentiment_cache_ttl = 60 * 60  # 1 hour in seconds
        
        # Start the bot
        try:
            # Check for bot token
            if not self.bot_token:
                raise ValueError("Missing Telegram bot token")
            
            # Initialize the bot
            self.bot = Bot(token=self.bot_token)
        
            # Initialize the application
            self.application = Application.builder().bot(self.bot).build()
        
            # Register the handlers
            self._register_handlers(self.application)
            
            # Initialize signals dictionary but don't load them yet (will be done in initialize_services)
            self.user_signals = {}
        
            logger.info("Telegram service initialized")
            
            # Keep track of processed updates
            self.processed_updates = set()
            
        except Exception as e:
            logger.error(f"Error initializing Telegram service: {str(e)}")
            raise

    async def initialize_services(self):
        """Initialize services that require an asyncio event loop"""
        try:
            # Initialize chart service
            await self.chart_service.initialize()
            logger.info("Chart service initialized")
            
            # Load stored signals
            await self._load_signals()
            logger.info("Signals loaded")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise
            
    # Calendar service helpers
    @property
    def calendar_service(self):
        """Lazy loaded calendar service"""
        if self._calendar_service is None:
            # Only initialize the calendar service when it's first accessed
            self.logger.info("Lazy loading calendar service")
            self._calendar_service = EconomicCalendarService()
        return self._calendar_service
        
    def _get_calendar_service(self):
        """Get the calendar service instance"""
        self.logger.info("Getting calendar service")
        return self.calendar_service

    async def _format_calendar_events(self, calendar_data):
        """Format the calendar data into a readable HTML message"""
        self.logger.info(f"Formatting calendar data with {len(calendar_data)} events")
        if not calendar_data:
            return "<b>📅 Economic Calendar</b>\n\nNo economic events found for today."
        
        # Sort events by time
        try:
            # Try to parse time for sorting
            def parse_time_for_sorting(event):
                time_str = event.get('time', '')
                try:
                    # Extract hour and minute if in format like "08:30 EST"
                    if ':' in time_str:
                        parts = time_str.split(' ')[0].split(':')
                        hour = int(parts[0])
                        minute = int(parts[1])
                        return hour * 60 + minute
                    return 0
                except:
                    return 0
            
            # Sort the events by time
            sorted_events = sorted(calendar_data, key=parse_time_for_sorting)
        except Exception as e:
            self.logger.error(f"Error sorting calendar events: {str(e)}")
            sorted_events = calendar_data
        
        # Format the message
        message = "<b>📅 Economic Calendar</b>\n\n"
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        message += f"<b>Date:</b> {current_date}\n\n"
        
        # Add impact legend
        message += "<b>Impact:</b> 🔴 High   🟠 Medium   🟢 Low\n\n"
        
        # Group events by country
        events_by_country = {}
        for event in sorted_events:
            country = event.get('country', 'Unknown')
            if country not in events_by_country:
                events_by_country[country] = []
            events_by_country[country].append(event)
        
        # Format events by country
        for country, events in events_by_country.items():
            country_flag = CURRENCY_FLAG.get(country, '')
            message += f"<b>{country_flag} {country}</b>\n"
            
            for event in events:
                time = event.get('time', 'TBA')
                title = event.get('title', 'Unknown Event')
                impact = event.get('impact', 'Low')
                impact_emoji = {'High': '🔴', 'Medium': '🟠', 'Low': '🟢'}.get(impact, '🟢')
                
                message += f"{time} - {impact_emoji} {title}\n"
            
            message += "\n"  # Add extra newline between countries
        
        return message
        
    # Utility functions that might be missing
    async def update_message(self, query, text, keyboard=None, parse_mode=ParseMode.HTML):
        """Utility to update a message with error handling"""
        try:
            # Check if the message is too long for Telegram caption limits (1024 chars)
            MAX_CAPTION_LENGTH = 1000  # Slightly under the 1024 limit for safety
            MAX_MESSAGE_LENGTH = 4000  # Telegram message limit
            
            # Log message length for debugging
            logger.info(f"Updating message (length: {len(text)} chars)")
            
            # If message is too long for a caption but ok for a text message
            if len(text) > MAX_CAPTION_LENGTH and len(text) <= MAX_MESSAGE_LENGTH:
                logger.info("Message too long for caption but ok for text message")
                # Try to edit message text first
                await query.edit_message_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode=parse_mode
                )
                return True
            # If message is too long even for a text message
            elif len(text) > MAX_MESSAGE_LENGTH:
                logger.warning(f"Message too long ({len(text)} chars), truncating")
                # Find a good breaking point
                truncated = text[:MAX_MESSAGE_LENGTH-100]
                
                # Try to break at a paragraph
                last_newline = truncated.rfind('\n\n')
                if last_newline > MAX_MESSAGE_LENGTH * 0.8:  # If we can keep at least 80% of the text
                    truncated = truncated[:last_newline]
                    
                # Add indicator that text was truncated
                truncated += "\n\n<i>... (message truncated)</i>"
                
                # Try to edit message text with truncated content
                await query.edit_message_text(
                    text=truncated,
                    reply_markup=keyboard,
                    parse_mode=parse_mode
                )
                return True
            else:
                # Normal case - message is within limits
                # Try to edit message text first
                await query.edit_message_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode=parse_mode
                )
                return True
        except Exception as e:
            logger.warning(f"Could not update message text: {str(e)}")
            
            # If text update fails, try to edit caption
            try:
                # Check if caption is too long
                MAX_CAPTION_LENGTH = 1000  # Slightly under the 1024 limit for safety
                
                if len(text) > MAX_CAPTION_LENGTH:
                    logger.warning(f"Caption too long ({len(text)} chars), truncating")
                    # Find a good breaking point
                    truncated = text[:MAX_CAPTION_LENGTH-100]
                    
                    # Try to break at a paragraph
                    last_newline = truncated.rfind('\n\n')
                    if last_newline > MAX_CAPTION_LENGTH * 0.8:  # If we can keep at least 80% of the text
                        truncated = truncated[:last_newline]
                        
                    # Add indicator that text was truncated
                    truncated += "\n\n<i>... (message truncated)</i>"
                    
                    # Use truncated text for caption
                    await query.edit_message_caption(
                        caption=truncated,
                        reply_markup=keyboard,
                        parse_mode=parse_mode
                    )
                else:
                    # Caption is within limits
                    await query.edit_message_caption(
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode=parse_mode
                    )
                return True
            except Exception as e2:
                logger.error(f"Could not update caption either: {str(e2)}")
                
                # As a last resort, send a new message
                try:
                    chat_id = query.message.chat_id
                    
                    # Check if message is too long
                    MAX_MESSAGE_LENGTH = 4000  # Telegram message limit
                    
                    if len(text) > MAX_MESSAGE_LENGTH:
                        logger.warning(f"New message too long ({len(text)} chars), truncating")
                        # Find a good breaking point
                        truncated = text[:MAX_MESSAGE_LENGTH-100]
                        
                        # Try to break at a paragraph
                        last_newline = truncated.rfind('\n\n')
                        if last_newline > MAX_MESSAGE_LENGTH * 0.8:  # If we can keep at least 80% of the text
                            truncated = truncated[:last_newline]
                            
                        # Add indicator that text was truncated
                        truncated += "\n\n<i>... (message truncated)</i>"
                        
                        # Use truncated text for new message
                        await query.bot.send_message(
                            chat_id=chat_id,
                            text=truncated,
                            reply_markup=keyboard,
                            parse_mode=parse_mode
                        )
                    else:
                        # Message is within limits
                        await query.bot.send_message(
                            chat_id=chat_id,
                            text=text,
                            reply_markup=keyboard,
                            parse_mode=parse_mode
                        )
                    return True
                except Exception as e3:
                    logger.error(f"Failed to send new message: {str(e3)}")
                    return False
    
    # Missing handler implementations
    async def back_signals_callback(self, update: Update, context=None) -> int:
        """Handle back_signals button press"""
        query = update.callback_query
        await query.answer()
        
        logger.info("back_signals_callback called")
        
        # Make sure we're in the signals flow context
        if context and hasattr(context, 'user_data'):
            # Keep is_signals_context flag but reset from_signal flag
            context.user_data['is_signals_context'] = True
            context.user_data['from_signal'] = False
            
            # Clear other specific analysis keys but maintain signals context
            keys_to_remove = [
                'instrument', 'market', 'analysis_type', 'timeframe', 
                'signal_id', 'signal_instrument', 'signal_direction', 'signal_timeframe',
                'loading_message'
            ]
            
            for key in keys_to_remove:
                if key in context.user_data:
                    del context.user_data[key]
            
            logger.info(f"Updated context in back_signals_callback: {context.user_data}")
        
        # Create keyboard for signal menu
        keyboard = [
            [InlineKeyboardButton("📊 Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("⚙️ Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,
            text="<b>📈 Signal Management</b>\n\nManage your trading signals",
            keyboard=reply_markup
        )
        
        return SIGNALS
        
    async def get_subscribers_for_instrument(self, instrument: str, timeframe: str = None) -> List[int]:
        """
        Get a list of subscribed user IDs for a specific instrument and timeframe
        
        Args:
            instrument: The trading instrument (e.g., EURUSD)
            timeframe: Optional timeframe filter
            
        Returns:
            List of subscribed user IDs
        """
        try:
            logger.info(f"Getting subscribers for {instrument} timeframe: {timeframe}")
            
            # Get all subscribers from the database
            # Note: Using get_signal_subscriptions instead of find_all
            subscribers = await self.db.get_signal_subscriptions(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return []
                
            # Filter out subscribers that don't have an active subscription
            active_subscribers = []
            for subscriber in subscribers:
                user_id = subscriber['user_id']
                
                # Check if user is subscribed
                is_subscribed = await self.db.is_user_subscribed(user_id)
                
                # Check if payment has failed
                payment_failed = await self.db.has_payment_failed(user_id)
                
                if is_subscribed and not payment_failed:
                    active_subscribers.append(user_id)
                else:
                    logger.info(f"User {user_id} doesn't have an active subscription, skipping signal")
            
            return active_subscribers
            
        except Exception as e:
            logger.error(f"Error getting subscribers: {str(e)}")
            # FOR TESTING: Add admin users if available
            if hasattr(self, 'admin_users') and self.admin_users:
                logger.info(f"Returning admin users for testing: {self.admin_users}")
                return self.admin_users
            return []

    async def process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """
        Process a trading signal from TradingView webhook or API
        
        Supports two formats:
        1. TradingView format: instrument, signal, price, sl, tp1, tp2, tp3, interval
        2. Custom format: instrument, direction, entry, stop_loss, take_profit, timeframe
        
        Returns:
            bool: True if signal was processed successfully, False otherwise
        """
        try:
            # Log the incoming signal data
            logger.info(f"Processing signal: {signal_data}")
            
            # Check which format we're dealing with and normalize it
            instrument = signal_data.get('instrument')
            
            # Handle TradingView format (price, sl, interval)
            if 'price' in signal_data and 'sl' in signal_data:
                price = signal_data.get('price')
                sl = signal_data.get('sl')
                tp1 = signal_data.get('tp1')
                tp2 = signal_data.get('tp2')
                tp3 = signal_data.get('tp3')
                interval = signal_data.get('interval', '1h')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval,
                    'interval': interval  # Add interval for consistency
                }
                
                # Add optional fields if present
                normalized_data['tp1'] = tp1
                normalized_data['tp2'] = tp2
                normalized_data['tp3'] = tp3
            
            # Handle custom format (direction, entry, stop_loss, timeframe)
            elif 'direction' in signal_data and 'entry' in signal_data:
                direction = signal_data.get('direction')
                entry = signal_data.get('entry')
                stop_loss = signal_data.get('stop_loss')
                take_profit = signal_data.get('take_profit')
                timeframe = signal_data.get('timeframe', '1h')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe,
                    'interval': timeframe  # Add interval for consistency
                }
                
                # Add optional fields if present
                tp1 = signal_data.get('tp1', take_profit)
                tp2 = signal_data.get('tp2')
                tp3 = signal_data.get('tp3')
                if tp1:
                    normalized_data['tp1'] = tp1
                if tp2:
                    normalized_data['tp2'] = tp2
                if tp3:
                    normalized_data['tp3'] = tp3
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            timestamp = int(time.time())
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{timestamp}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            normalized_data['original_data'] = copy.deepcopy(signal_data)  # Store original data for reference
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Save signal for this admin
                        await self._ensure_signal_saved(admin_id, signal_id, normalized_data)
                        
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                except Exception as e:
                    logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', '1h')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Save signal for this user
                    await self._ensure_signal_saved(user_id, signal_id, normalized_data)
                    
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending signal to user {user_id}: {str(e)}")
            
            logger.info(f"Successfully sent signal {signal_id} to {sent_count}/{len(subscribers)} subscribers")
            return True
            
        except Exception as e:
            logger.error(f"Error processing signal: {str(e)}")
            logger.exception(e)
            return False

    def _format_signal_message(self, signal_data: Dict[str, Any]) -> str:
        """Format signal data into a nice message for Telegram"""
        try:
            # Extract fields from signal data
            instrument = signal_data.get('instrument', 'Unknown')
            direction = signal_data.get('direction', 'Unknown')
            entry = signal_data.get('entry', 'Unknown')
            stop_loss = signal_data.get('stop_loss')
            take_profit = signal_data.get('take_profit')
            timeframe = signal_data.get('timeframe', '1h')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b>🎯 New Trading Signal 🎯</b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} 🎯\n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} 🎯\n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} 🎯\n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "• Position size: 1-2% max\n"
            message += "• Use proper stop loss\n"
            message += "• Follow your trading plan\n\n"
            
            message += "————————————————————\n\n"
            
            # Generate AI verdict
            ai_verdict = f"The {instrument} {direction.lower()} signal shows a promising setup with defined entry at {entry} and stop loss at {stop_loss}. Multiple take profit levels provide opportunities for partial profit taking."
            message += f"<b>🤖 SigmaPips AI Verdict:</b>\n{ai_verdict}"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting signal message: {str(e)}")
            # Return simple message on error
            return f"New {signal_data.get('instrument', 'Unknown')} {signal_data.get('direction', 'Unknown')} Signal"

    def _register_handlers(self, application):
        """Register event handlers for bot commands and callback queries"""
        try:
            logger.info("Registering command handlers")
            
            # Initialize the application without using run_until_complete
            try:
                # Instead of using loop.run_until_complete, directly call initialize 
                # which will be properly awaited by the caller
                self.init_task = application.initialize()
                logger.info("Telegram application initialization ready to be awaited")
            except Exception as init_e:
                logger.error(f"Error during application initialization: {str(init_e)}")
                logger.exception(init_e)
                
            # Set bot commands for menu
            commands = [
                BotCommand("start", "Start the bot and get the welcome message"),
                BotCommand("menu", "Show the main menu"),
                BotCommand("help", "Show available commands and how to use the bot")
            ]
            
            # Store the set_commands_task to be awaited later
            try:
                # Instead of asyncio.create_task, we will await this in the startup event
                self.set_commands_task = self.bot.set_my_commands(commands)
                logger.info("Bot commands ready to be set")
            except Exception as cmd_e:
                logger.error(f"Error preparing bot commands: {str(cmd_e)}")
            
            # Register command handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("menu", self.menu_command))
            application.add_handler(CommandHandler("help", self.help_command))
            
            # Register secret admin commands
            application.add_handler(CommandHandler("set_subscription", self.set_subscription_command))
            application.add_handler(CommandHandler("set_payment_failed", self.set_payment_failed_command))
            logger.info("Registered secret admin commands")
            
            # Register callback handlers
            application.add_handler(CallbackQueryHandler(self.menu_analyse_callback, pattern="^menu_analyse$"))
            application.add_handler(CallbackQueryHandler(self.menu_signals_callback, pattern="^menu_signals$"))
            application.add_handler(CallbackQueryHandler(self.signals_add_callback, pattern="^signals_add$"))
            application.add_handler(CallbackQueryHandler(self.signals_manage_callback, pattern="^signals_manage$"))
            application.add_handler(CallbackQueryHandler(self.market_callback, pattern="^market_"))
            application.add_handler(CallbackQueryHandler(self.instrument_callback, pattern="^instrument_(?!.*_signals)"))
            application.add_handler(CallbackQueryHandler(self.instrument_signals_callback, pattern="^instrument_.*_signals$"))
            
            # Add handler for back buttons
            application.add_handler(CallbackQueryHandler(self.back_market_callback, pattern="^back_market$"))
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            application.add_handler(CallbackQueryHandler(self.back_signals_callback, pattern="^back_signals$"))
            application.add_handler(CallbackQueryHandler(self.back_menu_callback, pattern="^back_menu$"))
            
            # Analysis handlers for regular flow
            application.add_handler(CallbackQueryHandler(self.analysis_technical_callback, pattern="^analysis_technical$"))
            application.add_handler(CallbackQueryHandler(self.analysis_sentiment_callback, pattern="^analysis_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^analysis_calendar$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.analysis_technical_callback, pattern="^analysis_technical_signal_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_sentiment_callback, pattern="^analysis_sentiment_signal_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^analysis_calendar_signal_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
        except Exception as e:
            logger.error(f"Error registering handlers: {str(e)}")
            logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled

    async def back_to_signal_callback(self, update: Update, context=None) -> int:
        """Handle back_to_signal button press"""
        query = update.callback_query
        await query.answer()
        logger.info(f"back_to_signal_callback called with data: {query.data}")
        
        try:
            # Get the current signal being viewed
            user_id = update.effective_user.id
            user_str_id = str(user_id)
            logger.info(f"Processing back_to_signal for user: {user_id}")
            
            # Check if we have original signal information stored in context
            original_signal = None
            if context and hasattr(context, 'user_data'):
                original_signal = context.user_data.get('original_signal')
                logger.info(f"Retrieved original signal from context: {original_signal}")
            
            # If we have original signal info, use it directly
            if original_signal and isinstance(original_signal, dict):
                signal_instrument = original_signal.get('instrument')
                signal_id = original_signal.get('signal_id')
                signal_message = original_signal.get('message')
                
                # Set signal flow flags to ensure proper context is maintained
                if context and hasattr(context, 'user_data'):
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                
                # If we have a stored message, use it directly
                if signal_message and signal_instrument and signal_id:
                    # Prepare analyze button with signal info embedded
                    keyboard = [
                        [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{signal_instrument}_{signal_id}")]
                    ]
                    
                    # Edit current message to show signal
                    await query.edit_message_text(
                        text=signal_message,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode=ParseMode.HTML
                    )
                    
                    logger.info(f"Returned to original signal using stored message")
                    return SIGNAL_DETAILS
            
            # First try to get signal data from backup in context
            signal_instrument = None
            signal_direction = None
            signal_timeframe = None
            signal_id = None
            
            if context and hasattr(context, 'user_data'):
                # Try to get from backup fields first (these are more reliable after navigation)
                signal_instrument = context.user_data.get('signal_instrument_backup') or context.user_data.get('signal_instrument')
                signal_direction = context.user_data.get('signal_direction_backup') or context.user_data.get('signal_direction')
                signal_timeframe = context.user_data.get('signal_timeframe_backup') or context.user_data.get('signal_timeframe')
                signal_id = context.user_data.get('signal_id_backup') or context.user_data.get('signal_id')
                
                # Set signal flow flags to ensure proper context is maintained
                context.user_data['from_signal'] = True
                context.user_data['in_signal_flow'] = True
                
                # Log retrieved values for debugging
                logger.info(f"Retrieved signal data from context: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}, signal_id={signal_id}")
                logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
            
            # Find the signal data using the most reliable method available
            signal_data = None
            
            # Method 1: Try to get the signal directly by ID if we have it
            if signal_id and hasattr(self, 'user_signals') and user_str_id in self.user_signals:
                if signal_id in self.user_signals[user_str_id]:
                    signal_data = self.user_signals[user_str_id][signal_id]
                    logger.info(f"Found signal with ID {signal_id} in memory cache")
            
            # Method 2: If no signal_id or not found, try to find by matching instrument, direction, timeframe
            if not signal_data and signal_instrument and hasattr(self, 'user_signals') and user_str_id in self.user_signals:
                user_signal_dict = self.user_signals[user_str_id]
                # Find signals matching instrument, direction and timeframe
                matching_signals = []
                
                for sig_id, sig in user_signal_dict.items():
                    instrument_match = sig.get('instrument') == signal_instrument
                    direction_match = True  # Default to true if we don't have direction data
                    timeframe_match = True  # Default to true if we don't have timeframe data
                    
                    if signal_direction:
                        direction_match = sig.get('direction') == signal_direction
                    if signal_timeframe:
                        # Check both interval and timeframe fields
                        timeframe_match = (sig.get('interval') == signal_timeframe or 
                                          sig.get('timeframe') == signal_timeframe)
                    
                    if instrument_match and direction_match and timeframe_match:
                        matching_signals.append((sig_id, sig))
                
                # Sort by timestamp, newest first
                if matching_signals:
                    matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                    signal_id, signal_data = matching_signals[0]
                    logger.info(f"Found matching signal with ID: {signal_id}")
                else:
                    logger.warning(f"No exact matching signals found for instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
                    # If no exact match, try with just the instrument
                    matching_signals = []
                    for sig_id, sig in user_signal_dict.items():
                        if sig.get('instrument') == signal_instrument:
                            matching_signals.append((sig_id, sig))
                    
                    if matching_signals:
                        matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                        signal_id, signal_data = matching_signals[0]
                        logger.info(f"Found signal with just instrument match, ID: {signal_id}")
            
            # Method 3: Try to get signal from database by ID
            if not signal_data and signal_id and hasattr(self, 'db') and self.db:
                logger.info(f"Trying to retrieve signal {signal_id} from database")
                try:
                    signal_data = await self.db.get_signal(user_id, signal_id)
                    if signal_data:
                        logger.info(f"Retrieved signal {signal_id} from database")
                        
                        # Store in memory for future use
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                        
                        if user_str_id not in self.user_signals:
                            self.user_signals[user_str_id] = {}
                            
                        self.user_signals[user_str_id][signal_id] = signal_data
                except Exception as db_error:
                    logger.error(f"Error retrieving signal from database: {str(db_error)}")
            
            # Method 4: Try to get signals for this instrument from database
            if not signal_data and signal_instrument and hasattr(self, 'db') and self.db:
                logger.info(f"Trying to retrieve signals for instrument {signal_instrument} from database")
                try:
                    signals = await self.db.get_user_signals(user_id, signal_instrument)
                    if signals and len(signals) > 0:
                        # Use the most recent signal
                        signal_data = signals[0]  # Already sorted by timestamp, newest first
                        signal_id = signal_data.get('id')
                        logger.info(f"Retrieved signal {signal_id} for instrument {signal_instrument} from database")
                        
                        # Store in memory for future use
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                        
                        if user_str_id not in self.user_signals:
                            self.user_signals[user_str_id] = {}
                            
                        self.user_signals[user_str_id][signal_id] = signal_data
                except Exception as db_error:
                    logger.error(f"Error retrieving signals from database: {str(db_error)}")
            
            # Method 5: Try to find signal file on disk
            if not signal_data and signal_id:
                signals_dir = os.path.join(os.getcwd(), 'signals')
                signal_file = os.path.join(signals_dir, f"{signal_id}.json")
                if os.path.exists(signal_file):
                    try:
                        with open(signal_file, 'r') as f:
                            signal_data = json.load(f)
                            logger.info(f"Loaded signal {signal_id} from file")
                            
                            # Store in memory for future use
                            if not hasattr(self, 'user_signals'):
                                self.user_signals = {}
                            
                            if user_str_id not in self.user_signals:
                                self.user_signals[user_str_id] = {}
                                
                            self.user_signals[user_str_id][signal_id] = signal_data
                    except Exception as file_error:
                        logger.error(f"Error loading signal from file: {str(file_error)}")
            
            if not signal_data:
                # Fallback message if signal not found
                logger.warning("Signal data not found, returning to main menu")
                await query.edit_message_text(
                    text="Signal not found. Please use the main menu to continue.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
                return MENU
            
            # Update context with signal details if available
            if context and hasattr(context, 'user_data') and signal_data:
                context.user_data['signal_instrument'] = signal_data.get('instrument')
                context.user_data['signal_direction'] = signal_data.get('direction')
                context.user_data['signal_timeframe'] = signal_data.get('interval') or signal_data.get('timeframe')
                context.user_data['signal_id'] = signal_id
                
                # Also update backup copies
                context.user_data['signal_instrument_backup'] = signal_data.get('instrument')
                context.user_data['signal_direction_backup'] = signal_data.get('direction')
                context.user_data['signal_timeframe_backup'] = signal_data.get('interval') or signal_data.get('timeframe')
                context.user_data['signal_id_backup'] = signal_id
                
                logger.info(f"Updated context with signal details: instrument={signal_data.get('instrument')}, direction={signal_data.get('direction')}, timeframe={signal_data.get('interval') or signal_data.get('timeframe')}, id={signal_id}")
            
            # Show the signal details with analyze button
            # Prepare analyze button with signal info embedded
            keyboard = [
                [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{signal_data.get('instrument')}_{signal_id}")]
            ]
            
            # Get the formatted message from the signal
            signal_message = signal_data.get('message', "Signal details not available.")
            
            # Edit current message to show signal
            logger.info(f"Displaying signal with analyze button. Message length: {len(signal_message)}")
            await query.edit_message_text(
                text=signal_message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
            return SIGNAL_DETAILS
            
        except Exception as e:
            logger.error(f"Error in back_to_signal_callback: {str(e)}")
            logger.exception(e)
            
            # Error recovery
            try:
                await query.edit_message_text(
                    text="An error occurred. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
            except Exception:
                pass
            
            return MENU
            
    async def analyze_from_signal_callback(self, update: Update, context=None) -> int:
        """Handle Analyze Market button from signal notifications"""
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        logger.info(f"analyze_from_signal_callback called with data: {query.data}")
        
        try:
            # Extract signal information from callback data
            parts = query.data.split('_')
            logger.info(f"Callback data parts: {parts}")
            
            # Format: analyze_from_signal_INSTRUMENT_SIGNALID
            instrument = None
            signal_id = None
            
            if len(parts) >= 4:
                instrument = parts[3]
                signal_id = parts[4] if len(parts) >= 5 else None
                logger.info(f"Extracted instrument: {instrument}, signal_id: {signal_id}")
                
                # Store in context for other handlers
                if context and hasattr(context, 'user_data'):
                    context.user_data['instrument'] = instrument
                    if signal_id:
                        context.user_data['signal_id'] = signal_id
                    
                    # Set signal flow flags
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                    
                    # Store the original signal page information
                    # This will be used to return to the signal page later
                    await self._store_original_signal_page(update, context, instrument, signal_id)
                    
                    # Make a backup copy to ensure we can return to signal later
                    context.user_data['signal_instrument_backup'] = instrument
                    if signal_id:
                        context.user_data['signal_id_backup'] = signal_id
                    
                    # Also store info from the actual signal if available
                    user_id = update.effective_user.id
                    user_str_id = str(user_id)
                    
                    # Try to get signal data from memory first
                    if hasattr(self, 'user_signals') and user_str_id in self.user_signals and signal_id in self.user_signals[user_str_id]:
                        signal = self.user_signals[user_str_id][signal_id]
                        if signal:
                            # Store signal details in context
                            context.user_data['signal_direction'] = signal.get('direction')
                            context.user_data['signal_timeframe'] = signal.get('interval') or signal.get('timeframe')
                            # Backup copies
                            context.user_data['signal_direction_backup'] = signal.get('direction')
                            context.user_data['signal_timeframe_backup'] = signal.get('interval') or signal.get('timeframe')
                            logger.info(f"Stored signal details: direction={signal.get('direction')}, timeframe={signal.get('interval') or signal.get('timeframe')}")
                            
                            # Make sure signal is stored in database with correct ID
                            if hasattr(self, 'db') and self.db:
                                # Ensure the signal has the correct ID
                                if signal.get('id') != signal_id:
                                    signal['id'] = signal_id
                                await self.db.store_signal(user_id, signal)
                                logger.info(f"Stored signal {signal_id} in database for user {user_id}")
                    
                    # Try to retrieve signal from database if not found in memory
                    elif signal_id and hasattr(self, 'db') and self.db:
                        try:
                            signal = await self.db.get_signal(user_id, signal_id)
                            if signal:
                                # Store in memory for future use
                                if not hasattr(self, 'user_signals'):
                                    self.user_signals = {}
                                
                                if user_str_id not in self.user_signals:
                                    self.user_signals[user_str_id] = {}
                                self.user_signals[user_str_id][signal_id] = signal
                                
                                # Store in context
                                context.user_data['signal_direction'] = signal.get('direction')
                                context.user_data['signal_timeframe'] = signal.get('interval') or signal.get('timeframe')
                                # Backup copies
                                context.user_data['signal_direction_backup'] = signal.get('direction')
                                context.user_data['signal_timeframe_backup'] = signal.get('interval') or signal.get('timeframe')
                                logger.info(f"Retrieved and stored signal details from database: direction={signal.get('direction')}, timeframe={signal.get('interval') or signal.get('timeframe')}")
                            else:
                                # If signal not found by ID, try to find by instrument and create a new entry
                                logger.info(f"Signal {signal_id} not found in database, checking memory for signal data")
                                if hasattr(self, 'user_signals') and user_str_id in self.user_signals:
                                    # Look for any signals with this instrument
                                    for sig_id, sig_data in self.user_signals[user_str_id].items():
                                        if sig_data.get('instrument') == instrument:
                                            # Create a copy with the correct ID
                                            signal_copy = sig_data.copy()
                                            signal_copy['id'] = signal_id
                                            await self.db.store_signal(user_id, signal_copy)
                                            logger.info(f"Created and stored signal {signal_id} in database for user {user_id}")
                                            break
                        except Exception as db_error:
                            logger.error(f"Error retrieving signal from database: {str(db_error)}")
            else:
                # Legacy support - just extract the instrument
                instrument = parts[3] if len(parts) >= 4 else None
                logger.warning(f"Using legacy format, extracted instrument: {instrument}")
                
                if instrument and context and hasattr(context, 'user_data'):
                    context.user_data['instrument'] = instrument
                    context.user_data['signal_instrument_backup'] = instrument
                    # Set signal flow flags even in legacy mode
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info(f"Set signal flow flags (legacy mode): from_signal=True, in_signal_flow=True")
            
            # Fallback if we couldn't extract an instrument
            if not instrument:
                logger.error("Could not extract instrument from callback data")
                await query.edit_message_text(
                    text="Error: Could not identify the instrument. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
                return MENU
            
            # Show analysis options for this instrument
            # Format message
            # Use the SIGNAL_ANALYSIS_KEYBOARD for consistency
            keyboard = [
                [InlineKeyboardButton("📈 Technical Analysis", callback_data="signal_technical")],
                [InlineKeyboardButton("🧠 Market Sentiment", callback_data="signal_sentiment")],
                [InlineKeyboardButton("📅 Economic Calendar", callback_data="signal_calendar")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_signal")]
            ]
            
            # Try to edit the message text
            try:
                await query.edit_message_text(
                    text=f"Select your analysis type for {instrument}:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
                logger.info(f"Successfully displayed analysis options for {instrument}")
            except Exception as e:
                logger.error(f"Error in analyze_from_signal_callback when updating message: {str(e)}")
                # Fall back to sending a new message
                try:
                    await query.message.reply_text(
                        text=f"Select your analysis type for {instrument}:",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode=ParseMode.HTML
                    )
                    logger.info(f"Sent new message with analysis options for {instrument}")
                except Exception as reply_error:
                    logger.error(f"Failed to send reply message: {str(reply_error)}")
                    # Last resort - try to send a completely new message
                    try:
                        await self.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"Select your analysis type for {instrument}:",
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode=ParseMode.HTML
                        )
                        logger.info(f"Sent completely new message with analysis options for {instrument}")
                    except Exception as send_error:
                        logger.error(f"Failed to send new message: {str(send_error)}")
            
            return CHOOSE_ANALYSIS
        
        except Exception as e:
            logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
            logger.exception(e)
            
            try:
                await query.edit_message_text(
                    text="An error occurred. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
            except Exception as edit_error:
                logger.error(f"Failed to edit message after error: {str(edit_error)}")
                try:
                    await self.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="An error occurred. Please try again from the main menu.",
                        reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                    )
                except Exception:
                    pass
            
            return MENU

    async def _store_original_signal_page(self, update: Update, context=None, instrument=None, signal_id=None):
        """Store the original signal page information in context"""
        try:
            # Get the current signal being viewed
            user_id = update.effective_user.id
            user_str_id = str(user_id)
            logger.info(f"Storing original signal for user: {user_id}")
            
            # Check if we have original signal information stored in context
            original_signal = None
            if context and hasattr(context, 'user_data'):
                original_signal = context.user_data.get('original_signal')
                logger.info(f"Retrieved original signal from context: {original_signal}")
            
            # If we have original signal info, use it directly
            if original_signal and isinstance(original_signal, dict):
                signal_instrument = original_signal.get('instrument')
                signal_id = original_signal.get('signal_id')
                signal_message = original_signal.get('message')
                
                # Set signal flow flags to ensure proper context is maintained
                if context and hasattr(context, 'user_data'):
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                
                # If we have a stored message, use it directly
                if signal_message and signal_instrument and signal_id:
                    # Prepare analyze button with signal info embedded
                    keyboard = [
                        [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{signal_instrument}_{signal_id}")]
                    ]
                    
                    # Edit current message to show signal
                    await update.message.edit_text(
                        text=signal_message,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode=ParseMode.HTML
                    )
                    
                    logger.info(f"Returned to original signal using stored message")
                    return SIGNAL_DETAILS
            
            # First try to get signal data from backup in context
            signal_instrument = None
            signal_direction = None
            signal_timeframe = None
            signal_id = None
            
            if context and hasattr(context, 'user_data'):
                # Try to get from backup fields first (these are more reliable after navigation)
                signal_instrument = context.user_data.get('signal_instrument_backup') or context.user_data.get('signal_instrument')
                signal_direction = context.user_data.get('signal_direction_backup') or context.user_data.get('signal_direction')
                signal_timeframe = context.user_data.get('signal_timeframe_backup') or context.user_data.get('signal_timeframe')
                signal_id = context.user_data.get('signal_id_backup') or context.user_data.get('signal_id')
                
                # Set signal flow flags to ensure proper context is maintained
                context.user_data['from_signal'] = True
                context.user_data['in_signal_flow'] = True
                
                # Log retrieved values for debugging
                logger.info(f"Retrieved signal data from context: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}, signal_id={signal_id}")
                logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
            
            # Find the signal data using the most reliable method available
            signal_data = None
            
            # Method 1: Try to get the signal directly by ID if we have it
            if signal_id and hasattr(self, 'user_signals') and user_str_id in self.user_signals:
                if signal_id in self.user_signals[user_str_id]:
                    signal_data = self.user_signals[user_str_id][signal_id]
                    logger.info(f"Found signal with ID {signal_id} in memory cache")
            
            # Method 2: If no signal_id or not found, try to find by matching instrument, direction, timeframe
            if not signal_data and signal_instrument and hasattr(self, 'user_signals') and user_str_id in self.user_signals:
                user_signal_dict = self.user_signals[user_str_id]
                # Find signals matching instrument, direction and timeframe
                matching_signals = []
                
                for sig_id, sig in user_signal_dict.items():
                    instrument_match = sig.get('instrument') == signal_instrument
                    direction_match = True  # Default to true if we don't have direction data
                    timeframe_match = True  # Default to true if we don't have timeframe data
                    
                    if signal_direction:
                        direction_match = sig.get('direction') == signal_direction
                    if signal_timeframe:
                        # Check both interval and timeframe fields
                        timeframe_match = (sig.get('interval') == signal_timeframe or 
                                          sig.get('timeframe') == signal_timeframe)
                    
                    if instrument_match and direction_match and timeframe_match:
                        matching_signals.append((sig_id, sig))
                
                # Sort by timestamp, newest first
                if matching_signals:
                    matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                    signal_id, signal_data = matching_signals[0]
                    logger.info(f"Found matching signal with ID: {signal_id}")
                else:
                    logger.warning(f"No exact matching signals found for instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
                    # If no exact match, try with just the instrument
                    matching_signals = []
                    for sig_id, sig in user_signal_dict.items():
                        if sig.get('instrument') == signal_instrument:
                            matching_signals.append((sig_id, sig))
                    
                    if matching_signals:
                        matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                        signal_id, signal_data = matching_signals[0]
                        logger.info(f"Found signal with just instrument match, ID: {signal_id}")
            
            # Method 3: Try to get signal from database by ID
            if not signal_data and signal_id and hasattr(self, 'db') and self.db:
                logger.info(f"Trying to retrieve signal {signal_id} from database")
                try:
                    signal_data = await self.db.get_signal(user_id, signal_id)
                    if signal_data:
                        logger.info(f"Retrieved signal {signal_id} from database")
                        
                        # Store in memory for future use
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                        
                        if user_str_id not in self.user_signals:
                            self.user_signals[user_str_id] = {}
                            
                        self.user_signals[user_str_id][signal_id] = signal_data
                except Exception as db_error:
                    logger.error(f"Error retrieving signal from database: {str(db_error)}")
            
            # Method 4: Try to get signals for this instrument from database
            if not signal_data and signal_instrument and hasattr(self, 'db') and self.db:
                logger.info(f"Trying to retrieve signals for instrument {signal_instrument} from database")
                try:
                    signals = await self.db.get_user_signals(user_id, signal_instrument)
                    if signals and len(signals) > 0:
                        # Use the most recent signal
                        signal_data = signals[0]  # Already sorted by timestamp, newest first
                        signal_id = signal_data.get('id')
                        logger.info(f"Retrieved signal {signal_id} for instrument {signal_instrument} from database")
                        
                        # Store in memory for future use
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                        
                        if user_str_id not in self.user_signals:
                            self.user_signals[user_str_id] = {}
                            
                        self.user_signals[user_str_id][signal_id] = signal_data
                except Exception as db_error:
                    logger.error(f"Error retrieving signals from database: {str(db_error)}")
            
            # Method 5: Try to find signal file on disk
            if not signal_data and signal_id:
                signals_dir = os.path.join(os.getcwd(), 'signals')
                signal_file = os.path.join(signals_dir, f"{signal_id}.json")
                if os.path.exists(signal_file):
                    try:
                        with open(signal_file, 'r') as f:
                            signal_data = json.load(f)
                            logger.info(f"Loaded signal {signal_id} from file")
                            
                            # Store in memory for future use
                            if not hasattr(self, 'user_signals'):
                                self.user_signals = {}
                            
                            if user_str_id not in self.user_signals:
                                self.user_signals[user_str_id] = {}
                                
                            self.user_signals[user_str_id][signal_id] = signal_data
                    except Exception as file_error:
                        logger.error(f"Error loading signal from file: {str(file_error)}")
            
            if not signal_data:
                # Fallback message if signal not found
                logger.warning("Signal data not found, returning to main menu")
                await query.edit_message_text(
                    text="Signal not found. Please use the main menu to continue.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
                return MENU
            
            # Update context with signal details if available
            if context and hasattr(context, 'user_data') and signal_data:
                context.user_data['signal_instrument'] = signal_data.get('instrument')
                context.user_data['signal_direction'] = signal_data.get('direction')
                context.user_data['signal_timeframe'] = signal_data.get('interval') or signal_data.get('timeframe')
                context.user_data['signal_id'] = signal_id
                
                # Also update backup copies
                context.user_data['signal_instrument_backup'] = signal_data.get('instrument')
                context.user_data['signal_direction_backup'] = signal_data.get('direction')
                context.user_data['signal_timeframe_backup'] = signal_data.get('interval') or signal_data.get('timeframe')
                context.user_data['signal_id_backup'] = signal_id
                
                logger.info(f"Updated context with signal details: instrument={signal_data.get('instrument')}, direction={signal_data.get('direction')}, timeframe={signal_data.get('interval') or signal_data.get('timeframe')}, id={signal_id}")
            
            # Show the signal details with analyze button
            # Prepare analyze button with signal info embedded
            keyboard = [
                [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{signal_data.get('instrument')}_{signal_id}")]
            ]
            
            # Get the formatted message from the signal
            signal_message = signal_data.get('message', "Signal details not available.")
            
            # Edit current message to show signal
            logger.info(f"Displaying signal with analyze button. Message length: {len(signal_message)}")
            await query.edit_message_text(
                text=signal_message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            
            return SIGNAL_DETAILS
            
        except Exception as e:
            logger.error(f"Error in _store_original_signal_page: {str(e)}")
            logger.exception(e)
            
            # Error recovery
            try:
                await query.edit_message_text(
                    text="An error occurred. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
            except Exception:
                pass
            
            return MENU

    async def signal_technical_callback(self, update: Update, context=None) -> int:
        """Handle signal_technical button press"""
        query = update.callback_query
        await query.answer()
        
        # Add detailed debug logging
        logger.info(f"signal_technical_callback called with query data: {query.data}")
        
        # Save analysis type in context
        if context and hasattr(context, 'user_data'):
            context.user_data['analysis_type'] = 'technical'
        
        # Get the instrument from context
        instrument = None
        if context and hasattr(context, 'user_data'):
            instrument = context.user_data.get('instrument')
            # Debug log for instrument
            logger.info(f"Instrument from context: {instrument}")
            
            # If no instrument found in primary key, try backup
            if not instrument:
                instrument = context.user_data.get('signal_instrument_backup')
                if instrument:
                    logger.info(f"Retrieved instrument from backup: {instrument}")
                    context.user_data['instrument'] = instrument
        
        if not instrument:
            logger.error("No instrument found in context for technical analysis")
            # Show error message and return to analysis selection
            try:
                await query.edit_message_text(
                    text="Error: Could not identify the instrument for analysis. Please try again.",
                    reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to show error message: {str(e)}")
                try:
                    await self.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Error: Could not identify the instrument for analysis. Please try again.",
                        reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass
            return CHOOSE_ANALYSIS
        
        if instrument:
            # Set flag to indicate we're in signal flow
            if context and hasattr(context, 'user_data'):
                context.user_data['from_signal'] = True
                logger.info("Set from_signal flag to True")
            
            # Try to show loading animation first
            loading_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
            loading_text = f"Loading {instrument} chart..."
            
            # Store the current message ID to ensure we can find it later
            message_id = query.message.message_id
            chat_id = update.effective_chat.id
            logger.info(f"Current message_id: {message_id}, chat_id: {chat_id}")
            
            loading_message = None
            
            try:
                # Try to update with animated GIF first (best visual experience)
                await query.edit_message_media(
                    media=InputMediaAnimation(
                        media=loading_gif_url,
                        caption=loading_text
                    )
                )
                logger.info(f"Successfully showed loading GIF for {instrument}")
            except Exception as media_error:
                logger.warning(f"Could not update with GIF: {str(media_error)}")
                
                # If GIF fails, try to update the text
                try:
                    loading_message = await query.edit_message_text(
                        text=loading_text
                    )
                    if context and hasattr(context, 'user_data'):
                        context.user_data['loading_message'] = loading_message
                except Exception as text_error:
                    logger.warning(f"Could not update text: {str(text_error)}")
                    
                    # If text update fails, try to update caption
                    try:
                        await query.edit_message_caption(
                            caption=loading_text
                        )
                    except Exception as caption_error:
                        logger.warning(f"Could not update caption: {str(caption_error)}")
                        
                        # Last resort - send a new message with loading GIF
                        try:
                            from trading_bot.services.telegram_service.gif_utils import send_loading_gif
                            await send_loading_gif(
                                self.bot,
                                update.effective_chat.id,
                                caption=f"⏳ <b>Analyzing technical data for {instrument}...</b>"
                            )
                        except Exception as gif_error:
                            logger.warning(f"Could not show loading GIF: {str(gif_error)}")
            
            # Show technical analysis for this instrument
            return await self.show_technical_analysis(update, context, instrument=instrument)
        else:
            # Error handling - go back to signal analysis menu
            try:
                # First try to edit message text
                await query.edit_message_text(
                    text="Could not find the instrument. Please try again.",
                    reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD)
                )
            except Exception as text_error:
                # If that fails due to caption, try editing caption
                if "There is no text in the message to edit" in str(text_error):
                    try:
                        await query.edit_message_caption(
                            caption="Could not find the instrument. Please try again.",
                            reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                            parse_mode=ParseMode.HTML
                        )
                    except Exception as e:
                        logger.error(f"Failed to update caption in signal_technical_callback: {str(e)}")
                        # Try to send a new message as last resort
                        await query.message.reply_text(
                            text="Could not find the instrument. Please try again.",
                            reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                            parse_mode=ParseMode.HTML
                        )
                else:
                    # Re-raise for other errors
                    logger.error(f"Error in signal_technical_callback: {str(text_error)}")
                    # Try to send a new message as last resort
                    await query.message.reply_text(
                        text="An error occurred. Please try again.",
                        reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
            return CHOOSE_ANALYSIS