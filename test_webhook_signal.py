#!/usr/bin/env python
import requests
import json
import logging
import os
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_webhook_signal():
    """Test sending a signal to the webhook endpoint"""
    try:
        # Default to localhost for testing
        webhook_url = os.getenv("WEBHOOK_URL", "http://localhost:8080/webhook")
        
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
        
        logger.info(f"Sending test signal to webhook: {webhook_url}")
        logger.info(f"Signal data: {json.dumps(test_signal, indent=2)}")
        
        # Send the signal to the webhook
        response = requests.post(
            webhook_url,
            json=test_signal,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info("Signal successfully sent to webhook")
            return True
        else:
            logger.error(f"Failed to send signal to webhook: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"Error in test_webhook_signal: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_webhook_signal()
    sys.exit(0 if success else 1) 