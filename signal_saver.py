#!/usr/bin/env python3
"""
Signal Saver - Standalone service that saves signals for the SigmaPips trading bot.

This script runs as a separate process alongside the main bot and provides:
1. A webhook endpoint to receive signals
2. Automatic storage of signals in the SignalStorageService
3. Access to stored signals via API endpoints

Usage:
    python signal_saver.py

Environment variables:
    WEBHOOK_PORT: Port to listen on (default: 8005)
    WEBHOOK_PATH: Path for the webhook endpoint (default: /webhook)
    STORAGE_DIR: Directory to store signals (default: ./storage)
    LOG_LEVEL: Logging level (default: INFO)
"""

import os
import json
import logging
import asyncio
import sys
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import signal
from aiohttp import web
import aiohttp
import argparse
import traceback

# Add parent directory to path so we can import from trading_bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our custom services
from trading_bot.services.signal_storage_service import SignalStorageService
from trading_bot.services.signal_interceptor import SignalInterceptor

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("signal_saver.log")
    ]
)
logger = logging.getLogger(__name__)

# Global variables
webhook_port = int(os.getenv("WEBHOOK_PORT", "8005"))
webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
storage_dir = os.getenv("STORAGE_DIR", "./storage")
interceptor = None  # Will be initialized in main()

async def handle_webhook(request):
    """Handle incoming webhook requests with signals."""
    try:
        # Get the request body
        body = await request.json()
        logger.info(f"Received webhook: {json.dumps(body)}")
        
        # Extract user ID if present
        user_id = body.get("user_id", "default")
        
        # Intercept and store the signal
        signal_id = await interceptor.intercept_signal(body, user_id)
        
        # Return success response
        return web.json_response({
            "status": "success", 
            "message": f"Signal {signal_id} intercepted and stored"
        })
        
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        traceback.print_exc()
        return web.json_response({
            "status": "error", 
            "message": f"Error handling webhook: {str(e)}"
        }, status=500)

async def handle_signals_query(request):
    """Handle API requests for stored signals."""
    try:
        # Get user ID from query params, default to 'default'
        user_id = request.query.get("user_id", "default")
        
        # Get instrument if specified
        instrument = request.query.get("instrument")
        
        # Get signals
        if instrument:
            signals = await interceptor.get_signals_for_instrument(user_id, instrument)
            logger.info(f"Retrieved {len(signals)} signals for user {user_id} and instrument {instrument}")
        else:
            signals = await interceptor.get_signals(user_id)
            logger.info(f"Retrieved {len(signals)} signals for user {user_id}")
        
        # Return signals
        return web.json_response({
            "status": "success",
            "signals": signals
        })
        
    except Exception as e:
        logger.error(f"Error handling signals query: {str(e)}")
        return web.json_response({
            "status": "error",
            "message": f"Error retrieving signals: {str(e)}"
        }, status=500)

async def handle_signal_query(request):
    """Handle API requests for a specific signal."""
    try:
        # Get user ID and signal ID from query params
        user_id = request.query.get("user_id", "default")
        signal_id = request.match_info.get("signal_id")
        
        if not signal_id:
            return web.json_response({
                "status": "error",
                "message": "Signal ID is required"
            }, status=400)
            
        # Get signal
        signal = await interceptor.get_signal(user_id, signal_id)
        
        if signal:
            logger.info(f"Retrieved signal {signal_id} for user {user_id}")
            return web.json_response({
                "status": "success",
                "signal": signal
            })
        else:
            logger.warning(f"Signal {signal_id} not found for user {user_id}")
            return web.json_response({
                "status": "error",
                "message": f"Signal {signal_id} not found for user {user_id}"
            }, status=404)
        
    except Exception as e:
        logger.error(f"Error handling signal query: {str(e)}")
        return web.json_response({
            "status": "error",
            "message": f"Error retrieving signal: {str(e)}"
        }, status=500)

async def forward_to_bot_webhook(app):
    """Forward any signals to the bot's webhook if enabled."""
    bot_webhook_url = os.getenv("BOT_WEBHOOK_URL")
    if not bot_webhook_url:
        logger.info("BOT_WEBHOOK_URL not set, not forwarding signals to bot")
        return
        
    logger.info(f"Will forward signals to bot webhook: {bot_webhook_url}")
    
    app["bot_webhook_url"] = bot_webhook_url
    app["bot_webhook_session"] = aiohttp.ClientSession()

async def cleanup_bot_webhook(app):
    """Clean up the bot webhook session."""
    if "bot_webhook_session" in app:
        await app["bot_webhook_session"].close()

def setup_routes(app):
    """Set up the web routes."""
    app.router.add_post(webhook_path, handle_webhook)
    app.router.add_get("/api/signals", handle_signals_query)
    app.router.add_get("/api/signal/{signal_id}", handle_signal_query)
    app.router.add_static("/ui", "./ui")  # Serve static files for UI

async def start_webapp():
    """Start the webhook server."""
    app = web.Application()
    
    # Add routes
    setup_routes(app)
    
    # Set up signal forwarding to bot if enabled
    app.on_startup.append(forward_to_bot_webhook)
    app.on_cleanup.append(cleanup_bot_webhook)
    
    # Set up the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", webhook_port)
    await site.start()
    
    logger.info(f"Signal Saver webhook server started on port {webhook_port}")
    logger.info(f"Webhook endpoint: http://localhost:{webhook_port}{webhook_path}")
    logger.info(f"API endpoints:")
    logger.info(f"  - http://localhost:{webhook_port}/api/signals?user_id=USER_ID&instrument=INSTRUMENT")
    logger.info(f"  - http://localhost:{webhook_port}/api/signal/SIGNAL_ID?user_id=USER_ID")
    logger.info(f"UI: http://localhost:{webhook_port}/ui/")
    
    return runner, site

async def main():
    """Main function."""
    global interceptor
    
    try:
        # Initialize the signal interceptor
        interceptor = SignalInterceptor()
        await interceptor.setup()
        
        # Start the webhook server
        runner, site = await start_webapp()
        
        # Start the signal interceptor
        interceptor.start_monitoring()
        
        # Keep running until interrupted
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        
        # Set up signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(stop_event, runner, site)))
        
        # Wait for stop event
        await stop_event.wait()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        traceback.print_exc()

async def shutdown(stop_event, runner, site):
    """Shut down the application gracefully."""
    logger.info("Shutting down...")
    
    # Stop the signal interceptor
    if interceptor:
        interceptor.stop_monitoring()
    
    # Stop the web server
    await runner.cleanup()
    
    # Set the stop event
    stop_event.set()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Signal Saver - Saves signals for the SigmaPips trading bot")
    parser.add_argument("--port", type=int, default=webhook_port, help=f"Port to listen on (default: {webhook_port})")
    parser.add_argument("--path", type=str, default=webhook_path, help=f"Webhook path (default: {webhook_path})")
    parser.add_argument("--storage", type=str, default=storage_dir, help=f"Storage directory (default: {storage_dir})")
    parser.add_argument("--log-level", type=str, default=os.getenv("LOG_LEVEL", "INFO"), 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level (default: INFO)")
    
    args = parser.parse_args()
    
    # Update global variables with command-line arguments
    webhook_port = args.port
    webhook_path = args.path
    storage_dir = args.storage
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Run the main function
    asyncio.run(main()) 