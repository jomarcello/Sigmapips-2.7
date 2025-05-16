#!/usr/bin/env python
"""
Telegram bot connection verification script
This script tests if the Telegram bot is properly configured and can receive messages
"""

import os
import sys
import asyncio
import logging
import argparse
import json
import time
import requests
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_ping(url):
    """Test if the service is reachable with a ping"""
    ping_url = f"{url.rstrip('/')}/ping"
    logger.info(f"Testing ping endpoint: {ping_url}")
    
    try:
        response = requests.get(ping_url, timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Service is reachable! Response: {response.text}")
            return True
        else:
            logger.warning(f"⚠️ Service returned non-200 response: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ Service not reachable at {url}: {str(e)}")
        return False

def send_test_signal(url, include_timestamp=True):
    """Send a test signal to the webhook endpoint"""
    
    # Create a unique test signal
    test_id = int(time.time())
    test_signal = {
        "instrument": "EURUSD",
        "direction": "BUY",
        "entry": 1.0850,
        "stop_loss": 1.0800,
        "take_profit": 1.0900,
        "timeframe": "15",
        "test_id": test_id
    }
    
    # Add a timestamp for uniqueness if requested
    if include_timestamp:
        test_signal["timestamp"] = datetime.now().isoformat()
        
    # Ensure the URL ends with /signal
    if not url.endswith("/signal"):
        url = f"{url.rstrip('/')}/signal"
        
    logger.info(f"Sending test signal to: {url}")
    logger.info(f"Test signal data: {json.dumps(test_signal, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        if response.status_code == 200:
            logger.info(f"✅ SUCCESS! Test signal sent successfully")
            return True, test_signal
        else:
            logger.warning(f"⚠️ Failed to send test signal. Status code: {response.status_code}")
            return False, test_signal
            
    except requests.RequestException as e:
        logger.error(f"❌ Error sending test signal: {str(e)}")
        return False, test_signal

def main():
    """Main function to verify bot connection"""
    parser = argparse.ArgumentParser(description="Verify Telegram bot connection")
    parser.add_argument("--url", help="URL of the webhook service", default=os.environ.get("WEBHOOK_URL", "https://sigmapips-27-production.up.railway.app"))
    parser.add_argument("--token", help="Telegram bot token to use for testing")
    parser.add_argument("--chat-id", help="Telegram chat ID to send a direct message to")
    parser.add_argument("--no-timestamp", help="Don't add timestamp to the test signal", action="store_true")
    args = parser.parse_args()
    
    # Set token if provided
    if args.token:
        os.environ["TELEGRAM_BOT_TOKEN"] = args.token
    
    # Print header
    logger.info("=" * 50)
    logger.info("TELEGRAM BOT CONNECTION VERIFICATION")
    logger.info("=" * 50)
    logger.info(f"Testing service at: {args.url}")
    
    # Step 1: Check if service is reachable
    if not test_ping(args.url):
        logger.error("❌ Service ping failed, aborting test")
        return False
    
    # Step 2: Send a test signal
    success, test_signal = send_test_signal(args.url, not args.no_timestamp)
    
    if success:
        logger.info("\n✅ TEST SUMMARY:")
        logger.info("✓ Service is reachable")
        logger.info("✓ Test signal sent successfully")
        logger.info(f"✓ Test signal ID: {test_signal.get('test_id')}")
        
        # Step 3: Provide instructions for verification
        logger.info("\n🔍 VERIFICATION INSTRUCTIONS:")
        logger.info("1. Check if the signal was received by the bot")
        logger.info("2. Verify the formatted signal message in Telegram")
        logger.info("3. Confirm that all subscriber(s) received the signal")
        
        if args.chat_id:
            logger.info(f"4. Check if chat ID {args.chat_id} received the signal")
        
        logger.info("\nIf administrators received the test signal, the webhook connection is working correctly!")
        return True
    else:
        logger.error("\n❌ TEST SUMMARY:")
        logger.error("✓ Service is reachable")
        logger.error("✗ Test signal sending failed")
        logger.error("\nThe webhook endpoint is reachable but couldn't process the signal.")
        logger.error("Check the application logs for more details.")
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 