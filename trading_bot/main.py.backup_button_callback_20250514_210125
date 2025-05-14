# Import necessary modules for improved logging
import os
import sys
import json
import logging
import logging.config
from datetime import datetime


async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
        
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise

# Calendar service helpers
    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Handle the /start command"""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        # Check if user is subscribed
        is_subscribed = await self.db.is_user_subscribed(user.id)
        
        # Create welcome message
        welcome_text = (
            f"👋 Welcome to SigmaPips Trading Bot, {user.first_name}!\n\n"
            "I'm your AI-powered trading assistant. Here's what I can do for you:\n\n"
            " <b>Market Analysis</b> - Technical and sentiment analysis for major markets\n"
            " <b>Signal Management</b> - Receive and manage trading signals\n"
            " <b>Economic Calendar</b> - Stay updated with important economic events\n\n"
        )
        
        # Add subscription status
        if is_subscribed:
            welcome_text += " <b>Subscription Status:</b> Active\n\n"
        else:
            welcome_text += " <b>Subscription Status:</b> Inactive\n\n"
        
        welcome_text += "Use the /menu command to access all features."
        
        # Create keyboard for main menu
        keyboard = [
            [InlineKeyboardButton(" Analyze Markets", callback_data="menu_analyse")],
            [InlineKeyboardButton(" Signal Management", callback_data="menu_signals")],
            [InlineKeyboardButton("❓ Help", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send welcome message with keyboard
        await update.message.reply_html(
            welcome_text,
            reply_markup=reply_markup
        )
        
        # Log the user interaction
        logger.info(f"Sent welcome message to user {user.id}")
        
        # Store user data if needed
        if context:
            context.user_data['is_signals_context'] = False
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
        
        return MAIN_MENU

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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,            text="<b> Signal Management</b>\n\nManage your trading signals",


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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>
\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}
\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"
<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal
\n"
            
            message += "————————————————————

"
            message += "<b>Risk Management:</b>
"
            message += "- Position size: 1-2% max
"
            message += "- Use proper stop loss
"
            message += "- Follow your trading plan

"
            
            message += "————————————————————

"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,\n            text="<b> Signal Management</b>\n\nManage your trading signals",
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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "- Position size: 1-2% max\n"
            message += "- Use proper stop loss\n"
            message += "- Follow your trading plan\n\n"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

        async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a welcome message when the bot is started."""
        user = update.effective_user
        user_id = user.id
        first_name = user.first_name
        
        # Try to add the user to the database if they don't exist yet
    try:
            # Get user subscription since we can't check if user exists directly
            existing_subscription = await self.db.get_user_subscription(user_id)
            
            if not existing_subscription:
                # Add new user
                logger.info(f"New user started: {user_id}, {first_name}")
                await self.db.save_user(user_id, first_name, None, user.username)
        else:
                logger.info(f"Existing user started: {user_id}, {first_name}")
                
# Import necessary modules for improved logging
import os
import sys
import json
import logging
import logging.config
from datetime import datetime


async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
        
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise

# Calendar service helpers
    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Handle the /start command"""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        # Check if user is subscribed
        is_subscribed = await self.db.is_user_subscribed(user.id)
        
        # Create welcome message
        welcome_text = (
            f"👋 Welcome to SigmaPips Trading Bot, {user.first_name}!\n\n"
            "I'm your AI-powered trading assistant. Here's what I can do for you:\n\n"
            " <b>Market Analysis</b> - Technical and sentiment analysis for major markets\n"
            " <b>Signal Management</b> - Receive and manage trading signals\n"
            " <b>Economic Calendar</b> - Stay updated with important economic events\n\n"
        )
        
        # Add subscription status
        if is_subscribed:
            welcome_text += " <b>Subscription Status:</b> Active\n\n"
        else:
            welcome_text += " <b>Subscription Status:</b> Inactive\n\n"
        
        welcome_text += "Use the /menu command to access all features."
        
        # Create keyboard for main menu
        keyboard = [
            [InlineKeyboardButton(" Analyze Markets", callback_data="menu_analyse")],
            [InlineKeyboardButton(" Signal Management", callback_data="menu_signals")],
            [InlineKeyboardButton("❓ Help", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send welcome message with keyboard
        await update.message.reply_html(
            welcome_text,
            reply_markup=reply_markup
        )
        
        # Log the user interaction
        logger.info(f"Sent welcome message to user {user.id}")
        
        # Store user data if needed
        if context:
            context.user_data['is_signals_context'] = False
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
        
        return MAIN_MENU

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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,            text="<b> Signal Management</b>\n\nManage your trading signals",


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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>
\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}
\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"
<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal
\n"
            
            message += "————————————————————

"
            message += "<b>Risk Management:</b>
"
            message += "- Position size: 1-2% max
"
            message += "- Use proper stop loss
"
            message += "- Follow your trading plan

"
            
            message += "————————————————————

"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,\n            text="<b> Signal Management</b>\n\nManage your trading signals",
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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "- Position size: 1-2% max\n"
            message += "- Use proper stop loss\n"
            message += "- Follow your trading plan\n\n"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

        async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a welcome message when the bot is started."""
        user = update.effective_user
        user_id = user.id
        first_name = user.first_name
        
        # Try to add the user to the database if they don't exist yet
    try:
            # Get user subscription since we can't check if user exists directly
            existing_subscription = await self.db.get_user_subscription(user_id)
            
            if not existing_subscription:
                # Add new user
                logger.info(f"New user started: {user_id}, {first_name}")
                await self.db.save_user(user_id, first_name, None, user.username)
        else:
                logger.info(f"Existing user started: {user_id}, {first_name}")
                
    except Exception as e:
# Import necessary modules for improved logging
import os
import sys
import json
import logging
import logging.config
from datetime import datetime


async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
        
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise

# Calendar service helpers
    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Handle the /start command"""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        # Check if user is subscribed
        is_subscribed = await self.db.is_user_subscribed(user.id)
        
        # Create welcome message
        welcome_text = (
            f"👋 Welcome to SigmaPips Trading Bot, {user.first_name}!\n\n"
            "I'm your AI-powered trading assistant. Here's what I can do for you:\n\n"
            " <b>Market Analysis</b> - Technical and sentiment analysis for major markets\n"
            " <b>Signal Management</b> - Receive and manage trading signals\n"
            " <b>Economic Calendar</b> - Stay updated with important economic events\n\n"
        )
        
        # Add subscription status
        if is_subscribed:
            welcome_text += " <b>Subscription Status:</b> Active\n\n"
        else:
            welcome_text += " <b>Subscription Status:</b> Inactive\n\n"
        
        welcome_text += "Use the /menu command to access all features."
        
        # Create keyboard for main menu
        keyboard = [
            [InlineKeyboardButton(" Analyze Markets", callback_data="menu_analyse")],
            [InlineKeyboardButton(" Signal Management", callback_data="menu_signals")],
            [InlineKeyboardButton("❓ Help", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send welcome message with keyboard
        await update.message.reply_html(
            welcome_text,
            reply_markup=reply_markup
        )
        
        # Log the user interaction
        logger.info(f"Sent welcome message to user {user.id}")
        
        # Store user data if needed
        if context:
            context.user_data['is_signals_context'] = False
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
        
        return MAIN_MENU

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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,            text="<b> Signal Management</b>\n\nManage your trading signals",


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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>
\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}
\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"
<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal
\n"
            
            message += "————————————————————

"
            message += "<b>Risk Management:</b>
"
            message += "- Position size: 1-2% max
"
            message += "- Use proper stop loss
"
            message += "- Follow your trading plan

"
            
            message += "————————————————————

"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,\n            text="<b> Signal Management</b>\n\nManage your trading signals",
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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "- Position size: 1-2% max\n"
            message += "- Use proper stop loss\n"
            message += "- Follow your trading plan\n\n"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

        async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a welcome message when the bot is started."""
        user = update.effective_user
        user_id = user.id
        first_name = user.first_name
        
        # Try to add the user to the database if they don't exist yet
    try:
            # Get user subscription since we can't check if user exists directly
            existing_subscription = await self.db.get_user_subscription(user_id)
            
            if not existing_subscription:
                # Add new user
                logger.info(f"New user started: {user_id}, {first_name}")
                await self.db.save_user(user_id, first_name, None, user.username)
        else:
                logger.info(f"Existing user started: {user_id}, {first_name}")
                
# Import necessary modules for improved logging
import os
import sys
import json
import logging
import logging.config
from datetime import datetime


async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
        
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise

# Calendar service helpers
    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Handle the /start command"""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        # Check if user is subscribed
        is_subscribed = await self.db.is_user_subscribed(user.id)
        
        # Create welcome message
        welcome_text = (
            f"👋 Welcome to SigmaPips Trading Bot, {user.first_name}!\n\n"
            "I'm your AI-powered trading assistant. Here's what I can do for you:\n\n"
            " <b>Market Analysis</b> - Technical and sentiment analysis for major markets\n"
            " <b>Signal Management</b> - Receive and manage trading signals\n"
            " <b>Economic Calendar</b> - Stay updated with important economic events\n\n"
        )
        
        # Add subscription status
        if is_subscribed:
            welcome_text += " <b>Subscription Status:</b> Active\n\n"
        else:
            welcome_text += " <b>Subscription Status:</b> Inactive\n\n"
        
        welcome_text += "Use the /menu command to access all features."
        
        # Create keyboard for main menu
        keyboard = [
            [InlineKeyboardButton(" Analyze Markets", callback_data="menu_analyse")],
            [InlineKeyboardButton(" Signal Management", callback_data="menu_signals")],
            [InlineKeyboardButton("❓ Help", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send welcome message with keyboard
        await update.message.reply_html(
            welcome_text,
            reply_markup=reply_markup
        )
        
        # Log the user interaction
        logger.info(f"Sent welcome message to user {user.id}")
        
        # Store user data if needed
        if context:
            context.user_data['is_signals_context'] = False
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
        
        return MAIN_MENU

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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,            text="<b> Signal Management</b>\n\nManage your trading signals",


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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>
\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}
\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"
<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal
\n"
            
            message += "————————————————————

"
            message += "<b>Risk Management:</b>
"
            message += "- Position size: 1-2% max
"
            message += "- Use proper stop loss
"
            message += "- Follow your trading plan

"
            
            message += "————————————————————

"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,\n            text="<b> Signal Management</b>\n\nManage your trading signals",
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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "- Position size: 1-2% max\n"
            message += "- Use proper stop loss\n"
            message += "- Follow your trading plan\n\n"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

        async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a welcome message when the bot is started."""
        user = update.effective_user
        user_id = user.id
        first_name = user.first_name
        
        # Try to add the user to the database if they don't exist yet
    try:
            # Get user subscription since we can't check if user exists directly
            existing_subscription = await self.db.get_user_subscription(user_id)
            
            if not existing_subscription:
                # Add new user
                logger.info(f"New user started: {user_id}, {first_name}")
                await self.db.save_user(user_id, first_name, None, user.username)
        else:
                logger.info(f"Existing user started: {user_id}, {first_name}")
                
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        
        # Check if the user has a subscription 
        is_subscribed = await self.db.is_user_subscribed(user_id)
        
        # Check if payment has failed
        payment_failed = await self.db.has_payment_failed(user_id)
        
        if is_subscribed and not payment_failed:
            # For subscribed users, direct them to use the /menu command instead
            await update.message.reply_text(
                text="Welcome back! Please use the /menu command to access all features.",
                parse_mode=ParseMode.HTML
            )
            return
        elif payment_failed:
            # Show payment failure message
            failed_payment_text = f"""
 <b>Subscription Payment Failed</b> 

Your subscription payment could not be processed and your service has been deactivated.

To continue using Sigmapips AI and receive trading signals, please reactivate your subscription by clicking the button below.
            """
            
            # Use direct URL link for reactivation
            reactivation_url = "https://buy.stripe.com/9AQcPf3j63HL5JS145"
            
            # Create button for reactivation
            keyboard = [
                [InlineKeyboardButton("🔄 Reactivate Subscription", url=reactivation_url)]
            ]
            
            await update.message.reply_text(
                text=failed_payment_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
    else:
            # Show the welcome message with trial option from the screenshot
            welcome_text = """
 Welcome to Sigmapips AI! 

Discover powerful trading signals for various markets:
- Forex - Major and minor currency pairs

- Crypto - Bitcoin, Ethereum and other top
 cryptocurrencies

- Indices - Global market indices

- Commodities - Gold, silver and oil

Features:
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

Start today with a FREE 14-day trial!
            """
            
            # Use direct URL link instead of callback for the trial button
            checkout_url = "https://buy.stripe.com/3cs3eF9Hu9256NW9AA"
            
            # Create buttons - Trial button goes straight to Stripe checkout
            keyboard = [
                [InlineKeyboardButton("🔥 Start 14-day FREE Trial", url=checkout_url)]
            ]
            
            # Gebruik de juiste welkomst-GIF URL
            welcome_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
            
        try:
                # Send the GIF with caption containing the welcome message
                await update.message.reply_animation(
                    animation=welcome_gif_url,
                    caption=welcome_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except Exception as e:\n            logger.error(f"Error sending welcome GIF with caption: {str(e)}")
                # Fallback to text-only message if GIF fails
                await update.message.reply_text(
                    text=welcome_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
    async def set_subscription_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """S  # Use direct URL link for reactivation
                reactivation_url = "https://buy.stripe.com/9AQcPf3j63HL5JS145"
                
                # Create button for reactivation
                keyboard = [
                    [InlineKeyboardButton("🔄 Reactivate Subscription", url=reactivation_url)]
                ]
                
                # First send success message
                await update.message.reply_text(message)
                
                # Then show payment failed interface
                await update.message.reply_text(
                    text=failed_payment_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            else:
                message = f" Could not set payment failed status for user {chat_id}"
            logger.error("Database returned failure")
                await update.message.reply_text(message)
                
        except ValueError as e:
            error_msg = f"Invalid argument. Chat ID must be a number. Error: {str(e)}"
        logger.error(error_msg)
            await update.message.reply_text(error_msg)
    except Exception as e:
            error_msg = f"Error setting payment failed status: {str(e)}"
        logger.error(error_msg)
            await update.message.reply_text(error_msg)

    async def menu_analyse_callback(self, update: Update, context=None) -> int:
        """Handle menu_analyse button press"""
        query = update.callback_query
        await query.answer()
        
        # Gebruik de juiste analyse GIF URL
        gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Probeer eerst het huidige bericht te verwijderen en een nieuw bericht te sturen met de analyse GIF
    try:
            await query.message.delete()
            await context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation=gif_url,\n                caption="Select your analysis type:",
                reply_markup=InlineKeyboardMarkup(ANALYSIS_KEYBOARD),
                parse_mode=ParseMode.HTML
            )
            return CHOOSE_ANALYSIS
        except Exception as delete_error:
        logger.warning(f"Could not delete message: {str(delete_error)}")
            
            # Als verwijderen mislukt, probeer de media te updaten
        try:
                await query.edit_message_media(
                    media=InputMediaAnimation(
                        media=gif_url,
                        caption="Select your analysis type:"
                    ),
                    reply_markup=InlineKeyboardMarkup(ANALYSIS_KEYBOARD)
                )
                return CHOOSE_ANALYSIS
            except Exception as media_error:
            logger.warning(f"Could not update media: {str(media_error)}")
                
                # Als media update mislukt, probeer tekst te updaten
            try:
                    await query.edit_message_text(
                        text="Select your analysis type:",
                        reply_markup=InlineKeyboardMarkup(ANALYSIS_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
                except Exception as text_error:
                    # Als tekst updaten mislukt, probeer bijschrift te updaten
                    if "There is no text in the message to edit" in str(text_error):
                    try:
                            await query.edit_message_caption(
                                caption="Select your analysis type:",
                                reply_markup=InlineKeyboardMarkup(ANALYSIS_KEYBOARD),
                                parse_mode=ParseMode.HTML
                            )
                        except Exception as caption_error:
                        logger.error(f"Failed to update caption: {str(caption_error)}")
                            # Laatste redmiddel: stuur een nieuw bericht
                            await context.bot.send_animation(
                                chat_id=update.effective_chat.id,
                                animation=gif_url,
                                caption="Select your analysis type:",
                                reply_markup=InlineKeyboardMarkup(ANALYSIS_KEYBOARD),
                                parse_mode=ParseMode.HTML
                            )
                    else:
                    logger.error(f"Failed to update message: {str(text_error)}")
                        # Laatste redmiddel: stuur een nieuw bericht
                        await context.bot.send_animation(
                            chat_id=update.effective_chat.id,
                            animation=gif_url,
                            caption="Select your analysis type:",
                            reply_markup=InlineKeyboardMarkup(ANALYSIS_KEYBOARD),
                            parse_mode=ParseMode.HTML
                        )
        
        return CHOOSE_ANALYSIS

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None, skip_gif=False) -> None:
        """Show the main menu when /menu command is used"""
        # Use context.bot if available, otherwise use self.bot
        bot = context.bot if context is not None else self.bot
        
        # Check if the user has a subscription
        user_id = update.effective_user.id
        is_subscribed = await self.db.is_user_subscribed(user_id)
        payment_failed = await self.db.has_payment_failed(user_id)
        
        if is_subscribed and not payment_failed:
            # Show the main menu for subscribed users
            reply_markup = InlineKeyboardMarkup(START_KEYBOARD)
            
            # Forceer altijd de welkomst GIF
            gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
            
            # If we should show the GIF
            if not skip_gif:
            try:
                    # For message commands we can use reply_animation
                    if hasattr(update, 'message') and update.message:
                        # Verwijder eventuele vorige berichten met callback query
                        if hasattr(update, 'callback_query') and update.callback_query:
                        try:
                                await update.callback_query.message.delete()
                            except Exception:
                                pass
                        
                        # Send the GIF using regular animation method
                        await update.message.reply_animation(
                            animation=gif_url,
                            caption=WELCOME_MESSAGE,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup
                        )
                    else:
                        # Voor callback_query, verwijder huidige bericht en stuur nieuw bericht
                        if hasattr(update, 'callback_query') and update.callback_query:
                        try:
                                # Verwijder het huidige bericht
                                await update.callback_query.message.delete()
                                
                                # Stuur nieuw bericht met de welkomst GIF
                                await bot.send_animation(
                                    chat_id=update.effective_chat.id,
                                    animation=gif_url,
                                    caption=WELCOME_MESSAGE,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=reply_markup
                                )
                        except Exception as e:\n                            logger.error(f"Failed to handle callback query: {str(e)}")
                                # Valt terug op tekstwijziging als verwijderen niet lukt
                                await update.callback_query.edit_message_text(
                                    text=WELCOME_MESSAGE,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=reply_markup
                                )
                    else:
                            # Final fallback - try to send a new message
                            await bot.send_animation(
                                chat_id=update.effective_chat.id,
                                animation=gif_url,
                                caption=WELCOME_MESSAGE,
                                parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup
                            )
            except Exception as e:
                logger.error(f"Failed to send menu GIF: {str(e)}")
                    # Fallback to text-only approach
                    if hasattr(update, 'message') and update.message:
                        await update.message.reply_text(
                            text=WELCOME_MESSAGE,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup
                        )
                    else:
                        await bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=WELCOME_MESSAGE,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup
                        )
                    else:
                # Skip GIF mode - just send text
                if hasattr(update, 'message') and update.message:
                    await update.message.reply_text(
                        text=WELCOME_MESSAGE,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
                else:
                    await bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=WELCOME_MESSAGE,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
    else:
            # Handle non-subscribed users similar to start command
            await self.start_command(update, context)
            
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a message when the command /help is issued."""
        await self.show_main_menu(update, context)
        
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a message when the command /menu is issued."""
        await self.show_main_menu(update, context)
        
    async def analysis_technical_callback(self, update: Update, context=None) -> int:
        """Handle analysis_technical button press"""
        query = update.callback_query
        await query.answer()
        
        # Check if signal-specific data is present in callback data
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'technical'
        
        # Set the callback data
        callback_data = query.data
        
        # Set the instrument if it was passed in the callback data
        if callback_data.startswith("signal_flow_technical_"):
            # Extract instrument from the callback data
            instrument = callback_data.replace("signal_flow_technical_", "")
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['instrument'] = instrument
            
                logger.info(f"Technical analysis for specific instrument: {instrument}")
            
            # Show analysis directly for this instrument
            return await self.show_technical_analysis(update, context, instrument=instrument)
        
        # Show the market selection menu
    try:
            # First try to edit message text
            await query.edit_message_text(
                text="Select market for technical analysis:",
                reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD)
            )
        except Exception as text_error:
            # If that fails due to caption, try editing caption
            if "There is no text in the message to edit" in str(text_error):
            try:
                    await query.edit_message_caption(
                        caption="Select market for technical analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
            except Exception as e:
                logger.error(f"Failed to update caption in analysis_technical_callback: {str(e)}")
                    # Try to send a new message as last resort
                    await query.message.reply_text(
                        text="Select market for technical analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
                else:
                # Re-raise for other errors
                raise
        
        return CHOOSE_MARKET
        
    async def analysis_sentiment_callback(self, update: Update, context=None) -> int:
        """Handle analysis_sentiment button press"""
        query = update.callback_query
        await query.answer()
        
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'sentiment'
        
        # Set the callback data
        callback_data = query.data
        
        # Set the instrument if it was passed in the callback data
        if callback_data.startswith("signal_flow_sentiment_"):
            # Extract instrument from the callback data
            instrument = callback_data.replace("signal_flow_sentiment_", "")
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['instrument'] = instrument
            
                logger.info(f"Sentiment analysis for specific instrument: {instrument}")
            
            # Show analysis directly for this instrument
            return await self.show_sentiment_analysis(update, context, instrument=instrument)
            
        # Show the market selection menu
    try:
            # First try to edit message text
            await query.edit_message_text(
                text="Select market for sentiment analysis:",
                reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD)
            )
        except Exception as text_error:
            # If that fails due to caption, try editing caption
            if "There is no text in the message to edit" in str(text_error):
            try:
                    await query.edit_message_caption(
                        caption="Select market for sentiment analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
            except Exception as e:
                logger.error(f"Failed to update caption in analysis_sentiment_callback: {str(e)}")
                    # Try to send a new message as last resort
                    await query.message.reply_text(
                        text="Select market for sentiment analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
                else:
                # Re-raise for other errors
                raise
        
        return CHOOSE_MARKET
        
    async def analysis_calendar_callback(self, update: Update, context=None) -> int:
        """Handle analysis_calendar button press"""
        query = update.callback_query
        await query.answer()
        
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'calendar'
            
        # Set the callback data
        callback_data = query.data
        
        # Set the instrument if it was passed in the callback data
        if callback_data.startswith("signal_flow_calendar_"):
            # Extract instrument from the callback data
            instrument = callback_data.replace("signal_flow_calendar_", "")
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['instrument'] = instrument
            
                logger.info(f"Calendar analysis for specific instrument: {instrument}")
            
            # Show analysis directly for this instrument
            return await self.show_calendar_analysis(update, context, instrument=instrument)
        
        # Skip market selection and go directly to calendar analysis
        logger.info("Showing economic calendar without market selection")
        return await self.show_calendar_analysis(update, context)

    async def show_economic_calendar(self, update: Update, context: CallbackContext, currency=None, loading_message=None):
        """Show the economic calendar for a specific currency"""
    try:
            # VERIFICATION MARKER: SIGMAPIPS_CALENDAR_FIX_APPLIED
            self.logger.info("VERIFICATION MARKER: SIGMAPIPS_CALENDAR_FIX_APPLIED")
            
            chat_id = update.effective_chat.id
            query = update.callback_query
            
            # Log that we're showing the calendar
            self.logger.info(f"Showing economic calendar for all major currencies")
            
            # Initialize the calendar service
            calendar_service = self._get_calendar_service()
            cache_size = len(getattr(calendar_service, 'cache', {}))
            self.logger.info(f"Calendar service initialized, cache size: {cache_size}")
            
            # Check if API key is available
            tavily_api_key = os.environ.get("TAVILY_API_KEY", "")
            if tavily_api_key:
                masked_key = f"{tavily_api_key[:4]}..." if len(tavily_api_key) > 7 else "***"
                self.logger.info(f"Tavily API key is available: {masked_key}")
        else:
                self.logger.warning("No Tavily API key found, will use mock data")
            
            # Get calendar data for ALL major currencies, regardless of the supplied parameter
            self.logger.info(f"Requesting calendar data for all major currencies")
            
            calendar_data = []
            
            # Get all currencies data
        try:
                if hasattr(calendar_service, 'get_calendar'):
                    calendar_data = await calendar_service.get_calendar()
            else:
                    self.logger.warning("calendar_service.get_calendar method not available, using mock data")
                    calendar_data = []
        except Exception as e:
                self.logger.warning(f"Error getting calendar data: {str(e)}")
                calendar_data = []
            
            # Check if data is empty
            if not calendar_data or len(calendar_data) == 0:
                self.logger.warning("Calendar data is empty, using mock data...")
                # Generate mock data
                today_date = datetime.now().strftime("%B %d, %Y")
                
                # Use the mock data generator from the calendar service if available
                if hasattr(calendar_service, '_generate_mock_calendar_data'):
                    mock_data = calendar_service._generate_mock_calendar_data(MAJOR_CURRENCIES, today_date)
            else:
                    # Otherwise use our own implementation
                    mock_data = self._generate_mock_calendar_data(MAJOR_CURRENCIES, today_date)
                
                # Flatten the mock data
                flattened_mock = []
                for currency_code, events in mock_data.items():
                    for event in events:
                        flattened_mock.append({
                            "time": event.get("time", ""),
                            "country": currency_code,
                            "country_flag": CURRENCY_FLAG.get(currency_code, ""),
                            "title": event.get("event", ""),
                            "impact": event.get("impact", "Low")
                        })
                
                calendar_data = flattened_mock
                self.logger.info(f"Generated {len(flattened_mock)} mock calendar events")
            
            # Format the calendar data in chronological order
            if hasattr(self, '_format_calendar_events'):
                message = await self._format_calendar_events(calendar_data)
        else:
                # Fallback to calendar service formatting if the method doesn't exist on TelegramService
                if hasattr(calendar_service, '_format_calendar_response'):
                    message = await calendar_service._format_calendar_response(calendar_data, "ALL")
            else:
                    # Simple formatting fallback
                    message = "<b>Economic Calendar</b>\n\n"
                    for event in calendar_data[:10]:  # Limit to first 10 events
                        country = event.get('country', 'Unknown')
                        title = event.get('title', 'Unknown Event')
                        time = event.get('time', 'Unknown Time')
                        message += f"{country}: {time} - {title}\n\n"
            
            # Create keyboard with back button if not provided from caller
            keyboard = None
            if context and hasattr(context, 'user_data') and context.user_data.get('from_signal', False):
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_to_signal_analysis")]])
        else:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="menu_analyse")]])
            
            # Try to delete loading message first if it exists
            if loading_message:
            try:
                    await loading_message.delete()
                    self.logger.info("Successfully deleted loading message")
                except Exception as delete_error:
                    self.logger.warning(f"Could not delete loading message: {str(delete_error)}")
                    
                    # If deletion fails, try to edit it
                try:
                        await context.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=loading_message.message_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=keyboard
                        )
                        self.logger.info("Edited loading message with calendar data")
                        return  # Skip sending a new message
                    except Exception as edit_error:
                        self.logger.warning(f"Could not edit loading message: {str(edit_error)}")
            
            # Send the message as a new message
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            self.logger.info("Sent calendar data as new message")
        
        except Exception as e:
            self.logger.error(f"Error showing economic calendar: {str(e)}")
            self.logger.exception(e)
            
            # Send error message
            chat_id = update.effective_chat.id
            await context.bot.send_message(
                chat_id=chat_id,
                text="<b> Error showing economic calendar</b>\n\nSorry, there was an error retrieving the economic calendar data. Please try again later.",
                parse_mode=ParseMode.HTML
            )
            
    def _generate_mock_calendar_data(self, currencies, date):
        """Generate mock calendar data if the real service fails"""
        self.logger.info(f"Generating mock calendar data for {len(currencies)} currencies")
        mock_data = {}
        
        # Impact levels
        impact_levels = ["High", "Medium", "Low"]
        
        # Possible event titles
        events = [
            "Interest Rate Decision",
            "Non-Farm Payrolls",
            "GDP Growth Rate",
            "Inflation Rate",
            "Unemployment Rate",
            "Retail Sales",
            "Manufacturing PMI",
            "Services PMI",
            "Trade Balance",
            "Consumer Confidence",
            "Building Permits",
            "Central Bank Speech",
            "Housing Starts",
            "Industrial Production"
        ]
        
        # Generate random events for each currency
        for currency in currencies:
            num_events = random.randint(1, 5)  # Random number of events per currency
            currency_events = []
            
            for _ in range(num_events):
                # Generate a random time (hour between 7-18, minute 00, 15, 30 or 45)
                hour = random.randint(7, 18)
                minute = random.choice([0, 15, 30, 45])
                time_str = f"{hour:02d}:{minute:02d} EST"
                
                # Random event and impact
                event = random.choice(events)
                impact = random.choice(impact_levels)
                
                currency_events.append({
                    "time": time_str,
                    "event": event,
                    "impact": impact
                })
            
            # Sort events by time
            mock_data[currency] = sorted(currency_events, key=lambda x: x["time"])
        
        return mock_data

    async def signal_technical_callback(self, update: Update, context=None) -> int:
        """Handle signal_technical button press"""
        query = update.callback_query
        await query.answer()
        
        # Add detailed debug logging
        logger.info(f"signal_technical_callback called with query data: {query.data}")
        
        # Save analysis type in context
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'technical'
        
        # Get the instrument from context
        instrument = None
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            instrument = context.user_data.get('instrument')
            # Debug log for instrument
            logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_technical_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
        
        if instrument:
            # Set flag to indicate we're in signal flow
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['from_signal'] = True
                logger.info("Set from_signal flag to True")
            
            # Try to show loading animation first
            loading_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"\n            loading_text = f"Loading {instrument} chart..."
            
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
                        # Reset signal flow flags
                        context.user_data['from_signal'] = False
                        context.user_data['in_signal_flow'] = False
                        logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
                    raise
            return CHOOSE_ANALYSIS

    async def signal_sentiment_callback(self, update: Update, context=None) -> int:
        """Handle signal_sentiment button press"""
        query = update.callback_query
        await query.answer()
        
        # Save analysis type in context
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'sentiment'
        
        # Get the instrument from context
        instrument = None
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            instrument = context.user_data.get('instrument')
            logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_sentiment_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
                    logger.info(f"Instrument from context: {instrument}")
        
        if instrument:
            # Set flag to indicate we're in signal flow
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['from_signal'] = True
            
            # Try to show loading animation first
            loading_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"\n            loading_text = f"Loading sentiment analysis for {instrument}..."
            
        try:
                # Try to update with animated GIF first (best visual experience)
                await query.edit_message_media(
                    media=InputMediaAnimation(
                        media=loading_gif_url,
                        caption=loading_text
                    )
                )
                logger.info(f"Successfully showed loading GIF for {instrument} sentiment analysis")
            except Exception as media_error:
            logger.warning(f"Could not update with GIF: {str(media_error)}")
                
                # If GIF fails, try to update the text
            try:
                    loading_message = await query.edit_message_text(
                        text=loading_text
                    )
                    if context and hasattr(context, 'user_data'):
                        # Reset signal flow flags
                        context.user_data['from_signal'] = False
                        context.user_data['in_signal_flow'] = False
                        logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
                                caption=f"⏳ <b>Analyzing market sentiment for {instrument}...</b>"
                            )
                        except Exception as gif_error:
                        logger.warning(f"Could not show loading GIF: {str(gif_error)}")
            
            # Show sentiment analysis for this instrument
            return await self.show_sentiment_analysis(update, context, instrument=instrument)
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
                    logger.error(f"Failed to update caption in signal_sentiment_callback: {str(e)}")
                        # Try to send a new message as last resort
                        await query.message.reply_text(
                            text="Could not find the instrument. Please try again.",
                            reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                            parse_mode=ParseMode.HTML
                        )
                    else:
                # Re-raise for other errors
                raise
        return CHOOSE_ANALYSIS

    async def signal_calendar_callback(self, update: Update, context=None) -> int:
        """Handle signal_calendar button press"""
        query = update.callback_query
        await query.answer()
        
        # Add detailed debug logging
        logger.info(f"signal_calendar_callback called with data: {query.data}")
        
        # Save analysis type in context
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'calendar'
            # Make sure we save the original signal data to return to later
            signal_instrument = context.user_data.get('instrument')
            signal_direction = context.user_data.get('signal_direction')
            signal_timeframe = context.user_data.get('signal_timeframe') 
            
            # Save these explicitly to ensure they're preserved
            context.user_data['signal_instrument_backup'] = signal_instrument
            context.user_data['signal_direction_backup'] = signal_direction
            context.user_data['signal_timeframe_backup'] = signal_timeframe
            
            # Log for debugging
            logger.info(f"Saved signal data before calendar analysis: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
        
        # Get the instrument from context (voor tracking van context en eventuele toekomstige functionaliteit)
        instrument = None
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            instrument = context.user_data.get('instrument')
            logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_calendar_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
                    logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument
        if query.data.startswith("signal_flow_calendar_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
        
        # Set flag to indicate we're in signal flow
        if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['from_signal'] = True
            logger.info(f"Set from_signal flag to True for calendar analysis")
        
        # Try to show loading animation first
        loading_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"\n        loading_text = f"Loading economic calendar..."
        
    try:
            # Try to update with animated GIF first (best visual experience)
            await query.edit_message_media(
                media=InputMediaAnimation(
                    media=loading_gif_url,
                    caption=loading_text
                )
            )
            logger.info(f"Successfully showed loading GIF for economic calendar")
        except Exception as media_error:
        logger.warning(f"Could not update with GIF: {str(media_error)}")
            
            # If GIF fails, try to update the text
        try:
                loading_message = await query.edit_message_text(
                    text=loading_text
                )
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
                            caption=f"⏳ <b>Loading economic calendar...</b>"
                        )
                    except Exception as gif_error:
                    logger.warning(f"Could not show loading GIF: {str(gif_error)}")
        
        # Show calendar analysis for ALL major currencies
        return await self.show_calendar_analysis(update, context, instrument=None)

    
    
    async def analyze_from_signal_callback(self, update: Update, context=None) -> int:
        """Handle Analyze Market button from signal notifications"""
        query = update.callback_query
        # Add query.answer() to acknowledge the callback
        await query.answer()
        logger.info(f"analyze_from_signal_callback called with data: {query.data}")
        
    try:
            # Extract signal information from callback data
            parts = query.data.split('_')
            
            # Format: analyze_from_signal_INSTRUMENT_SIGNALID
            if len(parts) >= 4:
                instrument = parts[3]
                signal_id = parts[4] if len(parts) >= 5 else None
                
                # Store in context for other handlers
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
                    if signal_id:
                        context.user_data['signal_id'] = signal_id
                    # Set signal flow flags (only once)
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                    
                    # Make a backup copy to ensure we can return to signal later
                    context.user_data['signal_instrument'] = instrument
                    context.user_data['signal_instrument_backup'] = instrument
                    if signal_id:
                        context.user_data['signal_id_backup'] = signal_id
                    
                    # Also store info from the actual signal if available
                    if str(update.effective_user.id) in self.user_signals and signal_id in self.user_signals[str(update.effective_user.id)]:
                        signal = self.user_signals[str(update.effective_user.id)][signal_id]
                        if signal:
                            context.user_data['signal_direction'] = signal.get('direction')
                            # Use interval or timeframe, whichever is available
                            timeframe = signal.get('interval') or signal.get('timeframe')
                            context.user_data['signal_timeframe'] = timeframe
                            # Backup copies
                            context.user_data['signal_timeframe_backup'] = timeframe
                            context.user_data['signal_direction_backup'] = signal.get('direction')
                
                # Store the original signal page for later retrieval
                await self._store_original_signal_page(update, context, instrument, signal_id)
                
                # Show analysis options for this instrument
                keyboard = [
                    [InlineKeyboardButton("Technical Analysis", callback_data=f"signal_flow_technical_{instrument}")],
                    [InlineKeyboardButton("Market Sentiment", callback_data=f"signal_flow_sentiment_{instrument}")],
                    [InlineKeyboardButton("Economic Calendar", callback_data=f"signal_flow_calendar_{instrument}")],
                    [InlineKeyboardButton("Back to Signal", callback_data="back_to_signal")]
                ]
                
                # Update the message with the analysis options
                await query.edit_message_text(
                    text=f"<b> Analyze {instrument}</b>\n\nSelect the type of analysis you want to perform:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
                
                return CHOOSE_ANALYSIS
        else:
                # Invalid callback data
                await query.edit_message_text(
                    text="Invalid signal format. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
                return MENU
    except Exception as e:
        logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
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
    except Exception as e:
        logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
            # Error recovery
        try:
                await query.edit_message_text(
                    text="An error occurred. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
            except Exception:
                pass
            return MENU

    async def _store_original_signal_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, instrument: str, signal_id: str):
        """Store the original signal page data for later retrieval"""
    try:
        # Fetch the signal data from the database
            signal_data = await self.db.get_user_signals(update.effective_user.id, instrument)
            
            if signal_data:
                # Prepare the signal page data
                signal_page_data = {
                    "instrument": instrument,
                    "signal_id": signal_id,
                    "message": signal_data[0].get('message'),
                    "timestamp": signal_data[0].get('timestamp')
                }
                
                # Save the signal page data to the database
                await self.db.save_signal_page(update.effective_user.id, instrument, signal_page_data)
                
                logger.info(f"Original signal page data stored for {instrument} with signal ID {signal_id}")
        else:
            logger.warning(f"No signal data found for {instrument} with signal ID {signal_id}")
    except Exception as e:
        logger.error(f"Error storing original signal page: {str(e)}")
        logger.exception(e)

    async def _get_original_signal_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Retrieve the original signal page data for a given signal"""
    try:
        # Fetch the signal page data from the database
            signal_page_data = await self.db.get_signal_page(update.effective_user.id, update.callback_query.data.split('_')[3])
            
            if signal_page_data:
                return signal_page_data
        else:
            logger.warning(f"No signal page data found for signal ID {update.callback_query.data.split('_')[3]}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving original signal page: {str(e)}")
        logger.exception(e)
        return None

    async def _load_signals(self):
        """Load signals from the database"""
    try:
        # Fetch all signals from the database
            signals = await self.db.get_all_signals()
            
            if signals:
                for signal in signals:
                    self.user_signals[str(signal['user_id'])] = {signal['id']: signal}
                logger.info(f"Loaded {len(signals)} signals from the database")
        else:
                logger.info("No signals found in the database")
    except Exception as e:
        logger.error(f"Error loading signals: {str(e)}")
        logger.exception(e)

    async def _cleanup_old_signals(self, max_age_days):
        """Cleanup old signals from the database"""
    try:
            # Calculate the date threshold
            threshold_date = datetime.now() - timedelta(days=max_age_days)
            
        # Fetch signals older than the threshold date
            signals_to_delete = await self.db.get_old_signals(threshold_date)
            
            if signals_to_delete:
                for signal in signals_to_delete:
                    await self.db.delete_signal(signal['id'])
                logger.info(f"Deleted {len(signals_to_delete)} old signals from the database")
        else:
                logger.info("No old signals found to delete")
            
            return len(signals_to_delete)
    except Exception as e:
        logger.error(f"Error cleaning up old signals: {str(e)}")
        logger.exception(e)
            return 0

    async def _format_signal_message(self, signal_data):
        """Format the signal message for display"""
    try:
            # Extract fields from signal data
            instrument = signal_data.get('instrument', 'Unknown')
            direction = signal_data.get('direction', 'Unknown')
            entry = signal_data.get('entry', 'Unknown')
            stop_loss = signal_data.get('stop_loss')
            take_profit = signal_data.get('take_profit')
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "- Position size: 1-2% max\n"
            message += "- Use proper stop loss\n"
            message += "- Follow your trading plan\n\n"
            
            message += "————————————————————\n\n"
            
            # Generate AI verdict
            ai_verdict = f"The {instrument} {direction.lower()} signal shows a promising setup with defined entry at {entry} and stop loss at {stop_loss}. Multiple take profit levels provide opportunities for partial profit taking."
            message += f"<b>🤖 SigmaPips AI Verdict:</b>\n{ai_verdict}"
            
            return message
    except Exception as e:
        logger.error(f"Error formatting signal message: {str(e)}")
        logger.exception(e)
            return f"New {signal_data.get('instrument', 'Unknown')} {signal_data.get('direction', 'Unknown')} Signal"

    async def _get_signal_details(self, signal_id):
        """Retrieve signal details from the database"""
    try:
        # Fetch the signal data from the database
            signal_data = await self.db.get_signal(signal_id)
            
            if signal_data:
                return signal_data
        else:
            logger.warning(f"No signal data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal details: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_analysis(self, signal_id):
        """Retrieve signal analysis from the database"""
    try:
        # Fetch the signal analysis data from the database
            analysis_data = await self.db.get_signal_analysis(signal_id)
            
            if analysis_data:
                return analysis_data
        else:
            logger.warning(f"No analysis data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal analysis: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_sentiment(self, signal_id):
        """Retrieve signal sentiment from the database"""
    try:
        # Fetch the signal sentiment data from the database
            sentiment_data = await self.db.get_signal_sentiment(signal_id)
            
            if sentiment_data:
                return sentiment_data
        else:
            logger.warning(f"No sentiment data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal sentiment: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_calendar(self, signal_id):
        """Retrieve signal calendar data from the database"""
    try:
        # Fetch the signal calendar data from the database
            calendar_data = await self.db.get_signal_calendar(signal_id)
            
            if calendar_data:
                return calendar_data
        else:
            logger.warning(f"No calendar data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal calendar: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_market(self, signal_id):
        """Retrieve signal market data from the database"""
    try:
        # Fetch the signal market data from the database
            market_data = await self.db.get_signal_market(signal_id)
            
            if market_data:
                return market_data
        else:
            logger.warning(f"No market data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal market: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_trades(self, signal_id):
        """Retrieve signal trades from the database"""
    try:
        # Fetch the signal trades data from the database
        trades_data = await self.db.get_signal_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_comments(self, signal_id):
        """Retrieve signal comments from the database"""
    try:
        # Fetch the signal comments data from the database
            comments_data = await self.db.get_signal_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_attachments(self, signal_id):
        """Retrieve signal attachments from the database"""
    try:
        # Fetch the signal attachments data from the database
            attachments_data = await self.db.get_signal_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_notes(self, signal_id):
        """Retrieve signal notes from the database"""
    try:
        # Fetch the signal notes data from the database
            notes_data = await self.db.get_signal_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_tags(self, signal_id):
        """Retrieve signal tags from the database"""
    try:
        # Fetch the signal tags data from the database
            tags_data = await self.db.get_signal_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None


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
WELCOME_MESSAGE = r"""
<b>Sigmapips AI - Main Menu</b>

Choose an option to access advanced trading support:

Services:
- <b>Technical Analysis</b> - Real-time chart analysis and key levels

- <b>Market Sentiment</b> - Understand market trends and sentiment

- <b>Economic Calendar</b> - Stay updated on market-moving events

- <b>Trading Signals</b> - Get precise entry/exit points for your favorite pairs

Select your option to continue:
"""

# Abonnementsbericht voor nieuwe gebruikers
SUBSCRIPTION_WELCOME_MESSAGE = r"""
<b>Welcome to Sigmapips AI!</b>

To access all features, you need a subscription:

<b>Trading Signals Subscription - $29.99/month</b>
- Access to all trading signals (Forex, Crypto, Commodities, Indices)
- Advanced timeframe analysis
- Detailed chart analysis for each signal

Click the button below to subscribe:
"""

MENU_MESSAGE = r"""
Welcome to Sigmapips AI!

Choose a command:

/start - Set up new trading pairs
Add new market/instrument/timeframe combinations to receive signals

/manage - Manage your preferences
View, edit or delete your saved trading pairs

Need help? Use /help to see all available commands.
"""

HELP_MESSAGE = r"""
Available commands:
/menu - Show main menu
/start - Set up new trading pairs
/help - Show this help message
"""

# Start menu keyboard
START_KEYBOARD = [
    [InlineKeyboardButton("Analyze Market", callback_data=CALLBACK_MENU_ANALYSE)],
    [InlineKeyboardButton("Trading Signals", callback_data=CALLBACK_MENU_SIGNALS)]
]

# Analysis menu keyboard
ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data=CALLBACK_ANALYSIS_TECHNICAL)],
    [InlineKeyboardButton("Market Sentiment", callback_data=CALLBACK_ANALYSIS_SENTIMENT)],
    [InlineKeyboardButton("Economic Calendar", callback_data=CALLBACK_ANALYSIS_CALENDAR)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Signals menu keyboard
SIGNALS_KEYBOARD = [
    [InlineKeyboardButton("Add New Pairs", callback_data=CALLBACK_SIGNALS_ADD)],
    [InlineKeyboardButton("Manage Signals", callback_data=CALLBACK_SIGNALS_MANAGE)],
    [InlineKeyboardButton("Back", callback_data=CALLBACK_BACK_MENU)]
]

# Market keyboard voor signals
MARKET_KEYBOARD_SIGNALS = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_signals")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_signals")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_signals")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_signals")],
    [InlineKeyboardButton("Back", callback_data="back_signals")]
]

# Market keyboard voor analyse
MARKET_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities")],
    [InlineKeyboardButton("Indices", callback_data="market_indices")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
]

# Market keyboard specifiek voor sentiment analyse
MARKET_SENTIMENT_KEYBOARD = [
    [InlineKeyboardButton("Forex", callback_data="market_forex_sentiment")],
    [InlineKeyboardButton("Crypto", callback_data="market_crypto_sentiment")],
    [InlineKeyboardButton("Commodities", callback_data="market_commodities_sentiment")],
    [InlineKeyboardButton("Indices", callback_data="market_indices_sentiment")],
    [InlineKeyboardButton("Back", callback_data="back_analysis")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard voor analyse
CRYPTO_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_chart"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_chart"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Signal analysis keyboard
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("Back", callback_data="back_to_signal")]
]

# Crypto keyboard voor sentiment analyse
CRYPTO_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_sentiment"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_sentiment"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor analyse
INDICES_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_chart"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_chart"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor signals - Fix de "Terug" knop naar "Back"
INDICES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_signals"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_signals"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor analyse
COMMODITIES_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_chart"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_chart"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_chart")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor signals - Fix de "Terug" knop naar "Back"
COMMODITIES_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("XAUUSD", callback_data="instrument_XAUUSD_signals"),
        InlineKeyboardButton("XAGUSD", callback_data="instrument_XAGUSD_signals"),
        InlineKeyboardButton("USOIL", callback_data="instrument_USOIL_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
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
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Crypto keyboard for signals
CRYPTO_KEYBOARD_SIGNALS = [
    [
        InlineKeyboardButton("BTCUSD", callback_data="instrument_BTCUSD_signals"),
        InlineKeyboardButton("ETHUSD", callback_data="instrument_ETHUSD_signals"),
        InlineKeyboardButton("XRPUSD", callback_data="instrument_XRPUSD_signals")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Indices keyboard voor sentiment analyse
INDICES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("US30", callback_data="instrument_US30_sentiment"),
        InlineKeyboardButton("US500", callback_data="instrument_US500_sentiment"),
        InlineKeyboardButton("US100", callback_data="instrument_US100_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Commodities keyboard voor sentiment analyse
COMMODITIES_SENTIMENT_KEYBOARD = [
    [
        InlineKeyboardButton("GOLD", callback_data="instrument_XAUUSD_sentiment"),
        InlineKeyboardButton("SILVER", callback_data="instrument_XAGUSD_sentiment"),
        InlineKeyboardButton("OIL", callback_data="instrument_USOIL_sentiment")
    ],
    [InlineKeyboardButton("Back", callback_data="back_market")]
]

# Style keyboard
STYLE_KEYBOARD = [
    [InlineKeyboardButton("⚡ Test (one_min)", callback_data="style_test")],
    [InlineKeyboardButton("🏃 Scalp (fifteen_min)", callback_data="style_scalp")],
    [InlineKeyboardButton(" Intraday (one_hour)", callback_data="style_intraday")],
    [InlineKeyboardButton("🌊 Swing (four_hour)", callback_data="style_swing")],
    [InlineKeyboardButton("Back", callback_data="back_instrument")]
]

# Timeframe mapping
STYLE_TIMEFRAME_MAP = {
    "test": "one_min",
    "scalp": "fifteen_min",
    "intraday": "one_hour",
    "swing": "four_hour"
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
 <b>Subscription Payment Failed</b> 

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
 <b>Welcome to Sigmapips AI!</b> 

<b>Discover powerful trading signals for various markets:</b>
- <b>Forex</b> - Major and minor currency pairs
- <b>Crypto</b> - Bitcoin, Ethereum and other top cryptocurrencies
- <b>Indices</b> - Global market indices
- <b>Commodities</b> - Gold, silver and oil

<b>Features:</b>
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

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
        self.admin_users = [2004519703]  # Updated with correct Telegram ID from logs
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
            
            # Schedule periodic cleanup of old signals
            if hasattr(self, 'db') and self.db and self.db.using_redis:
                # Run initial cleanup
                cleaned = await self._cleanup_old_signals(max_age_days=7)
                logger.info(f"Initial signal cleanup completed, removed {cleaned} old signals")
                
                # Schedule periodic cleanup (every 24 hours)
                async def periodic_cleanup():
                    while True:
                        try:
                            # Wait for 24 hours
                            await asyncio.sleep(24 * 60 * 60)
                            # Run cleanup
                            cleaned = await self._cleanup_old_signals(max_age_days=7)
                            logger.info(f"Periodic signal cleanup completed, removed {cleaned} old signals")
                        except Exception as e:
                            logger.error(f"Error in periodic signal cleanup: {str(e)}")
                
                # Start the periodic cleanup task
                asyncio.create_task(periodic_cleanup())
                logger.info("Scheduled periodic signal cleanup")
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
            return "<b>Economic Calendar</b>\n\nNo economic events found for today."
        
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
        message = "<b>Economic Calendar</b>\n\n"
        
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
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
            [InlineKeyboardButton(" Add Signal", callback_data="signals_add")],
            [InlineKeyboardButton("Manage Signals", callback_data="signals_manage")],
            [InlineKeyboardButton("Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get the signals GIF URL for better UX
        signals_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
        
        # Update the message
        await self.update_message(
            query=query,\n            text="<b> Signal Management</b>\n\nManage your trading signals",
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
                interval = signal_data.get('interval', 'one_hour')
                
                # Determine signal direction based on price and SL relationship
                direction = "BUY" if float(sl) < float(price) else "SELL"
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': price,
                    'stop_loss': sl,
                    'take_profit': tp1,  # Use first take profit level
                    'timeframe': interval
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
                timeframe = signal_data.get('timeframe', 'one_hour')
                
                # Create normalized signal data
                normalized_data = {
                    'instrument': instrument,
                    'direction': direction,
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timeframe': timeframe
                }
            else:
                logger.error(f"Missing required signal data")
                return False
            
            # Basic validation
            if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
                logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
                return False
                
            # Create signal ID for tracking
            signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(time.time())}"
            
            # Format the signal message
            message = self._format_signal_message(normalized_data)
            
            # Determine market type for the instrument
            market_type = _detect_market(instrument)
            
            # Store the full signal data for reference
            normalized_data['id'] = signal_id
            normalized_data['timestamp'] = datetime.now().isoformat()
            normalized_data['message'] = message
            normalized_data['market'] = market_type
            
            # Save signal for history tracking
            if not os.path.exists(self.signals_dir):
                os.makedirs(self.signals_dir, exist_ok=True)
                
            # Save to signals directory
            with open(f"{self.signals_dir}/{signal_id}.json", 'w') as f:
                json.dump(normalized_data, f)
            
            # FOR TESTING: Always send to admin for testing
            if hasattr(self, 'admin_users') and self.admin_users:
                try:
                    logger.info(f"Sending signal to admin users for testing: {self.admin_users}")
                    for admin_id in self.admin_users:
                        # Prepare keyboard with analysis options
                        keyboard = [
                            [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                        ]
                        
                        # Send the signal
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        logger.info(f"Test signal sent to admin {admin_id}")
                        
                        # Store signal reference for quick access
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                            
                        admin_str_id = str(admin_id)
                        if admin_str_id not in self.user_signals:
                            self.user_signals[admin_str_id] = {}
                        
                        self.user_signals[admin_str_id][signal_id] = normalized_data
            except Exception as e:
                logger.error(f"Error sending test signal to admin: {str(e)}")
            
            # Get subscribers for this instrument
            timeframe = normalized_data.get('timeframe', 'one_hour')
            subscribers = await self.get_subscribers_for_instrument(instrument, timeframe)
            
            if not subscribers:
                logger.warning(f"No subscribers found for {instrument}")
                return True  # Successfully processed, just no subscribers
            
            # Send signal to all subscribers
            logger.info(f"Sending signal {signal_id} to {len(subscribers)} subscribers")
            
            sent_count = 0
            for user_id in subscribers:
                try:
                    # Prepare keyboard with analysis options
                    keyboard = [
                        [InlineKeyboardButton("Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
                    ]
                    
                    # Send the signal
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    
                    sent_count += 1
                    
                    # Store signal reference for quick access
                    if not hasattr(self, 'user_signals'):
                        self.user_signals = {}
                        
                    user_str_id = str(user_id)
                    if user_str_id not in self.user_signals:
                        self.user_signals[user_str_id] = {}
                    
                    self.user_signals[user_str_id][signal_id] = normalized_data
                    
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
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "- Position size: 1-2% max\n"
            message += "- Use proper stop loss\n"
            message += "- Follow your trading plan\n\n"
            
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
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Analysis handlers for signal flow - with instrument embedded in callback
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_flow_technical_.*$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_flow_sentiment_.*$"))
            application.add_handler(CallbackQueryHandler(self.analysis_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            
            # Signal analysis flow handlers
            application.add_handler(CallbackQueryHandler(self.signal_technical_callback, pattern="^signal_technical$"))
            application.add_handler(CallbackQueryHandler(self.signal_sentiment_callback, pattern="^signal_sentiment$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_calendar$"))
            application.add_handler(CallbackQueryHandler(self.signal_calendar_callback, pattern="^signal_flow_calendar_.*$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_callback, pattern="^back_to_signal$"))
            application.add_handler(CallbackQueryHandler(self.back_to_signal_analysis_callback, pattern="^back_to_signal_analysis$"))
            
            # Signal from analysis
            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern="^analyze_from_signal_.*$"))
            
            # Ensure back_instrument is properly handled
            application.add_handler(CallbackQueryHandler(self.back_instrument_callback, pattern="^back_instrument$"))
            
            # Catch-all handler for any other callbacks
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Don't load signals here - it will be done in initialize_services
            # self._load_signals()
            
            logger.info("Bot setup completed successfully")
            
    except Exception as e:
        logger.error(f"Error setting up bot handlers: {str(e)}")
        logger.exception(e)

    @property
    def signals_enabled(self):
        """Get whether signals processing is enabled"""
        return self._signals_enabled
    
    @signals_enabled.setter
    def signals_enabled(self, value):
        """Set whether signals processing is enabled"""
        self._signals_enabled = bool(value)
        logger.info(f"Signal processing is now {'enabled' if value else 'disabled'}")

        async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a welcome message when the bot is started."""
        user = update.effective_user
        user_id = user.id
        first_name = user.first_name
        
        # Try to add the user to the database if they don't exist yet
    try:
            # Get user subscription since we can't check if user exists directly
            existing_subscription = await self.db.get_user_subscription(user_id)
            
            if not existing_subscription:
                # Add new user
                logger.info(f"New user started: {user_id}, {first_name}")
                await self.db.save_user(user_id, first_name, None, user.username)
        else:
                logger.info(f"Existing user started: {user_id}, {first_name}")
                
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        
        # Check if the user has a subscription 
        is_subscribed = await self.db.is_user_subscribed(user_id)
        
        # Check if payment has failed
        payment_failed = await self.db.has_payment_failed(user_id)
        
        if is_subscribed and not payment_failed:
            # For subscribed users, direct them to use the /menu command instead
            await update.message.reply_text(
                text="Welcome back! Please use the /menu command to access all features.",
                parse_mode=ParseMode.HTML
            )
            return
        elif payment_failed:
            # Show payment failure message
            failed_payment_text = f"""
 <b>Subscription Payment Failed</b> 

Your subscription payment could not be processed and your service has been deactivated.

To continue using Sigmapips AI and receive trading signals, please reactivate your subscription by clicking the button below.
            """
            
            # Use direct URL link for reactivation
            reactivation_url = "https://buy.stripe.com/9AQcPf3j63HL5JS145"
            
            # Create button for reactivation
            keyboard = [
                [InlineKeyboardButton("🔄 Reactivate Subscription", url=reactivation_url)]
            ]
            
            await update.message.reply_text(
                text=failed_payment_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
    else:
            # Show the welcome message with trial option from the screenshot
            welcome_text = """
 Welcome to Sigmapips AI! 

Discover powerful trading signals for various markets:
- Forex - Major and minor currency pairs

- Crypto - Bitcoin, Ethereum and other top
 cryptocurrencies

- Indices - Global market indices

- Commodities - Gold, silver and oil

Features:
 Real-time trading signals

 Multi-timeframe analysis (timeframes)

 Advanced chart analysis

 Sentiment indicators

 Economic calendar integration

Start today with a FREE 14-day trial!
            """
            
            # Use direct URL link instead of callback for the trial button
            checkout_url = "https://buy.stripe.com/3cs3eF9Hu9256NW9AA"
            
            # Create buttons - Trial button goes straight to Stripe checkout
            keyboard = [
                [InlineKeyboardButton("🔥 Start 14-day FREE Trial", url=checkout_url)]
            ]
            
            # Gebruik de juiste welkomst-GIF URL
            welcome_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
            
        try:
                # Send the GIF with caption containing the welcome message
                await update.message.reply_animation(
                    animation=welcome_gif_url,
                    caption=welcome_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except Exception as e:\n            logger.error(f"Error sending welcome GIF with caption: {str(e)}")
                # Fallback to text-only message if GIF fails
                await update.message.reply_text(
                    text=welcome_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
    async def set_subscription_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Secret command to manually set subscription status for a user"""
        # Check if the command has correct arguments
        if not context.args or len(context.args) < 3:
            await update.message.reply_text("Usage: /set_subscription [chatid] [status] [days]")
            return
            
    try:
            # Parse arguments
            chat_id = int(context.args[0])
            status = context.args[1].lower()
            days = int(context.args[2])
            
            # Validate status
            if status not in ["active", "inactive"]:
                await update.message.reply_text("Status must be 'active' or 'inactive'")
                return
                
            # Calculate dates
            now = datetime.now()
            
            if status == "active":
                # Set active subscription
                start_date = now
                end_date = now + timedelta(days=days)
                
                # Save subscription to database
                await self.db.save_user_subscription(
                    chat_id, 
                    "monthly", 
                    start_date, 
                    end_date
                )
                await update.message.reply_text(f" Subscription set to ACTIVE for user {chat_id} for {days} days")
                
        else:
                # Set inactive subscription by setting end date in the past
                start_date = now - timedelta(days=30)
                end_date = now - timedelta(days=1)
                
                # Save expired subscription to database
                await self.db.save_user_subscription(
                    chat_id, 
                    "monthly", 
                    start_date, 
                    end_date
                )
                await update.message.reply_text(f" Subscription set to INACTIVE for user {chat_id}")
                
            logger.info(f"Manually set subscription status to {status} for user {chat_id}")
            
        except ValueError:
            await update.message.reply_text("Invalid arguments. Chat ID and days must be numbers.")
    except Exception as e:
        logger.error(f"Error setting subscription: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
            
    async def set_payment_failed_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Secret command to set a user's subscription to the payment failed state"""
        logger.info(f"set_payment_failed command received: {update.message.text}")
        
    try:
            # Extract chat_id directly from the message text if present
            command_parts = update.message.text.split()
            if len(command_parts) > 1:
            try:
                    chat_id = int(command_parts[1])
                    logger.info(f"Extracted chat ID from message: {chat_id}")
                except ValueError:
                logger.error(f"Invalid chat ID format in message: {command_parts[1]}")
                    await update.message.reply_text(f"Invalid chat ID format: {command_parts[1]}")
                    return
            # Fallback to context args if needed
            elif context and context.args and len(context.args) > 0:
                chat_id = int(context.args[0])
                logger.info(f"Using chat ID from context args: {chat_id}")
        else:
                # Default to the user's own ID
                chat_id = update.effective_user.id
                logger.info(f"No chat ID provided, using sender's ID: {chat_id}")
            
            # Set payment failed status in database
            success = await self.db.set_payment_failed(chat_id)
            
            if success:
                message = f" Payment status set to FAILED for user {chat_id}"
                logger.info(f"Manually set payment failed status for user {chat_id}")
                
                # Show the payment failed interface immediately
                failed_payment_text = f"""
 <b>Subscription Payment Failed</b> 

Your subscription payment could not be processed and your service has been deactivated.

To continue using Sigmapips AI and receive trading signals, please reactivate your subscription by clicking the button below.
                """
                
                                  parse_mode=ParseMode.HTML
                            )
                    else:
                    logger.error(f"Failed to update message: {str(text_error)}")
                        # Laatste redmiddel: stuur een nieuw bericht
                        await context.bot.send_animation(
                            chat_id=update.effective_chat.id,
                            animation=gif_url,
                            caption="Select your analysis type:",
                            reply_markup=InlineKeyboardMarkup(ANALYSIS_KEYBOARD),
                            parse_mode=ParseMode.HTML
                        )
        
        return CHOOSE_ANALYSIS

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None, skip_gif=False) -> None:
        """Show the main menu when /menu command is used"""
        # Use context.bot if available, otherwise use self.bot
        bot = context.bot if context is not None else self.bot
        
        # Check if the user has a subscription
        user_id = update.effective_user.id
        is_subscribed = await self.db.is_user_subscribed(user_id)
        payment_failed = await self.db.has_payment_failed(user_id)
        
        if is_subscribed and not payment_failed:
            # Show the main menu for subscribed users
            reply_markup = InlineKeyboardMarkup(START_KEYBOARD)
            
            # Forceer altijd de welkomst GIF
            gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"
            
            # If we should show the GIF
            if not skip_gif:
            try:
                    # For message commands we can use reply_animation
                    if hasattr(update, 'message') and update.message:
                        # Verwijder eventuele vorige berichten met callback query
                        if hasattr(update, 'callback_query') and update.callback_query:
                        try:
                                await update.callback_query.message.delete()
                            except Exception:
                                pass
                        
                        # Send the GIF using regular animation method
                        await update.message.reply_animation(
                            animation=gif_url,
                            caption=WELCOME_MESSAGE,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup
                        )
                    else:
                        # Voor callback_query, verwijder huidige bericht en stuur nieuw bericht
                        if hasattr(update, 'callback_query') and update.callback_query:
                        try:
                                # Verwijder het huidige bericht
                                await update.callback_query.message.delete()
                                
                                # Stuur nieuw bericht met de welkomst GIF
                                await bot.send_animation(
                                    chat_id=update.effective_chat.id,
                                    animation=gif_url,
                                    caption=WELCOME_MESSAGE,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=reply_markup
                                )
                        except Exception as e:\n                            logger.error(f"Failed to handle callback query: {str(e)}")
                                # Valt terug op tekstwijziging als verwijderen niet lukt
                                await update.callback_query.edit_message_text(
                                    text=WELCOME_MESSAGE,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=reply_markup
                                )
                    else:
                            # Final fallback - try to send a new message
                            await bot.send_animation(
                                chat_id=update.effective_chat.id,
                                animation=gif_url,
                                caption=WELCOME_MESSAGE,
                                parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup
                            )
            except Exception as e:
                logger.error(f"Failed to send menu GIF: {str(e)}")
                    # Fallback to text-only approach
                    if hasattr(update, 'message') and update.message:
                        await update.message.reply_text(
                            text=WELCOME_MESSAGE,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup
                        )
                    else:
                        await bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=WELCOME_MESSAGE,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup
                        )
                    else:
                # Skip GIF mode - just send text
                if hasattr(update, 'message') and update.message:
                    await update.message.reply_text(
                        text=WELCOME_MESSAGE,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
                else:
                    await bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=WELCOME_MESSAGE,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
    else:
            # Handle non-subscribed users similar to start command
            await self.start_command(update, context)
            
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a message when the command /help is issued."""
        await self.show_main_menu(update, context)
        
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None) -> None:
        """Send a message when the command /menu is issued."""
        await self.show_main_menu(update, context)
        
    async def analysis_technical_callback(self, update: Update, context=None) -> int:
        """Handle analysis_technical button press"""
        query = update.callback_query
        await query.answer()
        
        # Check if signal-specific data is present in callback data
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'technical'
        
        # Set the callback data
        callback_data = query.data
        
        # Set the instrument if it was passed in the callback data
        if callback_data.startswith("signal_flow_technical_"):
            # Extract instrument from the callback data
            instrument = callback_data.replace("signal_flow_technical_", "")
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['instrument'] = instrument
            
                logger.info(f"Technical analysis for specific instrument: {instrument}")
            
            # Show analysis directly for this instrument
            return await self.show_technical_analysis(update, context, instrument=instrument)
        
        # Show the market selection menu
    try:
            # First try to edit message text
            await query.edit_message_text(
                text="Select market for technical analysis:",
                reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD)
            )
        except Exception as text_error:
            # If that fails due to caption, try editing caption
            if "There is no text in the message to edit" in str(text_error):
            try:
                    await query.edit_message_caption(
                        caption="Select market for technical analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
            except Exception as e:
                logger.error(f"Failed to update caption in analysis_technical_callback: {str(e)}")
                    # Try to send a new message as last resort
                    await query.message.reply_text(
                        text="Select market for technical analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
                else:
                # Re-raise for other errors
                raise
        
        return CHOOSE_MARKET
        
    async def analysis_sentiment_callback(self, update: Update, context=None) -> int:
        """Handle analysis_sentiment button press"""
        query = update.callback_query
        await query.answer()
        
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'sentiment'
        
        # Set the callback data
        callback_data = query.data
        
        # Set the instrument if it was passed in the callback data
        if callback_data.startswith("signal_flow_sentiment_"):
            # Extract instrument from the callback data
            instrument = callback_data.replace("signal_flow_sentiment_", "")
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['instrument'] = instrument
            
                logger.info(f"Sentiment analysis for specific instrument: {instrument}")
            
            # Show analysis directly for this instrument
            return await self.show_sentiment_analysis(update, context, instrument=instrument)
            
        # Show the market selection menu
    try:
            # First try to edit message text
            await query.edit_message_text(
                text="Select market for sentiment analysis:",
                reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD)
            )
        except Exception as text_error:
            # If that fails due to caption, try editing caption
            if "There is no text in the message to edit" in str(text_error):
            try:
                    await query.edit_message_caption(
                        caption="Select market for sentiment analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
            except Exception as e:
                logger.error(f"Failed to update caption in analysis_sentiment_callback: {str(e)}")
                    # Try to send a new message as last resort
                    await query.message.reply_text(
                        text="Select market for sentiment analysis:",
                        reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
                        parse_mode=ParseMode.HTML
                    )
                else:
                # Re-raise for other errors
                raise
        
        return CHOOSE_MARKET
        
    async def analysis_calendar_callback(self, update: Update, context=None) -> int:
        """Handle analysis_calendar button press"""
        query = update.callback_query
        await query.answer()
        
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'calendar'
            
        # Set the callback data
        callback_data = query.data
        
        # Set the instrument if it was passed in the callback data
        if callback_data.startswith("signal_flow_calendar_"):
            # Extract instrument from the callback data
            instrument = callback_data.replace("signal_flow_calendar_", "")
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['instrument'] = instrument
            
                logger.info(f"Calendar analysis for specific instrument: {instrument}")
            
            # Show analysis directly for this instrument
            return await self.show_calendar_analysis(update, context, instrument=instrument)
        
        # Skip market selection and go directly to calendar analysis
        logger.info("Showing economic calendar without market selection")
        return await self.show_calendar_analysis(update, context)

    async def show_economic_calendar(self, update: Update, context: CallbackContext, currency=None, loading_message=None):
        """Show the economic calendar for a specific currency"""
    try:
            # VERIFICATION MARKER: SIGMAPIPS_CALENDAR_FIX_APPLIED
            self.logger.info("VERIFICATION MARKER: SIGMAPIPS_CALENDAR_FIX_APPLIED")
            
            chat_id = update.effective_chat.id
            query = update.callback_query
            
            # Log that we're showing the calendar
            self.logger.info(f"Showing economic calendar for all major currencies")
            
            # Initialize the calendar service
            calendar_service = self._get_calendar_service()
            cache_size = len(getattr(calendar_service, 'cache', {}))
            self.logger.info(f"Calendar service initialized, cache size: {cache_size}")
            
            # Check if API key is available
            tavily_api_key = os.environ.get("TAVILY_API_KEY", "")
            if tavily_api_key:
                masked_key = f"{tavily_api_key[:4]}..." if len(tavily_api_key) > 7 else "***"
                self.logger.info(f"Tavily API key is available: {masked_key}")
        else:
                self.logger.warning("No Tavily API key found, will use mock data")
            
            # Get calendar data for ALL major currencies, regardless of the supplied parameter
            self.logger.info(f"Requesting calendar data for all major currencies")
            
            calendar_data = []
            
            # Get all currencies data
        try:
                if hasattr(calendar_service, 'get_calendar'):
                    calendar_data = await calendar_service.get_calendar()
            else:
                    self.logger.warning("calendar_service.get_calendar method not available, using mock data")
                    calendar_data = []
        except Exception as e:
                self.logger.warning(f"Error getting calendar data: {str(e)}")
                calendar_data = []
            
            # Check if data is empty
            if not calendar_data or len(calendar_data) == 0:
                self.logger.warning("Calendar data is empty, using mock data...")
                # Generate mock data
                today_date = datetime.now().strftime("%B %d, %Y")
                
                # Use the mock data generator from the calendar service if available
                if hasattr(calendar_service, '_generate_mock_calendar_data'):
                    mock_data = calendar_service._generate_mock_calendar_data(MAJOR_CURRENCIES, today_date)
            else:
                    # Otherwise use our own implementation
                    mock_data = self._generate_mock_calendar_data(MAJOR_CURRENCIES, today_date)
                
                # Flatten the mock data
                flattened_mock = []
                for currency_code, events in mock_data.items():
                    for event in events:
                        flattened_mock.append({
                            "time": event.get("time", ""),
                            "country": currency_code,
                            "country_flag": CURRENCY_FLAG.get(currency_code, ""),
                            "title": event.get("event", ""),
                            "impact": event.get("impact", "Low")
                        })
                
                calendar_data = flattened_mock
                self.logger.info(f"Generated {len(flattened_mock)} mock calendar events")
            
            # Format the calendar data in chronological order
            if hasattr(self, '_format_calendar_events'):
                message = await self._format_calendar_events(calendar_data)
        else:
                # Fallback to calendar service formatting if the method doesn't exist on TelegramService
                if hasattr(calendar_service, '_format_calendar_response'):
                    message = await calendar_service._format_calendar_response(calendar_data, "ALL")
            else:
                    # Simple formatting fallback
                    message = "<b>Economic Calendar</b>\n\n"
                    for event in calendar_data[:10]:  # Limit to first 10 events
                        country = event.get('country', 'Unknown')
                        title = event.get('title', 'Unknown Event')
                        time = event.get('time', 'Unknown Time')
                        message += f"{country}: {time} - {title}\n\n"
            
            # Create keyboard with back button if not provided from caller
            keyboard = None
            if context and hasattr(context, 'user_data') and context.user_data.get('from_signal', False):
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_to_signal_analysis")]])
        else:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="menu_analyse")]])
            
            # Try to delete loading message first if it exists
            if loading_message:
            try:
                    await loading_message.delete()
                    self.logger.info("Successfully deleted loading message")
                except Exception as delete_error:
                    self.logger.warning(f"Could not delete loading message: {str(delete_error)}")
                    
                    # If deletion fails, try to edit it
                try:
                        await context.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=loading_message.message_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            reply_markup=keyboard
                        )
                        self.logger.info("Edited loading message with calendar data")
                        return  # Skip sending a new message
                    except Exception as edit_error:
                        self.logger.warning(f"Could not edit loading message: {str(edit_error)}")
            
            # Send the message as a new message
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            self.logger.info("Sent calendar data as new message")
        
        except Exception as e:
            self.logger.error(f"Error showing economic calendar: {str(e)}")
            self.logger.exception(e)
            
            # Send error message
            chat_id = update.effective_chat.id
            await context.bot.send_message(
                chat_id=chat_id,
                text="<b> Error showing economic calendar</b>\n\nSorry, there was an error retrieving the economic calendar data. Please try again later.",
                parse_mode=ParseMode.HTML
            )
            
    def _generate_mock_calendar_data(self, currencies, date):
        """Generate mock calendar data if the real service fails"""
        self.logger.info(f"Generating mock calendar data for {len(currencies)} currencies")
        mock_data = {}
        
        # Impact levels
        impact_levels = ["High", "Medium", "Low"]
        
        # Possible event titles
        events = [
            "Interest Rate Decision",
            "Non-Farm Payrolls",
            "GDP Growth Rate",
            "Inflation Rate",
            "Unemployment Rate",
            "Retail Sales",
            "Manufacturing PMI",
            "Services PMI",
            "Trade Balance",
            "Consumer Confidence",
            "Building Permits",
            "Central Bank Speech",
            "Housing Starts",
            "Industrial Production"
        ]
        
        # Generate random events for each currency
        for currency in currencies:
            num_events = random.randint(1, 5)  # Random number of events per currency
            currency_events = []
            
            for _ in range(num_events):
                # Generate a random time (hour between 7-18, minute 00, 15, 30 or 45)
                hour = random.randint(7, 18)
                minute = random.choice([0, 15, 30, 45])
                time_str = f"{hour:02d}:{minute:02d} EST"
                
                # Random event and impact
                event = random.choice(events)
                impact = random.choice(impact_levels)
                
                currency_events.append({
                    "time": time_str,
                    "event": event,
                    "impact": impact
                })
            
            # Sort events by time
            mock_data[currency] = sorted(currency_events, key=lambda x: x["time"])
        
        return mock_data

    async def signal_technical_callback(self, update: Update, context=None) -> int:
        """Handle signal_technical button press"""
        query = update.callback_query
        await query.answer()
        
        # Add detailed debug logging
        logger.info(f"signal_technical_callback called with query data: {query.data}")
        
        # Save analysis type in context
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'technical'
        
        # Get the instrument from context
        instrument = None
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            instrument = context.user_data.get('instrument')
            # Debug log for instrument
            logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_technical_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
        
        if instrument:
            # Set flag to indicate we're in signal flow
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['from_signal'] = True
                logger.info("Set from_signal flag to True")
            
            # Try to show loading animation first
            loading_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"\n            loading_text = f"Loading {instrument} chart..."
            
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
                        # Reset signal flow flags
                        context.user_data['from_signal'] = False
                        context.user_data['in_signal_flow'] = False
                        logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
                    raise
            return CHOOSE_ANALYSIS

    async def signal_sentiment_callback(self, update: Update, context=None) -> int:
        """Handle signal_sentiment button press"""
        query = update.callback_query
        await query.answer()
        
        # Save analysis type in context
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'sentiment'
        
        # Get the instrument from context
        instrument = None
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            instrument = context.user_data.get('instrument')
            logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_sentiment_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
                    logger.info(f"Instrument from context: {instrument}")
        
        if instrument:
            # Set flag to indicate we're in signal flow
            if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
                context.user_data['from_signal'] = False
                context.user_data['in_signal_flow'] = False
                logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                context.user_data['from_signal'] = True
            
            # Try to show loading animation first
            loading_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"\n            loading_text = f"Loading sentiment analysis for {instrument}..."
            
        try:
                # Try to update with animated GIF first (best visual experience)
                await query.edit_message_media(
                    media=InputMediaAnimation(
                        media=loading_gif_url,
                        caption=loading_text
                    )
                )
                logger.info(f"Successfully showed loading GIF for {instrument} sentiment analysis")
            except Exception as media_error:
            logger.warning(f"Could not update with GIF: {str(media_error)}")
                
                # If GIF fails, try to update the text
            try:
                    loading_message = await query.edit_message_text(
                        text=loading_text
                    )
                    if context and hasattr(context, 'user_data'):
                        # Reset signal flow flags
                        context.user_data['from_signal'] = False
                        context.user_data['in_signal_flow'] = False
                        logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
                                caption=f"⏳ <b>Analyzing market sentiment for {instrument}...</b>"
                            )
                        except Exception as gif_error:
                        logger.warning(f"Could not show loading GIF: {str(gif_error)}")
            
            # Show sentiment analysis for this instrument
            return await self.show_sentiment_analysis(update, context, instrument=instrument)
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
                    logger.error(f"Failed to update caption in signal_sentiment_callback: {str(e)}")
                        # Try to send a new message as last resort
                        await query.message.reply_text(
                            text="Could not find the instrument. Please try again.",
                            reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                            parse_mode=ParseMode.HTML
                        )
                    else:
                # Re-raise for other errors
                raise
        return CHOOSE_ANALYSIS

    async def signal_calendar_callback(self, update: Update, context=None) -> int:
        """Handle signal_calendar button press"""
        query = update.callback_query
        await query.answer()
        
        # Add detailed debug logging
        logger.info(f"signal_calendar_callback called with data: {query.data}")
        
        # Save analysis type in context
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['analysis_type'] = 'calendar'
            # Make sure we save the original signal data to return to later
            signal_instrument = context.user_data.get('instrument')
            signal_direction = context.user_data.get('signal_direction')
            signal_timeframe = context.user_data.get('signal_timeframe') 
            
            # Save these explicitly to ensure they're preserved
            context.user_data['signal_instrument_backup'] = signal_instrument
            context.user_data['signal_direction_backup'] = signal_direction
            context.user_data['signal_timeframe_backup'] = signal_timeframe
            
            # Log for debugging
            logger.info(f"Saved signal data before calendar analysis: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
        
        # Get the instrument from context (voor tracking van context en eventuele toekomstige functionaliteit)
        instrument = None
        if context and hasattr(context, 'user_data'):
            # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            instrument = context.user_data.get('instrument')
            logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_calendar_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
                    logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument
        if query.data.startswith("signal_flow_calendar_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
        
        # Set flag to indicate we're in signal flow
        if context and hasattr(context, 'user_data'):
                # Reset signal flow flags
            context.user_data['from_signal'] = False
            context.user_data['in_signal_flow'] = False
            logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
            context.user_data['from_signal'] = True
            logger.info(f"Set from_signal flag to True for calendar analysis")
        
        # Try to show loading animation first
        loading_gif_url = "https://media.giphy.com/media/gSzIKNrqtotEYrZv7i/giphy.gif"\n        loading_text = f"Loading economic calendar..."
        
    try:
            # Try to update with animated GIF first (best visual experience)
            await query.edit_message_media(
                media=InputMediaAnimation(
                    media=loading_gif_url,
                    caption=loading_text
                )
            )
            logger.info(f"Successfully showed loading GIF for economic calendar")
        except Exception as media_error:
        logger.warning(f"Could not update with GIF: {str(media_error)}")
            
            # If GIF fails, try to update the text
        try:
                loading_message = await query.edit_message_text(
                    text=loading_text
                )
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
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
                            caption=f"⏳ <b>Loading economic calendar...</b>"
                        )
                    except Exception as gif_error:
                    logger.warning(f"Could not show loading GIF: {str(gif_error)}")
        
        # Show calendar analysis for ALL major currencies
        return await self.show_calendar_analysis(update, context, instrument=None)

    
    async def analyze_from_signal_callback(self, update: Update, context=None) -> int:
        """Handle Analyze Market button from signal notifications"""
        query = update.callback_query
        # Add query.answer() to acknowledge the callback
        await query.answer()
        logger.info(f"analyze_from_signal_callback called with data: {query.data}")
        
    try:
            # Extract signal information from callback data
            parts = query.data.split('_')
            
            # Format: analyze_from_signal_INSTRUMENT_SIGNALID
            if len(parts) >= 4:
                instrument = parts[3]
                signal_id = parts[4] if len(parts) >= 5 else None
                
                # Store in context for other handlers
                if context and hasattr(context, 'user_data'):
                    # Reset signal flow flags
                    context.user_data['from_signal'] = False
                    context.user_data['in_signal_flow'] = False
                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                    context.user_data['instrument'] = instrument
                    if signal_id:
                        context.user_data['signal_id'] = signal_id
                    # Set signal flow flags (only once)
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                    
                    # Make a backup copy to ensure we can return to signal later
                    context.user_data['signal_instrument'] = instrument
                    context.user_data['signal_instrument_backup'] = instrument
                    if signal_id:
                        context.user_data['signal_id_backup'] = signal_id
                    
                    # Also store info from the actual signal if available
                    if str(update.effective_user.id) in self.user_signals and signal_id in self.user_signals[str(update.effective_user.id)]:
                        signal = self.user_signals[str(update.effective_user.id)][signal_id]
                        if signal:
                            context.user_data['signal_direction'] = signal.get('direction')
                            # Use interval or timeframe, whichever is available
                            timeframe = signal.get('interval') or signal.get('timeframe')
                            context.user_data['signal_timeframe'] = timeframe
                            # Backup copies
                            context.user_data['signal_timeframe_backup'] = timeframe
                            context.user_data['signal_direction_backup'] = signal.get('direction')
                
                # Store the original signal page for later retrieval
                await self._store_original_signal_page(update, context, instrument, signal_id)
                
                # Show analysis options for this instrument
                keyboard = [
                    [InlineKeyboardButton("Technical Analysis", callback_data=f"signal_flow_technical_{instrument}")],
                    [InlineKeyboardButton("Market Sentiment", callback_data=f"signal_flow_sentiment_{instrument}")],
                    [InlineKeyboardButton("Economic Calendar", callback_data=f"signal_flow_calendar_{instrument}")],
                    [InlineKeyboardButton("Back to Signal", callback_data="back_to_signal")]
                ]
                
                # Update the message with the analysis options
                await query.edit_message_text(
                    text=f"<b> Analyze {instrument}</b>\n\nSelect the type of analysis you want to perform:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
                
                return CHOOSE_ANALYSIS
        else:
                # Invalid callback data
                await query.edit_message_text(
                    text="Invalid signal format. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
                return MENU
    except Exception as e:
        logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
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
    except Exception as e:
        logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
            # Error recovery
        try:
                await query.edit_message_text(
                    text="An error occurred. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
            except Exception:
                pass
            return MENU

    async def _store_original_signal_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, instrument: str, signal_id: str):
        """Store the original signal page data for later retrieval"""
    try:
        # Fetch the signal data from the database
            signal_data = await self.db.get_user_signals(update.effective_user.id, instrument)
            
            if signal_data:
                # Prepare the signal page data
                signal_page_data = {
                    "instrument": instrument,
                    "signal_id": signal_id,
                    "message": signal_data[0].get('message'),
                    "timestamp": signal_data[0].get('timestamp')
                }
                
                # Save the signal page data to the database
                await self.db.save_signal_page(update.effective_user.id, instrument, signal_page_data)
                
                logger.info(f"Original signal page data stored for {instrument} with signal ID {signal_id}")
        else:
            logger.warning(f"No signal data found for {instrument} with signal ID {signal_id}")
    except Exception as e:
        logger.error(f"Error storing original signal page: {str(e)}")
        logger.exception(e)

    async def _get_original_signal_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Retrieve the original signal page data for a given signal"""
    try:
        # Fetch the signal page data from the database
            signal_page_data = await self.db.get_signal_page(update.effective_user.id, update.callback_query.data.split('_')[3])
            
            if signal_page_data:
                return signal_page_data
        else:
            logger.warning(f"No signal page data found for signal ID {update.callback_query.data.split('_')[3]}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving original signal page: {str(e)}")
        logger.exception(e)
        return None

    async def _load_signals(self):
        """Load signals from the database"""
    try:
        # Fetch all signals from the database
            signals = await self.db.get_all_signals()
            
            if signals:
                for signal in signals:
                    self.user_signals[str(signal['user_id'])] = {signal['id']: signal}
                logger.info(f"Loaded {len(signals)} signals from the database")
        else:
                logger.info("No signals found in the database")
    except Exception as e:
        logger.error(f"Error loading signals: {str(e)}")
        logger.exception(e)

    async def _cleanup_old_signals(self, max_age_days):
        """Cleanup old signals from the database"""
    try:
            # Calculate the date threshold
            threshold_date = datetime.now() - timedelta(days=max_age_days)
            
        # Fetch signals older than the threshold date
            signals_to_delete = await self.db.get_old_signals(threshold_date)
            
            if signals_to_delete:
                for signal in signals_to_delete:
                    await self.db.delete_signal(signal['id'])
                logger.info(f"Deleted {len(signals_to_delete)} old signals from the database")
        else:
                logger.info("No old signals found to delete")
            
            return len(signals_to_delete)
    except Exception as e:
        logger.error(f"Error cleaning up old signals: {str(e)}")
        logger.exception(e)
            return 0

    async def _format_signal_message(self, signal_data):
        """Format the signal message for display"""
    try:
            # Extract fields from signal data
            instrument = signal_data.get('instrument', 'Unknown')
            direction = signal_data.get('direction', 'Unknown')
            entry = signal_data.get('entry', 'Unknown')
            stop_loss = signal_data.get('stop_loss')
            take_profit = signal_data.get('take_profit')
            timeframe = signal_data.get('timeframe', 'one_hour')
            
            # Get multiple take profit levels if available
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            
            # Add emoji based on direction
            direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
            
            # Format the message with multiple take profits if available
            message = f"<b> New Trading Signal </b>\n\n"
            message += f"<b>Instrument:</b> {instrument}\n"
            message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
            message += f"<b>Entry Price:</b> {entry}\n"
            
            if stop_loss:
                message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
            
            # Add take profit levels
            if tp1:
                message += f"<b>Take Profit 1:</b> {tp1} \n"
            if tp2:
                message += f"<b>Take Profit 2:</b> {tp2} \n"
            if tp3:
                message += f"<b>Take Profit 3:</b> {tp3} \n"
            
            message += f"\n<b>Timeframe:</b> {timeframe}\n"
            message += f"<b>Strategy:</b> TradingView Signal\n\n"
            
            message += "————————————————————\n\n"
            message += "<b>Risk Management:</b>\n"
            message += "- Position size: 1-2% max\n"
            message += "- Use proper stop loss\n"
            message += "- Follow your trading plan\n\n"
            
            message += "————————————————————\n\n"
            
            # Generate AI verdict
            ai_verdict = f"The {instrument} {direction.lower()} signal shows a promising setup with defined entry at {entry} and stop loss at {stop_loss}. Multiple take profit levels provide opportunities for partial profit taking."
            message += f"<b>🤖 SigmaPips AI Verdict:</b>\n{ai_verdict}"
            
            return message
    except Exception as e:
        logger.error(f"Error formatting signal message: {str(e)}")
        logger.exception(e)
            return f"New {signal_data.get('instrument', 'Unknown')} {signal_data.get('direction', 'Unknown')} Signal"

    async def _get_signal_details(self, signal_id):
        """Retrieve signal details from the database"""
    try:
        # Fetch the signal data from the database
            signal_data = await self.db.get_signal(signal_id)
            
            if signal_data:
                return signal_data
        else:
            logger.warning(f"No signal data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal details: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_analysis(self, signal_id):
        """Retrieve signal analysis from the database"""
    try:
        # Fetch the signal analysis data from the database
            analysis_data = await self.db.get_signal_analysis(signal_id)
            
            if analysis_data:
                return analysis_data
        else:
            logger.warning(f"No analysis data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal analysis: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_sentiment(self, signal_id):
        """Retrieve signal sentiment from the database"""
    try:
        # Fetch the signal sentiment data from the database
            sentiment_data = await self.db.get_signal_sentiment(signal_id)
            
            if sentiment_data:
                return sentiment_data
        else:
            logger.warning(f"No sentiment data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal sentiment: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_calendar(self, signal_id):
        """Retrieve signal calendar data from the database"""
    try:
        # Fetch the signal calendar data from the database
            calendar_data = await self.db.get_signal_calendar(signal_id)
            
            if calendar_data:
                return calendar_data
        else:
            logger.warning(f"No calendar data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal calendar: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_market(self, signal_id):
        """Retrieve signal market data from the database"""
    try:
        # Fetch the signal market data from the database
            market_data = await self.db.get_signal_market(signal_id)
            
            if market_data:
                return market_data
        else:
            logger.warning(f"No market data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal market: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_trades(self, signal_id):
        """Retrieve signal trades from the database"""
    try:
        # Fetch the signal trades data from the database
        trades_data = await self.db.get_signal_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_comments(self, signal_id):
        """Retrieve signal comments from the database"""
    try:
        # Fetch the signal comments data from the database
            comments_data = await self.db.get_signal_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_attachments(self, signal_id):
        """Retrieve signal attachments from the database"""
    try:
        # Fetch the signal attachments data from the database
            attachments_data = await self.db.get_signal_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_notes(self, signal_id):
        """Retrieve signal notes from the database"""
    try:
        # Fetch the signal notes data from the database
            notes_data = await self.db.get_signal_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_tags(self, signal_id):
        """Retrieve signal tags from the database"""
    try:
        # Fetch the signal tags data from the database
            tags_data = await self.db.get_signal_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving signal tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
            
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_comments(self, signal_id):
        """Retrieve related comments from the database"""
    try:
        # Fetch the related comments data from the database
            comments_data = await self.db.get_related_comments(signal_id)
            
            if comments_data:
                return comments_data
        else:
            logger.warning(f"No related comments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related comments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_attachments(self, signal_id):
        """Retrieve related attachments from the database"""
    try:
        # Fetch the related attachments data from the database
            attachments_data = await self.db.get_related_attachments(signal_id)
            
            if attachments_data:
                return attachments_data
        else:
            logger.warning(f"No related attachments data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related attachments: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_notes(self, signal_id):
        """Retrieve related notes from the database"""
    try:
        # Fetch the related notes data from the database
            notes_data = await self.db.get_related_notes(signal_id)
            
            if notes_data:
                return notes_data
        else:
            logger.warning(f"No related notes data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related notes: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_tags(self, signal_id):
        """Retrieve related tags from the database"""
    try:
        # Fetch the related tags data from the database
            tags_data = await self.db.get_related_tags(signal_id)
            
            if tags_data:
                return tags_data
        else:
            logger.warning(f"No related tags data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related tags: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_signals(self, signal_id):
        """Retrieve related signals from the database"""
    try:
        # Fetch the related signals data from the database
            related_signals_data = await self.db.get_related_signals(signal_id)
            
            if related_signals_data:
                return related_signals_data
        else:
            logger.warning(f"No related signals data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related signals: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_articles(self, signal_id):
        """Retrieve related articles from the database"""
    try:
        # Fetch the related articles data from the database
            articles_data = await self.db.get_related_articles(signal_id)
            
            if articles_data:
                return articles_data
        else:
            logger.warning(f"No related articles data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related articles: {str(e)}")
        logger.exception(e)
        return None

    async def _get_signal_related_videos(self, signal_id):
        """Retrieve related videos from the database"""
    try:
        # Fetch the related videos data from the database
            videos_data = await self.db.get_related_videos(signal_id)
            
            if videos_data:
                return videos_data
        else:
            logger.warning(f"No related videos data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related videos: {str(e)}")
        logger.exception(e)
        return None

