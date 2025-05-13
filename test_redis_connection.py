#!/usr/bin/env python
import redis
import json
import os
import argparse
import logging
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_redis_connection(redis_url=None):
    """Test connection to Redis and signal storage/retrieval"""
    if not redis_url:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    logger.info(f"Testing Redis connection to: {redis_url}")
    
    try:
        # Connect to Redis
        r = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection with ping
        response = r.ping()
        logger.info(f"Redis ping response: {response}")
        
        # Create a test signal
        test_signal = {
            "id": f"TEST_EURUSD_BUY_{int(time.time())}",
            "instrument": "EURUSD",
            "direction": "BUY",
            "entry": "1.0750",
            "stop_loss": "1.0730",
            "take_profit": "1.0780",
            "timeframe": "15",
            "timestamp": datetime.now().isoformat(),
            "user_id": 12345,
            "message": "Test signal message"
        }
        
        # Store signal in Redis
        key = f"signal:{test_signal['user_id']}:{test_signal['id']}"
        r.setex(key, 3600, json.dumps(test_signal))  # Expire in 1 hour
        logger.info(f"Stored test signal with key: {key}")
        
        # Retrieve the signal
        retrieved_json = r.get(key)
        if retrieved_json:
            retrieved_signal = json.loads(retrieved_json)
            logger.info(f"Successfully retrieved signal: {retrieved_signal['id']}")
            
            # Verify data integrity
            assert retrieved_signal["instrument"] == test_signal["instrument"]
            assert retrieved_signal["direction"] == test_signal["direction"]
            logger.info("Signal data integrity verified")
        else:
            logger.error("Failed to retrieve signal from Redis")
            return False
        
        # Test pattern matching for keys
        pattern = f"signal:{test_signal['user_id']}:*"
        keys = r.keys(pattern)
        logger.info(f"Found {len(keys)} keys matching pattern '{pattern}'")
        
        # Clean up test data
        r.delete(key)
        logger.info(f"Cleaned up test key: {key}")
        
        logger.info("✅ Redis connection and signal storage/retrieval test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Redis test failed: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Redis connection and signal storage")
    parser.add_argument("--redis-url", help="Redis URL (default: from REDIS_URL env var or redis://localhost:6379)")
    
    args = parser.parse_args()
    
    success = test_redis_connection(args.redis_url)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 