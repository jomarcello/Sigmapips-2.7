#!/usr/bin/env python3
import redis
import json
import time
from datetime import datetime

def store_test_signal(instrument, direction, entry, stop_loss, take_profit, timeframe="15"):
    """Store a test signal directly in Redis"""
    
    # Connect to Redis
    r = redis.from_url("redis://localhost:6379", decode_responses=True)
    
    # Test connection
    if not r.ping():
        print("❌ Failed to connect to Redis")
        return False
    
    # Create signal ID
    signal_id = f"{instrument}_{direction}_{timeframe}_{int(time.time())}"
    
    # Create signal data
    signal_data = {
        "id": signal_id,
        "instrument": instrument,
        "direction": direction.upper(),
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "timeframe": timeframe,
        "timestamp": datetime.now().isoformat(),
        "tp1": take_profit,
        "tp2": str(round(float(take_profit) + 0.005, 3)) if direction.upper() == "BUY" else str(round(float(take_profit) - 0.005, 3)),
        "tp3": str(round(float(take_profit) + 0.01, 3)) if direction.upper() == "BUY" else str(round(float(take_profit) - 0.01, 3))
    }
    
    # Store in Redis
    key = f"signal:test:{signal_id}"
    r.setex(key, 3600, json.dumps(signal_data))  # Expire in 1 hour
    
    print(f"✅ Signal stored in Redis with key: {key}")
    
    # Verify storage
    stored_data = r.get(key)
    if stored_data:
        print(f"✅ Successfully verified signal storage")
        print(f"Signal data: {json.loads(stored_data)}")
    else:
        print("❌ Failed to verify signal storage")
        return False
    
    # List all signal keys
    all_keys = r.keys("signal:*")
    print(f"Total signal keys in Redis: {len(all_keys)}")
    for k in all_keys:
        print(f"  - {k}")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Store a test signal in Redis")
    parser.add_argument("--instrument", default="GBPUSD", help="Trading instrument")
    parser.add_argument("--direction", default="BUY", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--entry", default="1.2850", help="Entry price")
    parser.add_argument("--stop-loss", default="1.2800", help="Stop loss price")
    parser.add_argument("--take-profit", default="1.2950", help="Take profit price")
    parser.add_argument("--timeframe", default="15", help="Timeframe in minutes")
    
    args = parser.parse_args()
    
    store_test_signal(
        args.instrument,
        args.direction,
        args.entry,
        args.stop_loss,
        args.take_profit,
        args.timeframe
    ) 