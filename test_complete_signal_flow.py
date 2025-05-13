#!/usr/bin/env python
import os
import asyncio
import logging
import json
import time
from datetime import datetime
import sys
from trading_bot.services.database.db import Database
from trading_bot.main import TelegramService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_complete_signal_flow():
    """Test the complete signal flow with Redis and TelegramService"""
    try:
        # Set environment variables
        os.environ["TELEGRAM_BOT_TOKEN"] = "7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk"
        
        # Set up Redis environment variables
        os.environ["REDIS_URL"] = "redis://default:${REDIS_PASSWORD}@${RAILWAY_TCP_PROXY_DOMAIN}:${RAILWAY_TCP_PROXY_PORT}"
        os.environ["REDIS_PASSWORD"] = "test_password"
        os.environ["REDISHOST"] = "localhost"
        os.environ["REDISPORT"] = "6379"
        os.environ["REDISUSER"] = "default"
        
        # Initialize Database
        logger.info("Initializing Database")
        db = Database()
        
        logger.info(f"Database using_redis flag: {db.using_redis}")
        logger.info(f"Final Redis URL: {db.redis_url}")
        
        # Initialize TelegramService with the database
        logger.info("Initializing TelegramService")
        telegram_service = TelegramService(db=db)
        
        # Create a test signal
        test_signal = {
            "instrument": "GBPUSD",
            "direction": "BUY",
            "entry": "1.2850",
            "stop_loss": "1.2800",
            "take_profit": "1.2950",
            "timeframe": "15",
            "interval": "15",
            "price": "1.2850",
            "sl": "1.2800",
            "timestamp": datetime.now().isoformat(),
            "tp1": "1.2950",
            "tp2": "1.3",
            "tp3": "1.305"
        }
        
        # Process the signal
        logger.info("Processing test signal")
        result = await telegram_service.process_signal(test_signal)
        
        if not result:
            logger.error("Failed to process signal")
            return False
            
        logger.info("Signal processed successfully")
        
        # The signal ID is generated in process_signal, so we need to extract it
        # from the normalized_data that's created
        signal_id = None
        if hasattr(telegram_service, 'user_signals'):
            for user_id, signals in telegram_service.user_signals.items():
                if signals:
                    signal_id = list(signals.keys())[0]
                    logger.info(f"Found signal ID: {signal_id}")
                    break
        
        if not signal_id:
            logger.warning("Could not find signal ID in TelegramService")
            
            # Try to find signals in Redis directly
            if db.using_redis:
                keys = db.redis.keys("signal:*")
                logger.info(f"Found {len(keys)} signal keys in Redis")
                
                for key in keys:
                    logger.info(f"Redis key: {key}")
                    signal_json = db.redis.get(key)
                    if signal_json:
                        try:
                            signal_data = json.loads(signal_json)
                            logger.info(f"Signal data: {json.dumps(signal_data, indent=2)}")
                        except json.JSONDecodeError:
                            logger.error(f"Could not decode JSON for key {key}")
        
        # Test storing a signal directly
        user_id = 12345  # Test user ID
        direct_signal = {
            "id": f"TEST_DIRECT_GBPUSD_BUY_{int(time.time())}",
            "instrument": "GBPUSD",
            "direction": "BUY",
            "entry": "1.2850",
            "stop_loss": "1.2800",
            "take_profit": "1.2950",
            "timeframe": "15",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Storing direct test signal: {direct_signal['id']}")
        direct_result = await db.store_signal(user_id, direct_signal)
        logger.info(f"Direct signal storage result: {direct_result}")
        
        # Verify the signal was stored
        stored_signal = await db.get_signal(user_id, direct_signal['id'])
        if stored_signal:
            logger.info(f"Successfully retrieved direct signal: {direct_signal['id']}")
            logger.info(f"Signal data: {json.dumps(stored_signal, indent=2)}")
            return True
        else:
            logger.error(f"Failed to retrieve direct signal: {direct_signal['id']}")
            return False
    
    except Exception as e:
        logger.error(f"Error in test_complete_signal_flow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_signal_flow())
    sys.exit(0 if success else 1) 