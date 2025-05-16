import requests
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def send_new_signal():
    """Send a new trading signal to the webhook URL"""
    # Webhook URL
    webhook_url = "https://railwaywebhook-production-8102.up.railway.app/webhook"
    
    # Current timestamp
    now = datetime.now()
    timestamp = now.isoformat()
    
    # Create a different test signal (GBPJPY this time)
    test_signal = {
        "instrument": "GBPJPY",
        "direction": "SELL",
        "entry": 193.500,
        "stop_loss": 194.200,
        "take_profit": [192.500, 191.800, 191.000],
        "timeframe": "1H",
        "timestamp": timestamp,
        "strategy": "Test Strategy",
        "risk_reward": 1.8,
        "probability": 70,
        "notes": "Nieuwe test signal via webhook"
    }
    
    logger.info(f"Sending new signal to: {webhook_url}")
    logger.info(f"Signal data: {json.dumps(test_signal, indent=2)}")
    
    try:
        # Send POST request to the webhook
        response = requests.post(
            webhook_url,
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ SUCCESS! Signal sent successfully")
            return True
        else:
            logger.error(f"❌ Failed to send signal: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending signal: {str(e)}")
        return False

if __name__ == "__main__":
    success = send_new_signal()
    if success:
        print("\n✅ Signal is succesvol verzonden naar de webhook!")
    else:
        print("\n❌ Verzenden van signal is mislukt") 