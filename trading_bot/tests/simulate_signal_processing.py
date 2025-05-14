"""
Simulate signal processing locally

This script simulates the signal processing flow locally without needing
to send HTTP requests to the webhook endpoint. It processes both BUY and SELL
signals to verify the formatting and handling logic.
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the Python path to import modules
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from webhook_handeler import SignalHandler

# Sample signal data - BUY signal
BUY_SIGNAL = {
    "instrument": "EURUSD",
    "direction": "BUY",
    "entry_price": 1.0750,
    "stop_loss": 1.0700,
    "take_profit": [1.0800, 1.0850, 1.0900],
    "timeframe": "4H",
    "strategy": "Trend Following",
    "risk_reward": 3.0,
    "risk_percentage": 1.0,
    "ai_verdict": "Strong bullish momentum with support at 1.0720"
}

# Sample signal data - SELL signal
SELL_SIGNAL = {
    "instrument": "GBPUSD",
    "direction": "SELL",
    "entry_price": 1.2650,
    "stop_loss": 1.2700,
    "take_profit": [1.2600, 1.2550, 1.2500],
    "timeframe": "1D",
    "strategy": "Reversal",
    "risk_reward": 2.5,
    "risk_percentage": 1.0,
    "ai_verdict": "Bearish divergence on RSI with resistance at 1.2680"
}

def simulate_signal_processing():
    """Simulate processing of trading signals locally"""
    handler = SignalHandler()
    
    print("\n=== SIMULATING BUY SIGNAL PROCESSING ===")
    print(f"Input BUY signal: {json.dumps(BUY_SIGNAL, indent=2)}")
    
    try:
        # Process BUY signal
        formatted_signal = handler.format_signal(BUY_SIGNAL)
        print("\nFormatted BUY signal:")
        print(formatted_signal)
        print("\n✅ BUY signal processed successfully!")
    except Exception as e:
        print(f"\n❌ Error processing BUY signal: {str(e)}")
    
    print("\n=== SIMULATING SELL SIGNAL PROCESSING ===")
    print(f"Input SELL signal: {json.dumps(SELL_SIGNAL, indent=2)}")
    
    try:
        # Process SELL signal
        formatted_signal = handler.format_signal(SELL_SIGNAL)
        print("\nFormatted SELL signal:")
        print(formatted_signal)
        print("\n✅ SELL signal processed successfully!")
    except Exception as e:
        print(f"\n❌ Error processing SELL signal: {str(e)}")

if __name__ == "__main__":
    simulate_signal_processing() 