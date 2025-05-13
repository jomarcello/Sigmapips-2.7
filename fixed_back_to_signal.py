"""
Fixed version of the back_to_signal_callback function.

The key fix is adding the in_signal_flow flag on line 22:
context.user_data['in_signal_flow'] = True
"""

import logging
import traceback
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# Initialize logger
logger = logging.getLogger(__name__)

# Import the state constants
from trading_bot.services.telegram_service.states import SIGNAL_DETAILS, MENU

# Define keyboard layouts directly
SIGNAL_ANALYSIS_KEYBOARD = [
    [InlineKeyboardButton("📈 Technical Analysis", callback_data="signal_technical")],
    [InlineKeyboardButton("🧠 Market Sentiment", callback_data="signal_sentiment")],
    [InlineKeyboardButton("📅 Economic Calendar", callback_data="signal_calendar")],
    [InlineKeyboardButton("⬅️ Back", callback_data="back_to_signal")]
]

START_KEYBOARD = [
    [InlineKeyboardButton("🔍 Analyze Market", callback_data="menu_analyse")],
    [InlineKeyboardButton("📊 Trading Signals", callback_data="menu_signals")]
]

async def back_to_signal_callback(self, update: Update, context=None) -> int:
    """Handle back_to_signal button press"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get the current signal being viewed
        user_id = update.effective_user.id
        
        # First try to get signal data from backup in context
        signal_instrument = None
        signal_direction = None
        signal_timeframe = None
        
        if context and hasattr(context, 'user_data'):
            # Try to get from backup fields first (these are more reliable after navigation)
            signal_instrument = context.user_data.get('signal_instrument_backup') or context.user_data.get('signal_instrument')
            signal_direction = context.user_data.get('signal_direction_backup') or context.user_data.get('signal_direction')
            signal_timeframe = context.user_data.get('signal_timeframe_backup') or context.user_data.get('signal_timeframe')
            
            # Set both signal flow flags to ensure proper context is maintained
            context.user_data['from_signal'] = True
            context.user_data['in_signal_flow'] = True  # THIS IS THE KEY FIX
            
            # Log retrieved values for debugging
            logger.info(f"Retrieved signal data from context: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
            logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
            
            # Generate signal details message
            signal_message = f"📊 <b>Signal Details</b>\n\n"
            signal_message += f"🔸 <b>Instrument:</b> {signal_instrument}\n"
            signal_message += f"🔸 <b>Direction:</b> {signal_direction.upper()}\n"
            signal_message += f"🔸 <b>Timeframe:</b> {signal_timeframe}\n"
            
            # Show signal message with analysis options
            await query.edit_message_text(
                text=signal_message,
                reply_markup=InlineKeyboardMarkup(SIGNAL_ANALYSIS_KEYBOARD),
                parse_mode=ParseMode.HTML
            )
            
            return SIGNAL_DETAILS
    except Exception as e:
        logger.error(f"Error in back_to_signal_callback: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback to menu in case of error
        try:
            await query.edit_message_text(
                text="Sorry, there was an error retrieving signal details. Please try again.",
                reply_markup=InlineKeyboardMarkup(START_KEYBOARD),
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass
        
        return MENU 