"""
FastAPI route configuration for the trading bot
This module registers all webhook routes for the bot to ensure all common webhook endpoints work.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

def register_webhook_routes(app: FastAPI):
    """
    Register all webhook routes to the FastAPI app
    This ensures that common webhook endpoints like /webhook/signal, /webhook, /api/signal work
    and point to the same handler.
    """
    
    @app.post("/webhook")
    async def webhook_endpoint(request: Request):
        """Webhook endpoint for receiving trading signals"""
        logger.info("Received request on /webhook endpoint, forwarding to /signal")
        # Forward to the main signal handler
        from trading_bot.app import receive_signal
        return await receive_signal(request)
    
    @app.post("/webhook/signal")
    async def webhook_signal_endpoint(request: Request):
        """Webhook endpoint for receiving trading signals via /webhook/signal"""
        logger.info("Received request on /webhook/signal endpoint, forwarding to /signal")
        # Forward to the main signal handler
        from trading_bot.app import receive_signal
        return await receive_signal(request)
    
    @app.post("/api/signal")
    async def api_signal_endpoint(request: Request):
        """API endpoint for receiving trading signals via /api/signal"""
        logger.info("Received request on /api/signal endpoint, forwarding to /signal")
        # Forward to the main signal handler
        from trading_bot.app import receive_signal
        return await receive_signal(request)
    
    @app.post("/bot/signal")
    async def bot_signal_endpoint(request: Request):
        """Bot endpoint for receiving trading signals via /bot/signal"""
        logger.info("Received request on /bot/signal endpoint, forwarding to /signal")
        # Forward to the main signal handler
        from trading_bot.app import receive_signal
        return await receive_signal(request)
    
    logger.info("Additional webhook routes registered successfully") 