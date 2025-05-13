#!/usr/bin/env python
import os
import asyncio
import logging
import json
import time
from datetime import datetime
import sys
from trading_bot.services.database.db import Database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_redis_fix():
    """Test the Redis connection fix and signal storage"""
    try:
        # Set up test environment variables with Railway-style placeholders
        os.environ["REDIS_URL"] = "redis://default:${REDIS_PASSWORD}@${RAILWAY_TCP_PROXY_DOMAIN}:${RAILWAY_TCP_PROXY_PORT}"
        os.environ["REDIS_PASSWORD"] = "test_password"
        os.environ["REDISHOST"] = "localhost"
        os.environ["REDISPORT"] = "6379"
        os.environ["REDISUSER"] = "default"
        
        logger.info("Initializing Database with test environment variables")
        db = Database()
        
        logger.info(f"Database using_redis flag: {db.using_redis}")
        logger.info(f"Final Redis URL: {db.redis_url}")
        
        if not db.using_redis:
            logger.error("Redis connection failed - signals won't be stored in Redis")
            return False
        
        # Create a test signal
        user_id = 12345
        test_signal = {
            "id": f"TEST_FIX_GBPUSD_BUY_{int(time.time())}",
            "instrument": "GBPUSD",
            "direction": "BUY",
            "entry": "1.2850",
            "stop_loss": "1.2800",
            "take_profit": "1.2950",
            "timeframe": "15",
            "timestamp": datetime.now().isoformat()
        }
        
        # Store the signal
        logger.info(f"Storing test signal: {test_signal['id']}")
        result = await db.store_signal(user_id, test_signal)
        logger.info(f"Signal storage result: {result}")
        
        # Verify the signal was stored
        stored_signal = await db.get_signal(user_id, test_signal['id'])
        if stored_signal:
            logger.info(f"Successfully retrieved signal: {test_signal['id']}")
            logger.info(f"Signal data: {json.dumps(stored_signal, indent=2)}")
            return True
        else:
            logger.error(f"Failed to retrieve signal: {test_signal['id']}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing Redis fix: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_redis_fix())
    sys.exit(0 if success else 1) 