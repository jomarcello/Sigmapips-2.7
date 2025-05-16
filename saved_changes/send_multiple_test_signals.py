import requests
import json
import logging
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def send_signal(webhook_url, signal_data):
    """Send a signal to the webhook URL"""
    try:
        logger.info(f"Sending signal to: {webhook_url}")
        logger.info(f"Signal data: {json.dumps(signal_data, indent=2)}")
        
        response = requests.post(
            webhook_url,
            json=signal_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        return response.status_code == 200
    
    except Exception as e:
        logger.error(f"Error sending signal: {str(e)}")
        return False

def send_multiple_test_signals():
    """Send multiple test signals with different formats"""
    # Webhook URL
    webhook_url = "https://railwaywebhook-production-8102.up.railway.app/webhook"
    
    # Get current timestamp
    now = datetime.now()
    timestamp = now.isoformat()
    
    # Create different test signals
    signals = [
        # Signal 1: Simple format
        {
            "instrument": "EURUSD",
            "direction": "BUY",
            "entry": 1.0850,
            "stop_loss": 1.0800,
            "take_profit": 1.0900,
            "timeframe": "4H",
            "timestamp": timestamp
        },
        
        # Signal 2: Format from test_signals directory
        {
            "instrument": "GBPUSD",
            "direction": "SELL",
            "entry": "1.2650",
            "stop_loss": "1.2700",
            "take_profit": "1.2600",
            "timeframe": "1D",
            "interval": "1D",
            "price": "1.2650",
            "sl": "1.2700",
            "timestamp": timestamp,
            "tp1": "1.2600",
            "tp2": "1.2550",
            "tp3": "1.2500"
        },
        
        # Signal 3: Detailed format with array
        {
            "id": f"USDJPY_SELL_{now.strftime('%Y%m%d_%H%M%S')}",
            "type": "trading_signal",
            "source": "manual_test",
            "instrument": "USDJPY",
            "direction": "SELL",
            "entry_price": 154.50,
            "stop_loss": 155.00,
            "take_profit": [154.00, 153.50, 153.00],
            "timeframe": "1H",
            "risk_reward": 1.5,
            "timestamp": timestamp,
            "strategy": "Test Strategy",
            "analysis": "This is test signal #3 with array format for take profit levels.",
            "probability": 80
        },
        
        # Signal 4: Extra fields format
        {
            "instrument": "XAUUSD",
            "direction": "BUY",
            "entry": 2345.00,
            "stop_loss": 2335.00,
            "take_profit": 2365.00,
            "timeframe": "4H",
            "timestamp": timestamp,
            "risk_percentage": 1.0,
            "signal_quality": "high",
            "market_condition": "bullish",
            "indicators": {
                "rsi": 65,
                "macd": "bullish",
                "trend": "uptrend"
            },
            "expiration": (now.timestamp() + 86400) * 1000  # 24 hours from now in milliseconds
        }
    ]
    
    # Send each signal with a delay between them
    results = []
    for i, signal in enumerate(signals, 1):
        logger.info(f"\nSending test signal #{i}...")
        success = send_signal(webhook_url, signal)
        results.append(success)
        
        # Wait a bit between signals (except after the last one)
        if i < len(signals):
            time.sleep(2)
    
    # Print summary
    logger.info("\n===== RESULTS SUMMARY =====")
    for i, result in enumerate(results, 1):
        status = "✅ SUCCESS" if result else "❌ FAILED"
        logger.info(f"Signal #{i}: {status}")
    
    successful = sum(results)
    logger.info(f"\nSuccessfully sent {successful} out of {len(signals)} signals.")

if __name__ == "__main__":
    send_multiple_test_signals() 