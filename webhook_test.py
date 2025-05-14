#!/usr/bin/env python3
"""
Send a test signal directly to the webhook endpoint
"""

import requests
import json
import logging
import argparse
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_webhook_signal(webhook_url, instrument, direction, entry, stop_loss, take_profit, timeframe="15"):
    """Send a test signal to the webhook endpoint"""
    try:
        # Create signal ID
        signal_id = f"{instrument}_{direction}_{timeframe}_{int(datetime.now().timestamp())}"
        
        # Convert string values to float for proper formatting
        entry_price = float(entry)
        stop_loss_price = float(stop_loss)
        take_profit_prices = [float(take_profit)]
        
        # Add additional take profit levels
        tp_diff = abs(entry_price - take_profit_prices[0])
        if direction.upper() == "BUY":
            take_profit_prices.append(entry_price + 1.5 * tp_diff)
            take_profit_prices.append(entry_price + 2.0 * tp_diff)
        else:
            take_profit_prices.append(entry_price - 1.5 * tp_diff)
            take_profit_prices.append(entry_price - 2.0 * tp_diff)
        
        # Calculate risk/reward ratio
        risk = abs(entry_price - stop_loss_price)
        reward = abs(take_profit_prices[0] - entry_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        # Create signal data in the format expected by the webhook handler
        signal_data = {
            "id": signal_id,
            "instrument": instrument,
            "direction": direction.upper(),
            "entry_price": entry_price,
            "stop_loss": stop_loss_price,
            "take_profit": take_profit_prices,
            "timeframe": timeframe,
            "strategy": "TradingView Signal",
            "risk_reward": risk_reward,
            "risk_percentage": 1.0,
            "ai_verdict": "This is a test signal sent via the webhook test script."
        }
        
        # Log the signal data
        logger.info(f"Sending signal to webhook: {json.dumps(signal_data, indent=2)}")
        
        # Send the signal to the webhook
        response = requests.post(
            webhook_url,
            json=signal_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Log the response
        logger.info(f"Webhook response status code: {response.status_code}")
        logger.info(f"Webhook response: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ Signal sent successfully!")
            return True
        else:
            logger.error(f"❌ Failed to send signal: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error sending signal: {str(e)}")
        return False

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Send a test signal to the webhook endpoint")
    parser.add_argument("--webhook-url", default="https://sigmapips.com/webhook", help="Webhook URL")
    parser.add_argument("--instrument", default="EURUSD", help="Trading instrument")
    parser.add_argument("--direction", default="BUY", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--entry", default="1.0850", help="Entry price")
    parser.add_argument("--stop-loss", default="1.0800", help="Stop loss price")
    parser.add_argument("--take-profit", default="1.0900", help="Take profit price")
    parser.add_argument("--timeframe", default="15", help="Timeframe in minutes")
    parser.add_argument("--local", action="store_true", help="Use local webhook URL (http://localhost:8080/webhook)")
    parser.add_argument("--signal-endpoint", action="store_true", help="Use /signal endpoint instead of /webhook")
    
    args = parser.parse_args()
    
    # Use local webhook URL if specified
    base_url = "http://localhost:8080" if args.local else args.webhook_url
    endpoint = "/signal" if args.signal_endpoint else "/webhook"
    webhook_url = f"{base_url}{endpoint}"
    
    # Send the signal
    success = send_webhook_signal(
        webhook_url,
        args.instrument,
        args.direction,
        args.entry,
        args.stop_loss,
        args.take_profit,
        args.timeframe
    )
    
    if success:
        logger.info("✅ Signal sent successfully!")
    else:
        logger.error("❌ Failed to send signal")

if __name__ == "__main__":
    main() 