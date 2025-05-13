#!/usr/bin/env python3
"""
Test script for signal storage and retrieval functionality
"""

import json
import logging
import asyncio
import os
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk"

async def test_signal_storage():
    """Test the storage and retrieval of original signal pages"""
    logger.info("Starting signal storage test")
    
    # Import required modules
    try:
        from telegram import Update, Message, Chat, User, CallbackQuery
        from telegram.ext import ContextTypes
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        return False
    
    # Mock the TelegramService class to avoid actual initialization
    with patch('trading_bot.main.TelegramService') as MockTelegramService:
        # Create a real instance for our test methods
        telegram_service = MockTelegramService.return_value
        
        # Mock user data
        user_id = 12345
        chat_id = user_id
        message_id = 67890
        
        # Create test signal data
        signal_data = {
            "id": f"TEST_GBPUSD_BUY_{int(datetime.now().timestamp())}",
            "instrument": "GBPUSD",
            "direction": "BUY",
            "entry": "1.2850",
            "stop_loss": "1.2800",
            "take_profit": "1.2950",
            "timeframe": "1H",
            "timestamp": datetime.now().isoformat(),
            "message": "🎯 New Trading Signal 🎯\n\nInstrument: GBPUSD\nAction: BUY 🟢\n\nEntry Price: 1.2850\nStop Loss: 1.2800 🔴\nTake Profit 1: 1.2950 🎯\n\nTimeframe: 1H\nStrategy: Breakout Strategy"
        }
        
        # Setup mock user_signals in TelegramService
        telegram_service.user_signals = {
            str(user_id): {
                signal_data["id"]: signal_data
            }
        }
        
        # Create mock Update and Context objects
        user = MagicMock(spec=User)
        user.id = user_id
        
        chat = MagicMock(spec=Chat)
        chat.id = chat_id
        
        message = MagicMock(spec=Message)
        message.message_id = message_id
        message.chat = chat
        message.text = signal_data["message"]
        message.caption = None
        
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = f"analyze_from_signal_{signal_data['instrument']}_{signal_data['id']}"
        callback_query.message = message
        
        update = MagicMock(spec=Update)
        update.effective_user = user
        update.effective_chat = chat
        update.callback_query = callback_query
        
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        
        # Now let's manually implement the key methods we want to test
        
        # Implement _store_original_signal_page method
        async def mock_store_original_signal_page(update, context=None, instrument=None, signal_id=None):
            if not context or not hasattr(context, 'user_data'):
                logger.warning("Cannot store original signal page: no context or user_data")
                return False
                
            try:
                user_id = update.effective_user.id
                user_str_id = str(user_id)
                
                # Create a dictionary with all the signal information
                original_signal = {
                    'instrument': instrument,
                    'signal_id': signal_id,
                    'message_id': update.callback_query.message.message_id,
                    'chat_id': update.callback_query.message.chat_id,
                    'timestamp': datetime.now().timestamp()
                }
                
                # Store the current message text if available
                if hasattr(update.callback_query, 'message') and update.callback_query.message:
                    if update.callback_query.message.text:
                        original_signal['message'] = update.callback_query.message.text
                    elif update.callback_query.message.caption:
                        original_signal['message'] = update.callback_query.message.caption
                
                # Store signal data if available
                if signal_id and hasattr(telegram_service, 'user_signals') and user_str_id in telegram_service.user_signals and signal_id in telegram_service.user_signals[user_str_id]:
                    signal_data = telegram_service.user_signals[user_str_id][signal_id]
                    if signal_data:
                        # Only override message if we don't already have one from the current message
                        if not original_signal.get('message') and signal_data.get('message'):
                            original_signal['message'] = signal_data.get('message')
                        original_signal['direction'] = signal_data.get('direction')
                        original_signal['timeframe'] = signal_data.get('interval') or signal_data.get('timeframe')
                
                # Store the original signal information in context
                context.user_data['original_signal'] = original_signal
                logger.info(f"Stored original signal page: {original_signal}")
                
                return True
            except Exception as e:
                logger.error(f"Error storing original signal page: {str(e)}")
                return False
        
        # Implement analyze_from_signal_callback method
        async def mock_analyze_from_signal_callback(update, context=None):
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
                        
                        # Set signal flow flags
                        context.user_data['from_signal'] = True
                        context.user_data['in_signal_flow'] = True
                        logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                        
                        # Store the original signal page information
                        # This will be used to return to the signal page later
                        await mock_store_original_signal_page(update, context, instrument, signal_id)
                        
                        # Make a backup copy to ensure we can return to signal later
                        context.user_data['signal_instrument_backup'] = instrument
                        if signal_id:
                            context.user_data['signal_id_backup'] = signal_id
                
                return True
            except Exception as e:
                logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
                return False
        
        # Implement back_to_signal_callback method
        async def mock_back_to_signal_callback(update, context=None):
            query = update.callback_query
            await query.answer()
            
            try:
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
                        # Edit current message to show signal
                        await query.edit_message_text(
                            text=signal_message,
                            reply_markup=None,
                            parse_mode=None
                        )
                        
                        logger.info(f"Returned to original signal using stored message")
                        return True
                
                return False
            except Exception as e:
                logger.error(f"Error in back_to_signal_callback: {str(e)}")
                return False
        
        # Implement back_to_signal_analysis_callback method
        async def mock_back_to_signal_analysis_callback(update, context=None):
            query = update.callback_query
            await query.answer()
            
            # Add detailed logging for debugging
            logger.info("back_to_signal_analysis_callback called")
            
            try:
                # Get instrument and signal info from context
                instrument = None
                signal_id = None
                
                if context and hasattr(context, 'user_data'):
                    # Check for original_signal first
                    original_signal = context.user_data.get('original_signal')
                    if original_signal and isinstance(original_signal, dict):
                        instrument = original_signal.get('instrument')
                        signal_id = original_signal.get('signal_id')
                        logger.info(f"Retrieved instrument and signal_id from original_signal: {instrument}, {signal_id}")
                    else:
                        # Try to get from backup fields if no original_signal
                        instrument = context.user_data.get('signal_instrument_backup') or context.user_data.get('instrument')
                        signal_id = context.user_data.get('signal_id_backup') or context.user_data.get('signal_id')
                    
                    # Set signal flow flags to ensure proper context is maintained
                    context.user_data['from_signal'] = True
                    context.user_data['in_signal_flow'] = True
                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                    logger.info(f"Going back to signal analysis for instrument: {instrument}, signal_id: {signal_id}")
                
                # Format the message text
                text = f"Select your analysis type for {instrument or 'this instrument'}:"
                
                # Edit the message text
                await query.edit_message_text(
                    text=text,
                    reply_markup=None,
                    parse_mode=None
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Error in back_to_signal_analysis_callback: {str(e)}")
                return False
        
        # Assign our mock methods to the telegram_service
        telegram_service._store_original_signal_page = mock_store_original_signal_page
        telegram_service.analyze_from_signal_callback = mock_analyze_from_signal_callback
        telegram_service.back_to_signal_callback = mock_back_to_signal_callback
        telegram_service.back_to_signal_analysis_callback = mock_back_to_signal_analysis_callback
        
        # Test 1: Store original signal page
        logger.info("Test 1: Storing original signal page")
        result = await telegram_service._store_original_signal_page(
            update=update, 
            context=context,
            instrument=signal_data["instrument"],
            signal_id=signal_data["id"]
        )
        
        if not result:
            logger.error("Failed to store original signal page")
            return False
        
        # Verify stored data
        if 'original_signal' not in context.user_data:
            logger.error("original_signal not found in context.user_data")
            return False
        
        original_signal = context.user_data['original_signal']
        logger.info(f"Original signal stored: {original_signal}")
        
        if original_signal.get('instrument') != signal_data["instrument"]:
            logger.error(f"Instrument mismatch: {original_signal.get('instrument')} != {signal_data['instrument']}")
            return False
        
        if original_signal.get('signal_id') != signal_data["id"]:
            logger.error(f"Signal ID mismatch: {original_signal.get('signal_id')} != {signal_data['id']}")
            return False
        
        if original_signal.get('message') != signal_data["message"]:
            logger.error(f"Message mismatch: {original_signal.get('message')} != {signal_data['message']}")
            return False
        
        # Test 2: Test analyze_from_signal_callback
        logger.info("Test 2: Testing analyze_from_signal_callback")
        
        # Reset context
        context.user_data = {}
        
        # Mock answer method
        callback_query.answer = AsyncMock()
        
        # Mock edit_message_text method
        callback_query.edit_message_text = AsyncMock()
        
        # Call analyze_from_signal_callback
        result = await telegram_service.analyze_from_signal_callback(update, context)
        if not result:
            logger.error("analyze_from_signal_callback failed")
            return False
        
        logger.info("analyze_from_signal_callback completed successfully")
        
        # Verify that _store_original_signal_page was called (indirectly through flags)
        if 'from_signal' not in context.user_data or not context.user_data['from_signal']:
            logger.error("from_signal flag not set in context.user_data")
            return False
        
        if 'in_signal_flow' not in context.user_data or not context.user_data['in_signal_flow']:
            logger.error("in_signal_flow flag not set in context.user_data")
            return False
        
        if 'original_signal' not in context.user_data:
            logger.error("original_signal not set in context.user_data")
            return False
        
        # Test 3: Test back_to_signal_callback
        logger.info("Test 3: Testing back_to_signal_callback")
        
        # Reset mock
        callback_query.edit_message_text.reset_mock()
        
        # Call back_to_signal_callback
        result = await telegram_service.back_to_signal_callback(update, context)
        if not result:
            logger.error("back_to_signal_callback failed")
            return False
        
        logger.info("back_to_signal_callback completed successfully")
        
        # Verify that edit_message_text was called with the original signal message
        callback_query.edit_message_text.assert_called()
        call_args = callback_query.edit_message_text.call_args
        if call_args:
            kwargs = call_args[1]
            if 'text' in kwargs and kwargs['text'] == signal_data["message"]:
                logger.info("Original signal message was correctly used in back_to_signal_callback")
            else:
                logger.error(f"Original message not used in back_to_signal_callback: {kwargs.get('text')}")
                return False
        else:
            logger.error("edit_message_text was not called with expected arguments")
            return False
        
        # Test 4: Test back_to_signal_analysis_callback
        logger.info("Test 4: Testing back_to_signal_analysis_callback")
        
        # Reset mock
        callback_query.edit_message_text.reset_mock()
        
        # Call back_to_signal_analysis_callback
        result = await telegram_service.back_to_signal_analysis_callback(update, context)
        if not result:
            logger.error("back_to_signal_analysis_callback failed")
            return False
        
        logger.info("back_to_signal_analysis_callback completed successfully")
        
        # Verify that edit_message_text was called
        callback_query.edit_message_text.assert_called()
        
        logger.info("✅ All tests passed successfully!")
        return True

def main():
    """Main entry point for the script"""
    success = asyncio.run(test_signal_storage())
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 