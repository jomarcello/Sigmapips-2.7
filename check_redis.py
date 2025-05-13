#!/usr/bin/env python
import redis
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def check_redis():
    """Check Redis for stored signals"""
    try:
        # Connect to Redis
        r = redis.from_url("redis://localhost:6379", decode_responses=True)
        
        # Test connection
        if not r.ping():
            logger.error("Could not connect to Redis")
            return
        
        logger.info("Connected to Redis successfully")
        
        # Get all signal keys
        keys = r.keys("signal:*")
        logger.info(f"Found {len(keys)} signal keys in Redis")
        
        # Print each signal
        for key in keys:
            signal_json = r.get(key)
            if signal_json:
                try:
                    signal_data = json.loads(signal_json)
                    logger.info(f"Key: {key}")
                    logger.info(f"Data: {json.dumps(signal_data, indent=2)}")
                except json.JSONDecodeError:
                    logger.error(f"Could not decode JSON for key {key}: {signal_json}")
            else:
                logger.warning(f"No data found for key {key}")
        
        # Store a test signal
        test_signal = {
            "id": "TEST_SIGNAL_456",
            "instrument": "GBPUSD",
            "direction": "BUY",
            "entry": "1.2850",
            "stop_loss": "1.2800",
            "take_profit": "1.2950",
            "timestamp": "2025-05-13T12:00:00.000000",
            "user_id": 12345
        }
        
        test_key = "signal:12345:TEST_SIGNAL_456"
        r.setex(test_key, 3600, json.dumps(test_signal))
        logger.info(f"Stored test signal with key: {test_key}")
        
        # Verify storage
        stored_json = r.get(test_key)
        if stored_json:
            stored_data = json.loads(stored_json)
            logger.info(f"Retrieved test signal: {stored_data['id']}")
            logger.info("Test signal stored and retrieved successfully")
        else:
            logger.error("Failed to retrieve test signal")
    
    except Exception as e:
        logger.error(f"Error checking Redis: {str(e)}")

if __name__ == "__main__":
    check_redis() 