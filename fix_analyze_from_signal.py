#!/usr/bin/env python3
"""
Fix for the analyze_from_signal_callback function in the Telegram bot.
"""

import logging
import sys
import re
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_analyze_from_signal_callback():
    """Fix the analyze_from_signal_callback function in the main.py file"""
    try:
        # Path to the main.py file
        main_file_path = Path("trading_bot/main.py")
        
        if not main_file_path.exists():
            logger.error(f"File not found: {main_file_path}")
            return False
        
        # Read the content of the file
        with open(main_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Define the pattern to match the analyze_from_signal_callback function
        pattern = r'async def analyze_from_signal_callback\(self, update: Update, context=None\) -> int:.*?return MENU'
        
        # Find all occurrences of the function
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if not matches:
            logger.error("Could not find the analyze_from_signal_callback function in the file")
            return False
        
        logger.info(f"Found {len(matches)} occurrences of the analyze_from_signal_callback function")
        
        # The fixed implementation of the function
        fixed_implementation = '''async def analyze_from_signal_callback(self, update: Update, context=None) -> int:
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
                    [InlineKeyboardButton("📈 Technical Analysis", callback_data=f"signal_flow_technical_{instrument}")],
                    [InlineKeyboardButton("🧠 Market Sentiment", callback_data=f"signal_flow_sentiment_{instrument}")],
                    [InlineKeyboardButton("📅 Economic Calendar", callback_data=f"signal_flow_calendar_{instrument}")],
                    [InlineKeyboardButton("⬅️ Back to Signal", callback_data="back_to_signal")]
                ]
                
                # Update the message with the analysis options
                await query.edit_message_text(
                    text=f"<b>🔍 Analyze {instrument}</b>\n\nSelect the type of analysis you want to perform:",
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
            return MENU'''
        
        # Replace all occurrences of the function with the fixed implementation
        new_content = content
        for match in reversed(matches):
            new_content = new_content[:match.start()] + fixed_implementation + new_content[match.end():]
        
        # Create a backup of the original file
        backup_path = main_file_path.with_suffix(".py.bak")
        with open(backup_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info(f"Created backup of the original file: {backup_path}")
        
        # Write the modified content back to the file
        with open(main_file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        
        logger.info(f"Successfully updated the analyze_from_signal_callback function in {main_file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing analyze_from_signal_callback: {str(e)}")
        return False

def fix_back_to_signal_callback():
    """Fix the back_to_signal_callback function in the main.py file"""
    try:
        # Path to the main.py file
        main_file_path = Path("trading_bot/main.py")
        
        if not main_file_path.exists():
            logger.error(f"File not found: {main_file_path}")
            return False
        
        # Read the content of the file
        with open(main_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Define the pattern to match the back_to_signal_callback function
        pattern = r'async def back_to_signal_callback\(self, update: Update, context=None\) -> int:.*?return MENU'
        
        # Find all occurrences of the function
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if not matches:
            logger.error("Could not find the back_to_signal_callback function in the file")
            return False
        
        logger.info(f"Found {len(matches)} occurrences of the back_to_signal_callback function")
        
        # The fixed implementation of the function
        fixed_implementation = '''async def back_to_signal_callback(self, update: Update, context=None) -> int:
        """Handle back_to_signal button press"""
        query = update.callback_query
        await query.answer()
        
        try:
            # Get the current signal being viewed
            user_id = update.effective_user.id
            user_str_id = str(user_id)
            
            # Try to get the original signal page data
            original_signal = await self._get_original_signal_page(update, context)
            
            # If we have the original signal, use it directly
            if original_signal and isinstance(original_signal, dict):
                signal_instrument = original_signal.get('instrument')
                signal_id = original_signal.get('signal_id')
                signal_message = original_signal.get('message')
                
                # If we have the complete message, use it
                if signal_message and signal_instrument and signal_id:
                    # Set signal flow flags to ensure proper context is maintained
                    if context and hasattr(context, 'user_data'):
                        context.user_data['from_signal'] = True
                        context.user_data['in_signal_flow'] = True
                        logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                    
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
                    
                    return SIGNAL_DETAILS
            
            # Fallback to the old method if we don't have the original signal
            # First try to get signal data from backup in context
            signal_instrument = None
            signal_direction = None
            signal_timeframe = None
            
            if context and hasattr(context, 'user_data'):
                # Set signal flow flags to ensure proper context is maintained
                context.user_data['from_signal'] = True
                context.user_data['in_signal_flow'] = True
                logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                
                # Try to get from backup fields first (these are more reliable after navigation)
                signal_instrument = context.user_data.get('signal_instrument_backup') or context.user_data.get('signal_instrument')
                signal_direction = context.user_data.get('signal_direction_backup') or context.user_data.get('signal_direction')
                signal_timeframe = context.user_data.get('signal_timeframe_backup') or context.user_data.get('signal_timeframe')
                
                # Log retrieved values for debugging
                logger.info(f"Retrieved signal data from context: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
            
            # Find the most recent signal for this user based on context data
            signal_data = None
            signal_id = None
            
            # Find matching signal based on instrument and direction
            if signal_instrument and user_str_id in self.user_signals:
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
                        timeframe_match = (sig.get('interval') == signal_timeframe or sig.get('timeframe') == signal_timeframe)
                    
                    if instrument_match and direction_match and timeframe_match:
                        matching_signals.append((sig_id, sig))
                
                # Sort by timestamp, newest first
                if matching_signals:
                    matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                    signal_id, signal_data = matching_signals[0]
                    logger.info(f"Found matching signal with ID: {signal_id}")
                else:
                    logger.warning(f"No matching signals found for instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
                    # If no exact match, try with just the instrument
                    matching_signals = []
                    for sig_id, sig in user_signal_dict.items():
                        if sig.get('instrument') == signal_instrument:
                            matching_signals.append((sig_id, sig))
                    
                    if matching_signals:
                        matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                        signal_id, signal_data = matching_signals[0]
                        logger.info(f"Found signal with just instrument match, ID: {signal_id}")
            
            # If still no signal data, try to get from database
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
            
            if not signal_data:
                # Fallback message if signal not found
                await query.edit_message_text(
                    text="Signal not found. Please use the main menu to continue.",
                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                )
                return MENU
            
            # Show the signal details with analyze button
            # Prepare analyze button with signal info embedded
            keyboard = [
                [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{signal_instrument}_{signal_id}")]
            ]
            
            # Get the formatted message from the signal
            signal_message = signal_data.get('message', "Signal details not available.")
            
            # Edit current message to show signal
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
            
            return MENU'''
        
        # Replace all occurrences of the function with the fixed implementation
        new_content = content
        for match in reversed(matches):
            new_content = new_content[:match.start()] + fixed_implementation + new_content[match.end():]
        
        # Create a backup of the original file if not already created
        backup_path = main_file_path.with_suffix(".py.bak")
        if not backup_path.exists():
            with open(backup_path, "w", encoding="utf-8") as file:
                file.write(content)
            logger.info(f"Created backup of the original file: {backup_path}")
        
        # Write the modified content back to the file
        with open(main_file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        
        logger.info(f"Successfully updated the back_to_signal_callback function in {main_file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing back_to_signal_callback: {str(e)}")
        return False

def main():
    """Main entry point for the script"""
    logger.info("Starting to fix analyze_from_signal_callback and back_to_signal_callback functions")
    
    # Fix the analyze_from_signal_callback function
    analyze_success = fix_analyze_from_signal_callback()
    
    # Fix the back_to_signal_callback function
    back_success = fix_back_to_signal_callback()
    
    if analyze_success and back_success:
        logger.info("Successfully fixed both functions!")
        return 0
    elif analyze_success:
        logger.warning("Fixed analyze_from_signal_callback but failed to fix back_to_signal_callback")
        return 1
    elif back_success:
        logger.warning("Fixed back_to_signal_callback but failed to fix analyze_from_signal_callback")
        return 1
    else:
        logger.error("Failed to fix both functions")
        return 2

if __name__ == "__main__":
    sys.exit(main()) 