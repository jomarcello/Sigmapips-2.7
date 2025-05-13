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

class SignalHandler:
    """Handler for trading signals"""
    
    def __init__(self):
        """Initialize the signal handler"""
        self.logger = logging.getLogger(__name__)
    
    def format_signal(self, signal_data):
        """Format a trading signal for display in Telegram"""
        try:
            # Extract signal data with defaults
            instrument = signal_data.get("instrument", "Unknown")
            direction = signal_data.get("direction", "Unknown").upper()
            entry_price = signal_data.get("entry_price")
            stop_loss = signal_data.get("stop_loss")
            take_profit = signal_data.get("take_profit", [])
            timeframe = signal_data.get("timeframe", "Unknown")
            strategy = signal_data.get("strategy", "Unknown")
            risk_reward = signal_data.get("risk_reward", 0)
            risk_percentage = signal_data.get("risk_percentage", 1)
            ai_verdict = signal_data.get("ai_verdict", "No AI analysis available")
            
            # Validate required fields
            if not all([instrument, direction, entry_price, stop_loss]):
                raise ValueError("Missing required signal data")
                
            # Ensure take_profit is a list
            if not isinstance(take_profit, list):
                take_profit = [take_profit]
                
            # Format the signal message
            if direction == "BUY":
                signal_emoji = "🟢"
                # For BUY signals, take profits should be above entry price in ascending order
                take_profit = sorted(take_profit)
            elif direction == "SELL":
                signal_emoji = "🔴"
                # For SELL signals, take profits should be below entry price in descending order
                take_profit = sorted(take_profit, reverse=True)
            else:
                signal_emoji = "⚪"
            
            # Format prices with appropriate precision
            def format_price(price):
                if instrument.endswith("JPY"):
                    return f"{price:.3f}"
                return f"{price:.5f}"
            
            # Build the signal message
            message = f"{signal_emoji} *{instrument} {direction} SIGNAL* {signal_emoji}\n\n"
            
            # Entry and SL
            message += f"*Entry Price:* {format_price(entry_price)}\n"
            message += f"*Stop Loss:* {format_price(stop_loss)}\n\n"
            
            # Take profit levels
            message += "*Take Profit Levels:*\n"
            for i, tp in enumerate(take_profit, 1):
                message += f"TP{i}: {format_price(tp)}\n"
            
            # Additional info
            message += f"\n*Timeframe:* {timeframe}\n"
            message += f"*Strategy:* {strategy}\n"
            message += f"*Risk/Reward:* {risk_reward:.1f}\n"
            message += f"*Risk %:* {risk_percentage:.1f}%\n\n"
            
            # AI analysis
            message += f"*AI Analysis:*\n{ai_verdict}\n\n"
            
            # Risk management reminder
            message += "⚠️ *Risk Management:* Always use proper position sizing and risk management."
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error formatting signal: {str(e)}")
            raise
    
    async def process_signal(self, signal_data):
        """Process a trading signal"""
        try:
            # Format the signal for display
            formatted_signal = self.format_signal(signal_data)
            
            # Here you would typically send the formatted signal to users
            # For now, we'll just return it
            return {
                "status": "success",
                "formatted_signal": formatted_signal
            }
        except Exception as e:
            self.logger.error(f"Error processing signal: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

class WebhookHandler:
    """Handler for Telegram webhooks"""
    
    def __init__(self):
        """Initialize the webhook handler"""
        self.logger = logging.getLogger(__name__)
        # Get the base URL for internal communication, default to the new production URL
        self.base_url = os.environ.get("INTERNAL_API_URL", "https://sigmapips-27-production.up.railway.app")
        self.logger.info(f"Using internal API URL: {self.base_url}")
        # Initialize the signal handler
        self.signal_handler = SignalHandler()
    
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
            
            # Process the signal
            result = await self.signal_handler.process_signal(data)
            
            # Return the result
            return JSONResponse(content=result, status_code=200 if result["status"] == "success" else 400)
            
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
