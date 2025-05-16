#!/usr/bin/env python3
"""
Signal Forward - Script to forward signals from the trading bot to the signal_saver service.
This script works with the existing bot without modifying main.py.

Usage:
    python signal_forward.py

This script works by:
1. Monkey patching the process_signal methods in the bot
2. Adding a hook to forward signals to the signal_saver service
3. Running as a separate process alongside the main bot
"""

import os
import sys
import json
import logging
import asyncio
import importlib
import aiohttp
import traceback
import argparse
from functools import wraps
from datetime import datetime
import types
import uuid

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("signal_forward.log")
    ]
)
logger = logging.getLogger(__name__)

# Global variable to hold the session
http_session = None

async def create_session():
    """Create a global HTTP session."""
    global http_session
    http_session = aiohttp.ClientSession()
    return http_session

async def close_session():
    """Close the global HTTP session."""
    global http_session
    if http_session:
        await http_session.close()
        http_session = None

async def forward_signal_to_saver(signal_data, user_id=None):
    """Forward signal data to the signal_saver service."""
    global http_session
    
    try:
        # Ensure we have a session
        if not http_session:
            await create_session()
        
        # Get service URL
        signal_saver_url = os.getenv("SIGNAL_SAVER_URL", "http://localhost:8005/webhook")
        
        # Add user ID to signal data if provided
        if user_id:
            signal_data["user_id"] = user_id
        
        # Add timestamp if not present
        if "timestamp" not in signal_data:
            signal_data["timestamp"] = datetime.now().isoformat()
            
        # Add ID if not present
        if "id" not in signal_data:
            signal_data["id"] = str(uuid.uuid4())
            
        # Forward the signal
        async with http_session.post(signal_saver_url, json=signal_data) as response:
            logger.info(f"Forwarded signal to {signal_saver_url}, status: {response.status}")
            
            # Log error details if unsuccessful
            if response.status >= 400:
                response_text = await response.text()
                logger.error(f"Error forwarding signal: {response_text}")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"Error forwarding signal: {str(e)}")
        traceback.print_exc()
        return False

def monkey_patch_bot():
    """
    Monkey patch the SigmaPipsBot class to intercept signals.
    
    This is the key function that adds our signal forwarding capability
    without modifying main.py.
    """
    logger.info("Starting monkey patching of SigmaPipsBot...")
    
    try:
        # Import the bot module (but don't run it)
        sys.path.insert(0, os.path.abspath('.'))
        
        # Try different possible bot module locations
        bot_module = None
        try:
            logger.info("Trying to import from trading_bot.services.telegram_service.bot...")
            from trading_bot.services.telegram_service.bot import SigmaPipsBot
            bot_found = True
        except ImportError:
            logger.warning("Failed to import from trading_bot.services.telegram_service.bot")
            try:
                logger.info("Trying to import from trading_bot.bot...")
                from trading_bot.bot import SigmaPipsBot
                bot_found = True
            except ImportError:
                logger.error("Could not find the SigmaPipsBot class. Make sure you're running this script from the project root.")
                bot_found = False
        
        if not bot_found:
            return False
        
        # Get the original methods
        original_process_signal = SigmaPipsBot.process_signal
        original_process_admin_signal = SigmaPipsBot.process_admin_signal
        original_process_user_signal = SigmaPipsBot.process_user_signal
        
        # Patch the process_signal method
        @wraps(original_process_signal)
        async def patched_process_signal(self, signal_data):
            """Patched version of process_signal that forwards signals to the signal_saver service."""
            # Process the signal with the original method first
            result = await original_process_signal(self, signal_data)
            
            # Forward the signal to the signal_saver service
            try:
                # Make a copy of the signal data to avoid modifying the original
                signal_copy = signal_data.copy() if isinstance(signal_data, dict) else {"raw_signal": str(signal_data)}
                
                # Add signal type
                signal_copy["signal_type"] = "general"
                
                # Forward the signal
                await forward_signal_to_saver(signal_copy)
                
            except Exception as e:
                logger.error(f"Error in patched_process_signal: {str(e)}")
                traceback.print_exc()
            
            # Return the original result
            return result
        
        # Patch the process_admin_signal method
        @wraps(original_process_admin_signal)
        async def patched_process_admin_signal(self, admin_id, signal_data):
            """Patched version of process_admin_signal that forwards signals to the signal_saver service."""
            # Process the signal with the original method first
            result = await original_process_admin_signal(self, admin_id, signal_data)
            
            # Forward the signal to the signal_saver service
            try:
                # Make a copy of the signal data to avoid modifying the original
                signal_copy = signal_data.copy() if isinstance(signal_data, dict) else {"raw_signal": str(signal_data)}
                
                # Add admin ID and signal type
                signal_copy["admin_id"] = admin_id
                signal_copy["signal_type"] = "admin"
                
                # Forward the signal
                await forward_signal_to_saver(signal_copy, str(admin_id))
                
            except Exception as e:
                logger.error(f"Error in patched_process_admin_signal: {str(e)}")
                traceback.print_exc()
            
            # Return the original result
            return result
            
        # Patch the process_user_signal method
        @wraps(original_process_user_signal)
        async def patched_process_user_signal(self, user_id, signal_data):
            """Patched version of process_user_signal that forwards signals to the signal_saver service."""
            # Process the signal with the original method first
            result = await original_process_user_signal(self, user_id, signal_data)
            
            # Forward the signal to the signal_saver service
            try:
                # Make a copy of the signal data to avoid modifying the original
                signal_copy = signal_data.copy() if isinstance(signal_data, dict) else {"raw_signal": str(signal_data)}
                
                # Add user ID and signal type
                signal_copy["user_id"] = user_id
                signal_copy["signal_type"] = "user"
                
                # Forward the signal
                await forward_signal_to_saver(signal_copy, str(user_id))
                
            except Exception as e:
                logger.error(f"Error in patched_process_user_signal: {str(e)}")
                traceback.print_exc()
            
            # Return the original result
            return result
            
        # Assign patched methods to the bot class
        SigmaPipsBot.process_signal = patched_process_signal
        SigmaPipsBot.process_admin_signal = patched_process_admin_signal
        SigmaPipsBot.process_user_signal = patched_process_user_signal
        
        logger.info("Successfully patched SigmaPipsBot methods")
        return True
        
    except Exception as e:
        logger.error(f"Error during monkey patching: {str(e)}")
        traceback.print_exc()
        return False

async def run():
    """Main function to run the signal forwarder."""
    # Create HTTP session
    await create_session()
    
    # Monkey patch the bot
    if not monkey_patch_bot():
        logger.error("Failed to monkey patch the bot, exiting")
        await close_session()
        return
    
    # Keep running to maintain patching
    logger.info("Signal forwarder is running...")
    try:
        while True:
            await asyncio.sleep(60)
            logger.info("Signal forwarder is still active")
    except asyncio.CancelledError:
        logger.info("Signal forwarder task cancelled")
    finally:
        await close_session()

def main():
    """Entry point for script."""
    parser = argparse.ArgumentParser(description="Signal Forward - Forward signals to the signal_saver service")
    parser.add_argument("--saver-url", type=str, 
                        default=os.getenv("SIGNAL_SAVER_URL", "http://localhost:8005/webhook"),
                        help="URL of the signal_saver webhook endpoint")
    parser.add_argument("--log-level", type=str, default=os.getenv("LOG_LEVEL", "INFO"), 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level (default: INFO)")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["SIGNAL_SAVER_URL"] = args.saver_url
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Run the signal forwarder
    try:
        logger.info(f"Starting signal forwarder, forwarding to {args.saver_url}")
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Signal forwarder stopped by user")
    except Exception as e:
        logger.error(f"Error in signal forwarder: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 