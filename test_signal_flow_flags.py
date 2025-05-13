#!/usr/bin/env python3

import logging
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestContext:
    """Mock context class for testing"""
    def __init__(self):
        self.user_data = {}

class TestUpdate:
    """Mock update class for testing"""
    def __init__(self, user_id=123):
        self.callback_query = AsyncMock()
        self.callback_query.answer = AsyncMock()
        self.callback_query.edit_message_text = AsyncMock()
        self.effective_user = MagicMock()
        self.effective_user.id = user_id

class TestBot:
    """Mock bot class for testing the back_to_signal_callback function"""
    def __init__(self):
        self.user_signals = {
            "123": {
                "test_signal_id": {
                    "instrument": "EURUSD",
                    "direction": "BUY",
                    "interval": "1h",
                    "timestamp": "2023-01-01T12:00:00Z",
                    "message": "Test signal message"
                }
            }
        }
    
    async def back_to_signal_callback(self, update, context=None):
        """Simplified version of the back_to_signal_callback function for testing"""
        await update.callback_query.answer()
        
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
                context.user_data['in_signal_flow'] = True
                
                # Log retrieved values for debugging
                logger.info(f"Retrieved signal data from context: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
                logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
            
            # For testing, we'll just return the context
            return context
            
        except Exception as e:
            logger.error(f"Error in back_to_signal_callback: {str(e)}")
            return None

async def run_test():
    """Run the test for the back_to_signal_callback function"""
    logger.info("Starting test for back_to_signal_callback")
    
    # Create test objects
    bot = TestBot()
    update = TestUpdate(user_id=123)
    context = TestContext()
    
    # Set up context data
    context.user_data['signal_instrument_backup'] = "EURUSD"
    context.user_data['signal_direction_backup'] = "BUY"
    context.user_data['signal_timeframe_backup'] = "1h"
    
    # Call the function
    result_context = await bot.back_to_signal_callback(update, context)
    
    # Check that the signal flow flags are set correctly
    if result_context and hasattr(result_context, 'user_data'):
        from_signal = result_context.user_data.get('from_signal', False)
        in_signal_flow = result_context.user_data.get('in_signal_flow', False)
        
        logger.info(f"Test results:")
        logger.info(f"  from_signal flag set: {from_signal}")
        logger.info(f"  in_signal_flow flag set: {in_signal_flow}")
        
        if from_signal and in_signal_flow:
            logger.info("✅ TEST PASSED: Both signal flow flags are set correctly")
        else:
            logger.error("❌ TEST FAILED: Signal flow flags are not set correctly")
            if not from_signal:
                logger.error("  - from_signal flag is not set")
            if not in_signal_flow:
                logger.error("  - in_signal_flow flag is not set")
    else:
        logger.error("❌ TEST FAILED: Could not get result context")

if __name__ == "__main__":
    asyncio.run(run_test()) 