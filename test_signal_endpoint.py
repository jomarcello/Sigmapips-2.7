#!/usr/bin/env python3
"""
Test script for the signal endpoint
"""

import asyncio
import json
import logging
import httpx
import argparse
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_signal_endpoint(url, instrument, direction, entry, stop_loss, take_profit, timeframe="15", save_only=False, local_test=False):
    """Test the signal endpoint by sending a test signal"""
    
    # Create the signal payload in the exact format expected by TradingView webhooks
    signal_data = {
        "instrument": instrument,
        "direction": direction.upper(),
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "timeframe": timeframe,
        "interval": timeframe,  # Adding interval field which is used in some parts of the code
        "price": entry,  # Adding price field for TradingView format compatibility
        "sl": stop_loss,  # Adding sl field for TradingView format compatibility
        "timestamp": datetime.now().isoformat()
    }
    
    # Add multiple take profit levels
    if take_profit:
        entry_value = float(entry)
        tp_value = float(take_profit)
        
        # Set TP1 directly from input
        signal_data["tp1"] = take_profit
        
        # For USDJPY SELL with specific values from screenshot
        if instrument == "USDJPY" and direction.upper() == "SELL" and entry == "141.994":
            # Use the exact values from the screenshot
            signal_data["tp1"] = "141.64"  # First TP should be below entry for SELL
            signal_data["tp2"] = "141.286"  # Second TP even lower
            signal_data["tp3"] = "140.932"  # Third TP even lower
        else:
            # Calculate TP2 and TP3 based on direction
            if direction.upper() == "BUY":
                # For BUY signals, TPs should be above entry in ascending order
                tp_diff = abs(tp_value - entry_value)
                signal_data["tp2"] = str(round(entry_value + 1.5 * tp_diff, 3))
                signal_data["tp3"] = str(round(entry_value + 2.0 * tp_diff, 3))
            else:
                # For SELL signals, TPs should be below entry in descending order
                # Make sure TP1 is below entry for SELL signals
                if tp_value > entry_value:
                    # If TP1 was incorrectly provided above entry, adjust it to be below entry
                    tp_diff = abs(float(stop_loss) - entry_value)
                    tp_value = entry_value - tp_diff
                    signal_data["tp1"] = str(round(tp_value, 3))
                else:
                    tp_diff = abs(entry_value - tp_value)
                
                # TP2 and TP3 progressively lower
                signal_data["tp2"] = str(round(entry_value - 1.5 * tp_diff, 3))
                signal_data["tp3"] = str(round(entry_value - 2.0 * tp_diff, 3))
    
    # Save the signal data to a file
    os.makedirs("test_signals", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_signals/signal_{instrument}_{direction}_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(signal_data, f, indent=2)
    
    logger.info(f"Saved test signal to {filename}")
    logger.info(json.dumps(signal_data, indent=2))
    
    if save_only:
        logger.info("Skipping API call, signal data saved to file only")
        return True
    
    if local_test:
        # Simulate processing the signal locally
        logger.info("Performing local test of signal processing...")
        try:
            # Import the TelegramService and process the signal
            from trading_bot.main import TelegramService
            from trading_bot.services.database.db import Database
            
            # Get the bot instance
            db = Database()
            telegram_service = TelegramService(db=db)
            
            # Process the signal
            result = await telegram_service.process_signal(signal_data)
            
            if result:
                logger.info("✅ Local signal processing test successful!")
                return True
            else:
                logger.error("❌ Local signal processing test failed")
                return False
        except Exception as e:
            logger.error(f"❌ Error in local signal processing: {str(e)}")
            return False
    
    # Send the signal to the endpoint
    logger.info(f"Sending test signal to {url}:")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=signal_data,
                timeout=30.0
            )
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            if response.status_code == 200:
                logger.info("✅ Signal endpoint test successful!")
                return True
            else:
                logger.error(f"❌ Signal endpoint test failed with status code: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error testing signal endpoint: {str(e)}")
        return False

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Test the signal endpoint")
    parser.add_argument("--url", default="https://sigmapips-27-production.up.railway.app/signal", help="URL of the signal endpoint")
    parser.add_argument("--instrument", default="USDJPY", help="Trading instrument")
    parser.add_argument("--direction", default="SELL", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--entry", default="141.994", help="Entry price")
    parser.add_argument("--stop-loss", default="142.054", help="Stop loss price")
    parser.add_argument("--take-profit", default="141.64", help="Take profit price")
    parser.add_argument("--timeframe", default="15", help="Timeframe in minutes")
    parser.add_argument("--save-only", action="store_true", help="Only save the signal to a file, don't send it")
    parser.add_argument("--local", action="store_true", help="Test signal processing locally")
    
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(test_signal_endpoint(
        args.url,
        args.instrument,
        args.direction,
        args.entry,
        args.stop_loss,
        args.take_profit,
        args.timeframe,
        args.save_only,
        args.local
    ))

if __name__ == "__main__":
    main() 