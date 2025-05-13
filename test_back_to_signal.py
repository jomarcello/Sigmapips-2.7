#!/usr/bin/env python
import redis
import json
import logging
import asyncio
import os
from trading_bot.services.database.db import Database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_back_to_signal():
    """Test the back_to_signal functionality"""
    try:
        # Set Redis URL environment variable
        os.environ["REDIS_URL"] = "redis://localhost:6379"
        
        # Disable mock data
        os.environ["USE_MOCK_DATA"] = "false"
        
        # Initialize database
        db = Database()
        
        # Test user ID
        user_id = 12345
        
        # Create a test signal
        test_signal = {
            "id": "TEST_BACK_SIGNAL_789",
            "instrument": "USDJPY",
            "direction": "SELL",
            "entry": "141.994",
            "stop_loss": "142.054",
            "take_profit": "141.64",
            "timeframe": "15",
            "interval": "15",
            "price": "141.994",
            "sl": "142.054",
            "timestamp": "2025-05-13T12:00:00.000000",
            "tp1": "141.64",
            "tp2": "141.286",
            "tp3": "140.932",
            "user_id": user_id
        }
        
        # Connect directly to Redis for verification
        r = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
        logger.info(f"Direct Redis connection test: {r.ping()}")
        
        # Store the signal directly in Redis
        key = f"signal:{user_id}:{test_signal['id']}"
        logger.info(f"Storing signal directly in Redis with key: {key}")
        r.setex(key, 30 * 24 * 60 * 60, json.dumps(test_signal))  # 30 days expiration
        
        # Verify directly in Redis
        if r.exists(key):
            logger.info(f"Signal found directly in Redis with key: {key}")
            logger.info(f"TTL: {r.ttl(key)} seconds")
            logger.info(f"Data: {r.get(key)}")
        else:
            logger.warning(f"Signal not found directly in Redis with key: {key}")
        
        # Try to retrieve the signal via the database
        logger.info(f"Retrieving signal via database: {test_signal['id']}")
        retrieved_signal = await db.get_signal(user_id, test_signal['id'])
        
        if retrieved_signal:
            logger.info("Signal retrieved successfully via database")
            logger.info(f"Retrieved data: {json.dumps(retrieved_signal, indent=2)}")
        else:
            logger.error("Failed to retrieve signal via database")
            
        # Test get_user_signals
        logger.info(f"Getting all signals for user {user_id}")
        user_signals = await db.get_user_signals(user_id)
        
        if user_signals:
            logger.info(f"Found {len(user_signals)} signals for user {user_id}")
            for signal in user_signals:
                logger.info(f"Signal ID: {signal.get('id')}")
        else:
            logger.warning(f"No signals found for user {user_id}")
            
        # Test get_active_signals
        logger.info("Getting all active signals")
        active_signals = await db.get_active_signals()
        
        if active_signals:
            logger.info(f"Found {len(active_signals)} active signals")
            for signal in active_signals:
                logger.info(f"Active signal ID: {signal.get('id')}")
        else:
            logger.warning("No active signals found")
        
        # Clean up
        logger.info("Cleaning up test data")
        r.delete(key)
        logger.info(f"Key {key} deleted: {not r.exists(key)}")
        
    except Exception as e:
        logger.error(f"Error in test_back_to_signal: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_back_to_signal()) 