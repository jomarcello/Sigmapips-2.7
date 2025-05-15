#!/usr/bin/env python3
"""
Generate Test Signal - Creates and prints a test signal in JSON format

Usage:
    python generate_test_signal.py
"""

import json
import time
from datetime import datetime

# Generate a sample signal
def generate_sample_signal():
    timestamp = int(time.time())
    
    # Create signal data
    signal_data = {
        "instrument": "GBPUSD",
        "direction": "BUY",
        "entry": 1.2850,
        "stop_loss": 1.2800,
        "take_profit": [1.2900, 1.2950, 1.3000],
        "timeframe": "4h",
        "timestamp": datetime.now().isoformat(),
        "id": f"GBPUSD_BUY_4h_{timestamp}"
    }
    
    # Calculate additional fields for completeness
    risk_reward = round((signal_data["take_profit"][1] - signal_data["entry"]) / 
                        (signal_data["entry"] - signal_data["stop_loss"]), 2)
    
    # Add optional fields for more comprehensive testing
    signal_data.update({
        "market": "forex",
        "strategy": "Trend Reversal",
        "risk_reward": risk_reward,
        "risk_percentage": 1.5,
        "ai_verdict": "Strong bullish momentum detected on GBP/USD with positive risk/reward ratio."
    })
    
    return signal_data

if __name__ == "__main__":
    # Generate the sample signal
    test_signal = generate_sample_signal()
    
    # Print formatted JSON
    print(json.dumps(test_signal, indent=2))
    
    # Also print usage examples
    print("\n=== HOW TO USE THIS SIGNAL ===")
    print("\n1. Using the test_direct_signal.py script:")
    print(f"python test_direct_signal.py --instrument {test_signal['instrument']} --direction {test_signal['direction']} --entry {test_signal['entry']} --stop-loss {test_signal['stop_loss']} --take-profit {' '.join(str(tp) for tp in test_signal['take_profit'])} --timeframe {test_signal['timeframe']}\n")
    
    print("2. Using curl to send to webhook:")
    print(f"curl -X POST -H \"Content-Type: application/json\" -d '{json.dumps(test_signal)}' http://localhost:8005/webhook\n")
    
    # Save to file
    with open("test_signal.json", "w") as f:
        json.dump(test_signal, f, indent=2)
    print("\nSignal has been saved to test_signal.json") 