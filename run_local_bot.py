#!/usr/bin/env python
import os
import asyncio
import logging
from trading_bot.main import TelegramService, setup_logging
import uvicorn
from fastapi import FastAPI, Request
import json
import threading
import signal
import sys
import argparse
import redis

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Create TelegramService
telegram_service = None

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhook requests"""
    try:
        # Parse the incoming JSON
        payload = await request.json()
        logger.info(f"Received webhook payload: {json.dumps(payload, indent=2)}")
        
        # Process the signal
        if telegram_service:
            await telegram_service.process_signal(payload)
            return {"status": "success", "message": "Signal processed"}
        else:
            logger.error("TelegramService not initialized")
            return {"status": "error", "message": "TelegramService not initialized"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

async def process_redis_signals():
    """Process signals stored in Redis"""
    try:
        # Connect to Redis
        r = redis.from_url("redis://localhost:6379", decode_responses=True)
        
        # Get all signal keys
        signal_keys = r.keys("signal:test:*")
        logger.info(f"Found {len(signal_keys)} test signals in Redis")
        
        if not signal_keys:
            logger.warning("No test signals found in Redis")
            return
        
        # Process each signal
        for key in signal_keys:
            try:
                # Get signal data
                signal_json = r.get(key)
                if not signal_json:
                    logger.warning(f"Signal {key} not found in Redis")
                    continue
                
                # Parse signal data
                signal_data = json.loads(signal_json)
                logger.info(f"Processing signal: {signal_data}")
                
                # Process the signal
                if telegram_service:
                    success = await telegram_service.process_signal(signal_data)
                    if success:
                        logger.info(f"✅ Successfully processed signal {key}")
                    else:
                        logger.error(f"❌ Failed to process signal {key}")
                else:
                    logger.error("TelegramService not initialized")
            except Exception as e:
                logger.error(f"Error processing signal {key}: {str(e)}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        logger.error(f"Error connecting to Redis: {str(e)}")
        import traceback
        traceback.print_exc()

async def start_telegram_service(token=None, process_signals=False):
    """Start the TelegramService"""
    global telegram_service
    try:
        # Set bot token if provided
        if token:
            os.environ["TELEGRAM_BOT_TOKEN"] = token
        else:
            # Default token
            os.environ["TELEGRAM_BOT_TOKEN"] = "7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk"
        
        # Set other environment variables
        os.environ["REDIS_URL"] = "redis://localhost:6379"
        os.environ["WEBHOOK_URL"] = "http://localhost:8080/webhook"
        os.environ["PORT"] = "8080"
        os.environ["FORCE_POLLING"] = "true"  # Use polling instead of webhook for local testing
        
        # Initialize TelegramService
        from trading_bot.services.database.db import Database
        db = Database()
        telegram_service = TelegramService(db=db, bot_token=token)
        
        # Process signals if requested
        if process_signals:
            logger.info("Processing signals from Redis...")
            await process_redis_signals()
        
        # Start the bot
        await telegram_service.run()
    except Exception as e:
        logger.error(f"Error starting TelegramService: {str(e)}")
        import traceback
        traceback.print_exc()

def run_fastapi():
    """Run the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8080)

async def main():
    """Main function to run both services"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the local bot")
    parser.add_argument("--token", help="Telegram bot token")
    parser.add_argument("--process-signals", action="store_true", help="Process signals from Redis")
    parser.add_argument("--local", action="store_true", help="Run in local mode")
    args = parser.parse_args()
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    # Start TelegramService
    await start_telegram_service(token=args.token, process_signals=args.process_signals)

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    logger.info("Shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc() 