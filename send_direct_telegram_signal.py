#!/usr/bin/env python3
"""
Send a test signal directly to the Telegram bot using the provided token
"""

import logging
import argparse
from datetime import datetime
import json
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def send_direct_signal(token, chat_id, instrument, direction, entry, stop_loss, take_profit, timeframe="15"):
    """Send a test signal directly to the Telegram bot"""
    try:
        # Create the bot instance
        bot = Bot(token=token)
        
        # Get bot information to verify token
        bot_info = await bot.get_me()
        logger.info(f"Connected to bot: {bot_info.first_name} (@{bot_info.username})")
        
        # Create signal data
        signal_id = f"{instrument}_{direction}_{timeframe}_{int(datetime.now().timestamp())}"
        
        # Format the signal message
        message = format_signal_message(instrument, direction, entry, stop_loss, take_profit, timeframe)
        
        # Create the inline keyboard with the analyze button
        keyboard = [
            [InlineKeyboardButton(text="🔍 Analyze Market", callback_data=f"analyze_from_signal_{instrument}_{signal_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send the message
        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        logger.info(f"Signal sent successfully to chat ID {chat_id}, message ID: {sent_message.message_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending signal: {str(e)}")
        return False

def format_signal_message(instrument, direction, entry, stop_loss, take_profit, timeframe):
    """Format a trading signal for display in Telegram"""
    # Add emoji based on direction
    direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
    
    # Calculate additional take profit levels
    entry_value = float(entry)
    tp_value = float(take_profit)
    tp_diff = abs(tp_value - entry_value)
    
    if direction.upper() == "BUY":
        tp2 = str(round(entry_value + 1.5 * tp_diff, 5))
        tp3 = str(round(entry_value + 2.0 * tp_diff, 5))
    else:
        tp2 = str(round(entry_value - 1.5 * tp_diff, 5))
        tp3 = str(round(entry_value - 2.0 * tp_diff, 5))
    
    # Format the message
    message = f"<b>🎯 New Trading Signal 🎯</b>\n\n"
    message += f"<b>Instrument:</b> {instrument}\n"
    message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
    message += f"<b>Entry Price:</b> {entry}\n"
    message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
    message += f"<b>Take Profit 1:</b> {take_profit} 🎯\n"
    message += f"<b>Take Profit 2:</b> {tp2} 🎯\n"
    message += f"<b>Take Profit 3:</b> {tp3} 🎯\n"
    message += f"\n<b>Timeframe:</b> {timeframe}\n"
    message += f"<b>Strategy:</b> TradingView Signal\n\n"
    message += "————————————————————\n\n"
    message += "<b>Risk Management:</b>\n"
    message += "• Position size: 1-2% max\n"
    message += "• Use proper stop loss\n"
    
    return message

async def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Send a test signal directly to the Telegram bot")
    parser.add_argument("--token", default="7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk", help="Telegram bot token")
    parser.add_argument("--chat-id", required=True, help="Chat ID to send the signal to")
    parser.add_argument("--instrument", default="EURUSD", help="Trading instrument")
    parser.add_argument("--direction", default="BUY", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--entry", default="1.0850", help="Entry price")
    parser.add_argument("--stop-loss", default="1.0800", help="Stop loss price")
    parser.add_argument("--take-profit", default="1.0900", help="Take profit price")
    parser.add_argument("--timeframe", default="15", help="Timeframe in minutes")
    
    args = parser.parse_args()
    
    # Send the signal
    success = await send_direct_signal(
        args.token,
        args.chat_id,
        args.instrument,
        args.direction,
        args.entry,
        args.stop_loss,
        args.take_profit,
        args.timeframe
    )
    
    if success:
        logger.info("✅ Signal sent successfully!")
    else:
        logger.error("❌ Failed to send signal")

if __name__ == "__main__":
    asyncio.run(main()) 