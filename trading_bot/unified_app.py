"""
Unified Application - Starts both the FastAPI server and Telegram bot in a single process
to avoid multiple bot instances conflicts.
"""

import os
import sys
import asyncio
import threading
import logging
import uvicorn
from contextlib import asynccontextmanager

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define a shared state object for communication between bot and API
class SharedState:
    """Shared state between FastAPI and Telegram bot"""
    def __init__(self):
        self.bot_ready = False
        self.telegram_service = None
        self.db = None
        self.stripe_service = None
        self.shutdown_event = asyncio.Event()
        

# Create shared state instance
shared_state = SharedState()

# Initialize FastAPI with lifespan that starts the bot
@asynccontextmanager
async def lifespan(app):
    """
    FastAPI lifespan handler to start and stop the Telegram bot
    """
    # Start the bot in a background task
    logger.info("Starting Telegram bot in background task")
    
    # Import here to avoid circular imports
    from trading_bot.services.database.db import Database
    from trading_bot.services.payment_service.stripe_service import StripeService
    from trading_bot.main import TelegramService, setup_logging
    
    # Set up logging
    setup_logging()
    
    # Initialize database
    shared_state.db = Database()
    logger.info("Database connection initialized")
    
    # Initialize Stripe service
    try:
        shared_state.stripe_service = StripeService(db=shared_state.db)
        logger.info("Stripe service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Stripe service: {str(e)}")
    
    # Create Telegram service instance
    try:
        shared_state.telegram_service = TelegramService(
            db=shared_state.db,
            stripe_service=shared_state.stripe_service
        )
        logger.info("Telegram service instance created")
        
        # Start the bot in a background task
        bot_task = asyncio.create_task(run_bot_in_background())
        shared_state.bot_task = bot_task
        
        # Wait until the bot reports it's ready
        while not shared_state.bot_ready:
            logger.info("Waiting for Telegram bot to initialize...")
            await asyncio.sleep(1)
            
        logger.info("Bot initialized and ready")
        
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {str(e)}")
        logger.exception(e)
    
    # Continue with FastAPI startup
    yield
    
    # Signal bot to shut down when FastAPI is shutting down
    logger.info("FastAPI shutting down, stopping Telegram bot")
    shared_state.shutdown_event.set()
    
    if hasattr(shared_state, 'bot_task'):
        try:
            # Wait for bot to shut down with timeout
            await asyncio.wait_for(shared_state.bot_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Telegram bot did not shut down gracefully, forcing exit")
    
    logger.info("Unified application shutdown complete")

# Create FastAPI app with the lifespan
from fastapi import FastAPI
app = FastAPI(lifespan=lifespan)

# Import the app routes
from trading_bot.app import app as api_app

# Copy all routes and middleware from the original app
app.routes.extend(api_app.routes)
app.middleware = api_app.middleware
app.exception_handlers = api_app.exception_handlers

# Expose the shared state to the app
app.state.shared_state = shared_state

# Add a signal endpoint override that uses the existing bot instance
from fastapi import Request, HTTPException
import json

@app.post("/signal")
async def process_signal(request: Request):
    """Process signal using the existing bot instance"""
    try:
        # Parse signal data from JSON
        signal_data = await request.json()
        logger.info(f"Received signal via unified webhook endpoint")
        
        if shared_state.telegram_service is None:
            raise HTTPException(status_code=503, detail="Telegram bot not initialized")
        
        # Process signal using the existing bot instance
        result = await shared_state.telegram_service.process_signal(signal_data)
        
        if result:
            logger.info("Signal processed successfully")
            return {"status": "success", "message": "Signal processed successfully"}
        else:
            logger.error("Failed to process signal")
            raise HTTPException(status_code=500, detail="Failed to process signal")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        logger.error(f"Error processing signal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing signal: {str(e)}")

# Register additional webhook routes
from trading_bot.routing import register_webhook_routes
register_webhook_routes(app)
logger.info("Registered additional webhook routes")

# Function to run the bot in the background
async def run_bot_in_background():
    """Run the Telegram bot in the background"""
    try:
        logger.info("Starting Telegram bot processing")
        
        # Initialize and start the bot
        if shared_state.telegram_service:
            # Run the bot
            await shared_state.telegram_service.run()
            
            # Set the ready flag
            shared_state.bot_ready = True
            
            # Wait for shutdown signal
            await shared_state.shutdown_event.wait()
            
            logger.info("Bot shutdown signal received")
            
            # Try to stop the bot gracefully
            if shared_state.telegram_service and shared_state.telegram_service.application:
                await shared_state.telegram_service.application.stop()
                logger.info("Bot stopped gracefully")
                
    except Exception as e:
        logger.error(f"Error running Telegram bot: {str(e)}")
        logger.exception(e)

# Function to start uvicorn in a separate thread
def run_uvicorn():
    """Run uvicorn server in a separate thread"""
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(
        "trading_bot.unified_app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

# Main entry point
if __name__ == "__main__":
    logger.info("Starting unified application")
    
    # Start uvicorn in a separate thread
    uvicorn_thread = threading.Thread(target=run_uvicorn)
    uvicorn_thread.daemon = True
    uvicorn_thread.start()
    
    # Run the asyncio event loop for the bot
    try:
        # Get the event loop
        loop = asyncio.get_event_loop()
        
        # Setup shutdown handling
        shutdown_event = asyncio.Event()
        
        # Start the bot
        bot_task = asyncio.ensure_future(run_bot_in_background())
        
        # Keep the main thread running
        logger.info("Main thread running, waiting for shutdown signal")
        try:
            # This will keep the main thread running until someone presses Ctrl+C
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down")
            # Set shutdown event to stop the bot
            shared_state.shutdown_event.set()
            # Wait for the bot to stop
            loop.run_until_complete(bot_task)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    except Exception as e:
        logger.error(f"Error in main thread: {str(e)}")
        logger.exception(e)
    finally:
        logger.info("Unified application shutting down") 
        # Clean up the event loop
        loop.close() 