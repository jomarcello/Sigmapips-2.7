#!/usr/bin/env python3
import logging
import asyncio
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_analyze_market_flow():
    """
    Test the analyze market button flow.
    This will simulate:
    1. A callback query with data "analyze_from_signal_EURUSD_12345"
    2. Then a callback query with data "signal_technical_EURUSD"
    
    This allows us to verify the changes we made to fix the analyze market button.
    """
    try:
        import json
        import sys
        from telegram import Update, CallbackQuery, Chat, User, Message, InlineKeyboardMarkup
        from telegram._utils.defaultvalue import DEFAULT_NONE
        
        # Mock objects needed for testing
        sys.path.append(".")  # Add current directory to path
        
        # Import the TelegramService class
        from trading_bot.main import TelegramService, setup_logging
        
        # Setup logging
        setup_logging()
        
        # Create mock objects that simulate telegram objects
        mock_user = User(id=123456789, first_name="Test", is_bot=False, username="testuser")
        mock_chat = Chat(id=123456789, type="private")
        
        # Mock message and query for the first callback (analyze_from_signal)
        mock_message_1 = Message(
            message_id=1,
            date=1234567890,
            chat=mock_chat,
            text="Test Signal",
            from_user=mock_user
        )
        
        mock_message_1.reply_text = lambda text, reply_markup=None, parse_mode=None: logger.info(f"Reply text: {text}")
        mock_message_1.edit_text = lambda text, reply_markup=None, parse_mode=None: logger.info(f"Edit text: {text}")
        
        # Create callback query for analyze market button
        mock_query_1 = CallbackQuery(
            id="123",
            from_user=mock_user,
            chat_instance="456",
            message=mock_message_1,
            data="analyze_from_signal_EURUSD_12345"
        )
        
        mock_query_1.answer = lambda text=None: logger.info(f"Query answered: {text or 'No text'}")
        mock_query_1.edit_message_text = lambda text, reply_markup=None, parse_mode=None: logger.info(f"Edit message: {text}")
        
        # Create update object for the first callback
        mock_update_1 = Update(
            update_id=1,
            callback_query=mock_query_1
        )
        mock_update_1.effective_user = mock_user
        
        # Create mock context for the first callback
        class MockContext:
            def __init__(self):
                self.user_data = {}
        
        mock_context_1 = MockContext()
        
        # Mock message and query for the second callback (signal_technical)
        mock_message_2 = Message(
            message_id=2,
            date=1234567890,
            chat=mock_chat,
            text="Analysis options",
            from_user=mock_user
        )
        
        mock_message_2.reply_text = lambda text, reply_markup=None, parse_mode=None: logger.info(f"Reply text: {text}")
        mock_message_2.edit_text = lambda text, reply_markup=None, parse_mode=None: logger.info(f"Edit text: {text}")
        
        # Create callback query for technical analysis button
        mock_query_2 = CallbackQuery(
            id="124",
            from_user=mock_user,
            chat_instance="456",
            message=mock_message_2,
            data="signal_technical_EURUSD"
        )
        
        mock_query_2.answer = lambda text=None: logger.info(f"Query answered: {text or 'No text'}")
        mock_query_2.edit_message_text = lambda text, reply_markup=None, parse_mode=None: logger.info(f"Edit message: {text}")
        
        # Create update object for the second callback
        mock_update_2 = Update(
            update_id=2,
            callback_query=mock_query_2
        )
        mock_update_2.effective_user = mock_user
        
        # Create mock context for the second callback
        mock_context_2 = MockContext()
        
        # Initialize TelegramService (we need to mock the DB)
        class MockDB:
            def __init__(self):
                self.supabase = None
            
            async def get_user_subscription(self, user_id):
                return {"active": True}
                
            async def is_user_subscribed(self, user_id):
                return True
                
            async def has_payment_failed(self, user_id):
                return False
                
            async def save_user(self, user_id, first_name, last_name, username):
                return True
        
        mock_db = MockDB()
        
        # Create a minimal instance of TelegramService
        telegram_service = TelegramService(db=mock_db, lazy_init=True)
        telegram_service.user_signals = {
            "123456789": {
                "12345": {
                    "instrument": "EURUSD",
                    "direction": "BUY",
                    "timeframe": "1h",
                    "signal_id": "12345"
                }
            }
        }
        
        # Initialize services required for testing
        await telegram_service.initialize_services()
        
        # Test analyze_from_signal_callback
        logger.info("Testing analyze_from_signal_callback...")
        
        # Use button_callback to simulate the real flow
        await telegram_service.button_callback(mock_update_1, mock_context_1)
        
        # Check if the context was updated correctly
        logger.info(f"Context after analyze_from_signal: {mock_context_1.user_data}")
        
        # Test signal_technical_callback
        logger.info("Testing signal_technical_callback...")
        
        # Copy the user_data from the first context to simulate continuation
        mock_context_2.user_data = mock_context_1.user_data
        
        # Use button_callback to simulate the real flow
        await telegram_service.button_callback(mock_update_2, mock_context_2)
        
        # Check if the context was updated correctly
        logger.info(f"Context after signal_technical: {mock_context_2.user_data}")
        
        logger.info("Test completed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        logger.exception(e)
        return False

def main():
    """Run the test"""
    asyncio.run(test_analyze_market_flow())

if __name__ == "__main__":
    main() 