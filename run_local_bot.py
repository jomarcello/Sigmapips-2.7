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

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Set environment variables
os.environ["TELEGRAM_BOT_TOKEN"] = "7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["WEBHOOK_URL"] = "http://localhost:8080/webhook"
os.environ["PORT"] = "8080"
os.environ["FORCE_POLLING"] = "true"  # Use polling instead of webhook for local testing

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

async def start_telegram_service():
    """Start the TelegramService"""
    global telegram_service
    try:
        # Initialize TelegramService
        telegram_service = TelegramService()
        
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
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    # Start TelegramService
    await start_telegram_service()

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