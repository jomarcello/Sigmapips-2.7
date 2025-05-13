#!/usr/bin/env python3
"""
Test script to verify the signal storage implementation in the Telegram bot.
This script simulates the flow of:
1. Receiving a signal
2. Clicking "Analyze Market"
3. Going back to the signal
"""

import os
import json
import logging
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock objects for testing
class MockMessage:
    def __init__(self, text=None, caption=None):
        self.message_id = 12345
        self.chat_id = 67890
        self.text = text
        self.caption = caption
        self.photo = None
        self.animation = None

class MockCallbackQuery:
    def __init__(self, data, text=None):
        self.data = data
        self.message = MockMessage(text=text)
        self.answer = AsyncMock()
        self.edit_message_text = AsyncMock()
        self.edit_message_caption = AsyncMock()
        self.message.reply_text = AsyncMock()
        self.message.delete = AsyncMock()

class MockUpdate:
    def __init__(self, callback_data, text=None):
        self.callback_query = MockCallbackQuery(callback_data, text)
        self.effective_user = MagicMock()
        self.effective_user.id = 123456789
        self.effective_chat = MagicMock()
        self.effective_chat.id = 67890

class MockContext:
    def __init__(self):
        self.user_data = {}
        self.bot = MagicMock()
        self.bot.send_message = AsyncMock()
        self.bot.send_animation = AsyncMock()

async def test_signal_storage():
    """Test the signal storage and retrieval functionality"""
    # Import the necessary functions from the main module
    try:
        # Try to import from the trading_bot module
        from trading_bot.main import TelegramService
        logger.info("Successfully imported TelegramService from trading_bot.main")
    except ImportError:
        logger.error("Could not import TelegramService from trading_bot.main")
        logger.info("Trying to import from test_back_to_signal.py instead")
        # If that fails, try to import from the test module
        try:
            from test_back_to_signal import TelegramService
            logger.info("Successfully imported TelegramService from test_back_to_signal")
        except ImportError:
            logger.error("Could not import TelegramService")
            return False
    
    # Create a mock TelegramService instance
    service = TelegramService(db=None)
    
    # Create mock signal data
    signal_data = {
        "id": "EURUSD_BUY_1h_1234567890",
        "instrument": "EURUSD",
        "direction": "BUY",
        "entry": 1.1000,
        "stop_loss": 1.0950,
        "take_profit": 1.1100,
        "timeframe": "1h",
        "interval": "1h",
        "message": "🟢 *EURUSD BUY SIGNAL* 🟢\n\n*Entry Price:* 1.10000\n*Stop Loss:* 1.09500\n\n*Take Profit Levels:*\nTP1: 1.11000\n\n*Timeframe:* 1h\n*Strategy:* Trend Following\n*Risk/Reward:* 2.0\n*Risk %:* 1.0%\n\n*AI Analysis:*\nStrong bullish momentum with support at 1.0950.\n\n⚠️ *Risk Management:* Always use proper position sizing and risk management."
    }
    
    # Create a mock user_signals dictionary
    service.user_signals = {
        "123456789": {
            "EURUSD_BUY_1h_1234567890": signal_data
        }
    }
    
    # 1. Simulate receiving a signal and clicking "Analyze Market"
    logger.info("Step 1: Simulating clicking 'Analyze Market' on a signal")
    update = MockUpdate("analyze_from_signal_EURUSD_EURUSD_BUY_1h_1234567890", 
                       text=signal_data["message"])
    context = MockContext()
    
    # Call the analyze_from_signal_callback function
    logger.info("Calling analyze_from_signal_callback")
    service._store_original_signal_page = AsyncMock()
    await service.analyze_from_signal_callback(update, context)
    
    # Verify that _store_original_signal_page was called
    service._store_original_signal_page.assert_called_once()
    logger.info("_store_original_signal_page was called successfully")
    
    # Manually call _store_original_signal_page since we mocked it above
    logger.info("Manually calling _store_original_signal_page")
    service._store_original_signal_page = service.__class__._store_original_signal_page
    await service._store_original_signal_page(service, update, context, "EURUSD", "EURUSD_BUY_1h_1234567890")
    
    # Verify that the original signal was stored in context
    assert 'original_signal' in context.user_data, "original_signal not found in context"
    logger.info(f"Original signal stored in context: {context.user_data['original_signal']}")
    
    # 2. Simulate going back to the signal
    logger.info("Step 2: Simulating clicking 'Back to Signal'")
    update = MockUpdate("back_to_signal", text="Select your analysis type:")
    
    # Mock the back_to_signal_callback function
    original_back_to_signal = service.back_to_signal_callback
    service.back_to_signal_callback = AsyncMock()
    
    # Call the back_to_signal_callback function
    await original_back_to_signal(service, update, context)
    
    # Verify that the edit_message_text was called with the original signal message
    update.callback_query.edit_message_text.assert_called_once()
    call_args = update.callback_query.edit_message_text.call_args[1]
    logger.info(f"edit_message_text called with text: {call_args.get('text')[:50]}...")
    
    # Check if the message contains the signal information
    assert "EURUSD BUY SIGNAL" in call_args.get('text', ""), "Signal message not found in edit_message_text call"
    logger.info("Successfully verified that back_to_signal_callback uses the original signal information")
    
    logger.info("All tests passed successfully!")
    return True

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_signal_storage()) 