#!/usr/bin/env python3
"""
Fix for the "analyze market" button in the Telegram bot.
This script applies the necessary changes to make the analyze market button work correctly.
"""

import logging
import sys
import re
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_analyze_market_button():
    """
    Fix the analyze market button functionality in the main.py file
    by updating the analyze_from_signal_callback method and button_callback method
    """
    try:
        # Path to the main.py file
        main_file_path = Path("trading_bot/main.py")
        
        if not main_file_path.exists():
            logger.error(f"File not found: {main_file_path}")
            return False
        
        # Read the content of the file
        with open(main_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Create a backup of the original file
        backup_path = main_file_path.with_suffix(".py.analyze_market_backup")
        with open(backup_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info(f"Created backup of the original file: {backup_path}")
        
        # Step 1: Update the analyze_from_signal_callback method
        # Define the pattern to match the analyze_from_signal_callback function
        analyze_pattern = r'async def analyze_from_signal_callback\(self, update: Update, context=None\) -> int:.*?return MENU'
        
        # Find the analyze_from_signal_callback function
        analyze_matches = list(re.finditer(analyze_pattern, content, re.DOTALL))
        
        if not analyze_matches:
            logger.error("Could not find the analyze_from_signal_callback function in the file")
            return False
        
        logger.info(f"Found analyze_from_signal_callback function at position {analyze_matches[0].start()}")
        
        # The updated implementation of the analyze_from_signal_callback function
        updated_analyze_callback = '''async def analyze_from_signal_callback(self, update: Update, context=None) -> int:
        """Handle Analyze Market button from signal notifications"""
        query = update.callback_query
        await query.answer()
        logger.info(f"analyze_from_signal_callback called with data: {query.data}")
        
        try:
            # Extract signal information from callback data
            parts = query.data.split('_')
            logger.info(f"Analyze callback parts: {parts}")
            
            # Format: analyze_from_signal_INSTRUMENT_SIGNALID
            if len(parts) >= 4:
                instrument = parts[3]
                signal_id = parts[4] if len(parts) >= 5 else None
                
                logger.info(f"Extracted instrument: {instrument}, signal_id: {signal_id}")
                
                # Store in context for other handlers
                if context and hasattr(context, 'user_data'):
                    context.user_data['instrument'] = instrument
                    if signal_id:
                        context.user_data['signal_id'] = signal_id
                    
                    # Mark that we're coming from signal flow
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info("Set signal flow flags: from_signal=True, in_signal_flow=True")
                    
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
                            context.user_data['signal_direction_backup'] = signal.get('direction')
                            context.user_data['signal_timeframe_backup'] = timeframe
                            logger.info(f"Stored signal details: direction={signal.get('direction')}, timeframe={timeframe}")
            else:
                # Legacy support - just extract the instrument
                instrument = parts[3] if len(parts) >= 4 else None
                
                if instrument and context and hasattr(context, 'user_data'):
                    context.user_data['instrument'] = instrument
                    context.user_data['signal_instrument_backup'] = instrument
            
            # Store the original signal page for later retrieval
            logger.info(f"Storing original signal page for: {instrument}, {signal_id}")
            try:
                await self._store_original_signal_page(update, context, instrument, signal_id)
                logger.info(f"Successfully stored original signal page")
            except Exception as store_err:
                logger.error(f"Error storing original signal page: {str(store_err)}")
            
            # Show analysis options for this instrument with specific signal flow callbacks
            keyboard = [
                [InlineKeyboardButton("📈 Technical Analysis", callback_data=f"signal_technical_{instrument}")],
                [InlineKeyboardButton("🧠 Market Sentiment", callback_data=f"signal_sentiment_{instrument}")],
                [InlineKeyboardButton("📅 Economic Calendar", callback_data=f"signal_calendar_{instrument}")],
                [InlineKeyboardButton("⬅️ Back to Signal", callback_data="back_to_signal")]
            ]
            
            # Try to edit the message text
            try:
                await query.edit_message_text(
                    text=f"<b>🔍 Analyze {instrument}</b>\\n\\nSelect the type of analysis you want to perform:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
                # Fall back to sending a new message
                await query.message.reply_text(
                    text=f"<b>🔍 Analyze {instrument}</b>\\n\\nSelect the type of analysis you want to perform:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            
            return CHOOSE_ANALYSIS
            
        except Exception as e:
            logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
            logger.exception(e)
            
            # Error recovery - show user a message and return to main menu
            try:
                await query.edit_message_text(
                    text="An error occurred. Please try again from the main menu.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
            except Exception:
                pass
            
            return MENU'''
        
        # Replace the analyze_from_signal_callback function with the updated implementation
        new_content = content[:analyze_matches[0].start()] + updated_analyze_callback + content[analyze_matches[0].end():]
        
        # Step 2: Update the button_callback method to handle signal_technical and signal_sentiment with instrument parameters
        # Find the button_callback function
        button_pattern = r'async def button_callback\(self, update: Update, context=None\) -> int:.*?# Handle analyze from signal button.*?await query\.answer\(\)'
        button_matches = list(re.finditer(button_pattern, new_content, re.DOTALL))
        
        if not button_matches:
            logger.error("Could not find the button_callback function in the file")
            return False
        
        logger.info(f"Found button_callback function at position {button_matches[0].start()}")
        
        # The updated implementation of the button_callback section
        updated_button_section = '''async def button_callback(self, update: Update, context=None) -> int:
        """Handle button callback queries"""
        try:
            query = update.callback_query
            callback_data = query.data
            
            # Log the callback data
            logger.info(f"Button callback opgeroepen met data: {callback_data}")
            
            # Answer the callback query to stop the loading indicator
            await query.answer()
            
            # Handle analyze from signal button
            if callback_data.startswith("analyze_from_signal_"):
                return await self.analyze_from_signal_callback(update, context)
            
            # Handle signal_technical with instrument parameter
            if callback_data.startswith("signal_technical_"):
                parts = callback_data.split('_')
                if len(parts) >= 3:
                    instrument = parts[2]
                    if context and hasattr(context, 'user_data'):
                        context.user_data['instrument'] = instrument
                    return await self.signal_technical_callback(update, context)
            
            # Handle signal_sentiment with instrument parameter
            if callback_data.startswith("signal_sentiment_"):
                parts = callback_data.split('_')
                if len(parts) >= 3:
                    instrument = parts[2]
                    if context and hasattr(context, 'user_data'):
                        context.user_data['instrument'] = instrument
                    return await self.signal_sentiment_callback(update, context)
            
            # Handle signal_calendar with instrument parameter
            if callback_data.startswith("signal_calendar_"):
                parts = callback_data.split('_')
                if len(parts) >= 3:
                    instrument = parts[2]
                    if context and hasattr(context, 'user_data'):
                        context.user_data['instrument'] = instrument
                    return await self.signal_calendar_callback(update, context)'''
        
        # Replace the button_callback section with the updated implementation
        match_end = button_matches[0].end()
        new_content = new_content[:button_matches[0].start()] + updated_button_section + new_content[match_end:]
        
        # Write the modified content back to the file
        with open(main_file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        
        logger.info(f"Successfully updated the analyze market button functionality in {main_file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing analyze market button: {str(e)}")
        logger.exception(e)
        return False

def main():
    """Apply the fix and report the result"""
    if fix_analyze_market_button():
        print("Successfully fixed the analyze market button functionality!")
        print("You can now test the functionality by running:")
        print("  python test_analyze_market.py")
        return 0
    else:
        print("Failed to fix the analyze market button functionality.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 