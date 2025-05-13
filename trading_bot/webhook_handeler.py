"""
Webhook handler for Telegram bot API.
This is a standalone module to handle webhook requests.
"""

import logging
import json
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookHandler:
    """Handler for Telegram webhooks"""
    
    def __init__(self):
        """Initialize the webhook handler"""
        self.logger = logging.getLogger(__name__)
        # Get the base URL for internal communication
        self.base_url = os.environ.get("INTERNAL_API_URL", "http://localhost:8000")
        self.logger.info(f"Using internal API URL: {self.base_url}")
    
    async def handle_webhook(self, request: Request):
        """Handle a webhook request"""
        try:
            # Log the incoming request
            body = await request.body()
            self.logger.info(f"Received webhook payload: {body.decode('utf-8')[:100]}...")
            
            # Parse JSON data
            try:
                data = await request.json()
            except json.JSONDecodeError:
                self.logger.error("Invalid JSON in request body")
                return JSONResponse(content={"status": "error", "message": "Invalid JSON"}, status_code=400)
            
            # Log the parsed data
            self.logger.info(f"Webhook data: {data}")
            
            # Return success
            return JSONResponse(content={"status": "success", "message": "Webhook received"})
        except Exception as e:
            self.logger.error(f"Error processing webhook: {str(e)}")
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
    async def handle_signal(self, request: Request):
        """Handle a signal webhook request"""
        try:
            # Log the incoming request
            body = await request.body()
            self.logger.info(f"Received signal payload: {body.decode('utf-8')[:100]}...")
            
            # Parse JSON data
            try:
                data = await request.json()
            except json.JSONDecodeError:
                self.logger.error("Invalid JSON in signal request body")
                return JSONResponse(content={"status": "error", "message": "Invalid JSON"}, status_code=400)
            
            # Log the parsed data
            self.logger.info(f"Signal data: {data}")
            
            # Forward to the main signal endpoint
            try:
                # Use the internal API URL to forward to the /signal endpoint
                signal_url = f"{self.base_url}/signal"
                self.logger.info(f"Forwarding signal to: {signal_url}")
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        signal_url,
                        json=data,
                        timeout=30.0
                    )
                    
                    # Log the response
                    self.logger.info(f"Signal forwarding response: {response.status_code}")
                    
                    # Return the response from the signal endpoint
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code
                    )
            except Exception as forward_error:
                self.logger.error(f"Error forwarding signal: {str(forward_error)}")
                return JSONResponse(
                    content={"status": "error", "message": f"Error forwarding signal: {str(forward_error)}"},
                    status_code=500
                )
            
        except Exception as e:
            self.logger.error(f"Error processing signal webhook: {str(e)}")
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
            
    async def register_routes(self, app: FastAPI):
        """Register webhook routes to the FastAPI app"""
        
        @app.post("/webhook")
        async def webhook(request: Request):
            """Main webhook endpoint"""
            return await self.handle_webhook(request)
            
        @app.post("/webhook/webhook")
        async def webhook_doubled(request: Request):
            """Handle doubled webhook path"""
            self.logger.info("Received request on doubled webhook path")
            return await self.handle_webhook(request)
        
        @app.post("/signal")
        async def signal_webhook(request: Request):
            """Signal webhook endpoint"""
            self.logger.info("Received request on signal endpoint")
            return await self.handle_signal(request)
            
        self.logger.info("Webhook routes registered")
        
# Create a singleton instance
webhook_handler = WebhookHandler() 
