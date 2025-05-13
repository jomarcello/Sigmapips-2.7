#!/usr/bin/env python3
"""
Script to send test signals using the Telegram bot token
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot token provided by the user
BOT_TOKEN = "7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk"

# Test user ID (replace with your own Telegram user ID)
TEST_USER_ID = None  # Will be set when the bot starts

async def format_signal_message(signal_data):
    """Format signal data into a nice message"""
    try:
        # Extract fields from signal data
        instrument = signal_data.get('instrument', 'Unknown')
        direction = signal_data.get('direction', 'Unknown')
        entry = signal_data.get('entry', 'Unknown')
        stop_loss = signal_data.get('stop_loss')
        timeframe = signal_data.get('timeframe', '1h')
        
        # Get multiple take profit levels if available
        tp1 = signal_data.get('tp1', signal_data.get('take_profit'))
        tp2 = signal_data.get('tp2')
        tp3 = signal_data.get('tp3')
        
        # Add emoji based on direction
        direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
        
        # Format the message with multiple take profits if available
        message = f"🎯 New Trading Signal 🎯\n\n"
        message += f"Instrument: {instrument}\n"
        message += f"Action: {direction.upper()} {direction_emoji}\n\n"
        message += f"Entry Price: {entry}\n"
        
        if stop_loss:
            message += f"Stop Loss: {stop_loss} 🔴\n"
        
        # Add take profit levels
        if tp1:
            message += f"Take Profit 1: {tp1} 🎯\n"
        if tp2:
            message += f"Take Profit 2: {tp2} 🎯\n"
        if tp3:
            message += f"Take Profit 3: {tp3} 🎯\n"
        
        message += f"\nTimeframe: {timeframe}\n"
        message += f"Strategy: Breakout Strategy\n\n"
        
        message += "————————————————————\n\n"
        message += "Risk Management:\n"
        message += "• Position size: 1-2% max\n"
        message += "• Use proper stop loss\n"
        message += "• Follow your trading plan\n\n"
        
        message += "————————————————————\n\n"
        
        # Generate AI verdict
        ai_verdict = f"The {instrument} {direction.lower()} signal shows a promising setup with defined entry at {entry} and stop loss at {stop_loss}. Multiple take profit levels provide opportunities for partial profit taking."
        message += f"🤖 SigmaPips AI Verdict:\n{ai_verdict}"
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting signal message: {str(e)}")
        # Return simple message on error
        return f"New {signal_data.get('instrument', 'Unknown')} {signal_data.get('direction', 'Unknown')} Signal"

def create_test_signal(instrument, direction, entry, stop_loss, take_profit, timeframe="15"):
    """Create a test signal"""
    
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
    
    return signal_data

async def send_test_signal(bot, chat_id, instrument, direction, entry, stop_loss, take_profit, timeframe="15"):
    """Send a test signal to a chat"""
    try:
        # Create the test signal
        signal_data = create_test_signal(instrument, direction, entry, stop_loss, take_profit, timeframe)
        
        # Format the signal message
        message = await format_signal_message(signal_data)
        
        # Create a unique signal ID
        timestamp = int(datetime.now().timestamp())
        signal_id = f"{direction}_{timeframe}_{timestamp}"
        
        # Create analyze button with correct callback data format
        # The format should be: analyze_from_signal_INSTRUMENT_SIGNALID
        keyboard = [
            [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
        ]
        
        # Send the message with the button
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        logger.info(f"✅ Test signal sent to chat {chat_id}")
        logger.info(f"✅ Signal ID: {signal_id}")
        logger.info(f"✅ Callback data: analyze_from_signal_{instrument}_{signal_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error sending test signal: {str(e)}")
        return False

async def send_multiple_test_signals():
    """Send multiple test signals"""
    try:
        # Initialize the bot
        bot = Bot(token=BOT_TOKEN)
        
        # Get bot information and user ID
        bot_info = await bot.get_me()
        logger.info(f"Bot initialized: @{bot_info.username}")
        
        # Get updates to find user ID if not set
        global TEST_USER_ID
        if not TEST_USER_ID:
            updates = await bot.get_updates(limit=10)
            if updates:
                # Use the user ID from the most recent update
                for update in reversed(updates):
                    if update.message and update.message.from_user:
                        TEST_USER_ID = update.message.from_user.id
                        logger.info(f"Found user ID from updates: {TEST_USER_ID}")
                        break
        
        if not TEST_USER_ID:
            logger.warning("No user ID found in updates. Please send a message to the bot first.")
            logger.info("Continuing with sending signals to the bot directly for testing...")
            # For testing, you can set a specific chat ID here
            TEST_USER_ID = bot_info.id
        
        # Test signals to send
        test_signals = [
            {
                "instrument": "GBPUSD", 
                "direction": "BUY", 
                "entry": "1.2650", 
                "stop_loss": "1.2600", 
                "take_profit": "1.2700", 
                "timeframe": "1H"
            },
            {
                "instrument": "EURUSD", 
                "direction": "BUY", 
                "entry": "1.0850", 
                "stop_loss": "1.0800", 
                "take_profit": "1.0900", 
                "timeframe": "4H"
            },
            {
                "instrument": "USDJPY", 
                "direction": "SELL", 
                "entry": "154.500", 
                "stop_loss": "155.000", 
                "take_profit": "154.000", 
                "timeframe": "15M"
            }
        ]
        
        # Send each test signal
        for signal in test_signals:
            success = await send_test_signal(
                bot, 
                TEST_USER_ID, 
                signal["instrument"], 
                signal["direction"], 
                signal["entry"], 
                signal["stop_loss"], 
                signal["take_profit"], 
                signal["timeframe"]
            )
            
            if success:
                logger.info(f"✅ Successfully sent {signal['instrument']} {signal['direction']} signal")
            else:
                logger.error(f"❌ Failed to send {signal['instrument']} {signal['direction']} signal")
            
            # Wait a bit between signals
            await asyncio.sleep(1)
        
        logger.info("✅ All test signals sent successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in send_multiple_test_signals: {str(e)}")

def main():
    """Main entry point for the script"""
    asyncio.run(send_multiple_test_signals())

if __name__ == "__main__":
    main() 