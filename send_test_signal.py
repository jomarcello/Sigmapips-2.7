#!/usr/bin/env python3
"""
Send a test signal to the Telegram bot
"""

import argparse
import logging
import os
import sys
import asyncio
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Send a test signal to the Telegram bot")
    parser.add_argument("--instrument", default="GBPUSD", help="Trading instrument")
    parser.add_argument("--direction", default="BUY", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--entry", default="1.2850", help="Entry price")
    parser.add_argument("--stop-loss", default="1.2800", help="Stop loss price")
    parser.add_argument("--take-profit", default="1.2950", help="Take profit price")
    parser.add_argument("--timeframe", default="15", help="Timeframe in minutes")
    parser.add_argument("--save-only", action="store_true", help="Only save the signal to a file, don't send it")
    parser.add_argument("--local", action="store_true", help="Test signal processing locally")
    parser.add_argument("--url", default="https://sigmapips-27-production.up.railway.app/signal", help="URL of the signal endpoint")
    
    args = parser.parse_args()
    
    try:
        # Import test_signal_endpoint function
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from test_signal_endpoint import test_signal_endpoint
        
        logger.info(f"Sending test signal to {args.url}")
        logger.info(f"Instrument: {args.instrument}, Direction: {args.direction}")
        logger.info(f"Entry: {args.entry}, Stop Loss: {args.stop_loss}, Take Profit: {args.take_profit}")
        
        # Run the test signal endpoint function
        result = await test_signal_endpoint(
            args.url,
            args.instrument,
            args.direction,
            args.entry,
            args.stop_loss,
            args.take_profit,
            args.timeframe,
            args.save_only,
            args.local
        )
        
        if result:
            logger.info("✅ Test signal sent successfully!")
        else:
            logger.error("❌ Failed to send test signal")
            sys.exit(1)
    
    except ImportError:
        logger.error("Could not import test_signal_endpoint. Make sure the file exists in the current directory.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error sending test signal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 