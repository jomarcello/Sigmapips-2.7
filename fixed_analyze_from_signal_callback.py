"""
Fixed version of the analyze_from_signal_callback method.

This version properly handles signal data extraction and has correct try-except blocks.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# Initialize logger
logger = logging.getLogger(__name__)

# Import the state constants
from trading_bot.services.telegram_service.states import CHOOSE_ANALYSIS, MENU

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

async def analyze_from_signal_callback(self, update: Update, context=None) -> int:
    """Handle Analyze Market button from signal notifications"""
    query = update.callback_query
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
                context.user_data['instrument'] = instrument
                if signal_id:
                    context.user_data['signal_id'] = signal_id
                
                # Make a backup copy to ensure we can return to signal later
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
        
        # Show analysis options for this instrument
        # Format message
        # Use the SIGNAL_ANALYSIS_KEYBOARD for consistency
        keyboard = SIGNAL_ANALYSIS_KEYBOARD
        
        # Try to edit the message text
        try:
            await query.edit_message_text(
                text=f"Select your analysis type:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
            # Fall back to sending a new message
            await query.message.reply_text(
                text=f"Select your analysis type:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        
        return CHOOSE_ANALYSIS
    
    except Exception as e:
        logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
        logger.exception(e)
        
        try:
            await query.edit_message_text(
                text="An error occurred. Please try again from the main menu.",
                reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
            )
        except Exception:
            pass
        
        return MENU 