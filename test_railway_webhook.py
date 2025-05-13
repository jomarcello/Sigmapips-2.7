#!/usr/bin/env python
import requests
import json
import logging
import argparse
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_railway_webhook(webhook_url):
    """Test sending a signal to the Railway webhook endpoint"""
    try:
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
        
        # Ensure the webhook URL has the correct format
        if not webhook_url.startswith("http"):
            webhook_url = f"https://{webhook_url}"
        
        # Add /webhook path if not present
        if not webhook_url.endswith("/webhook"):
            webhook_url = f"{webhook_url}/webhook"
        
        logger.info(f"Final webhook URL: {webhook_url}")
        
        # Send the signal to the webhook
        response = requests.post(
            webhook_url,
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=10  # 10 second timeout
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
        logger.error(f"Error in test_railway_webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test sending a signal to the Railway webhook endpoint")
    parser.add_argument("webhook_url", help="Railway webhook URL (e.g., sigmapips-27-production.up.railway.app)")
    
    args = parser.parse_args()
    
    success = test_railway_webhook(args.webhook_url)
    sys.exit(0 if success else 1) 