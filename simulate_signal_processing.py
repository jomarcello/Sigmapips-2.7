#!/usr/bin/env python3
"""
Simulate signal processing without requiring the Telegram bot token
"""

import json
import logging
import argparse
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_signal_message(signal_data):
    """Format a trading signal for display in Telegram"""
    try:
        # Extract signal data with defaults
        instrument = signal_data.get("instrument", "Unknown")
        direction = signal_data.get("direction", "Unknown").upper()
        entry_price = signal_data.get("entry") or signal_data.get("price", "Unknown")
        stop_loss = signal_data.get("stop_loss") or signal_data.get("sl", "Unknown")
        take_profit = signal_data.get("take_profit") or signal_data.get("tp1", "Unknown")
        timeframe = signal_data.get("timeframe", "Unknown")
        
        # Get multiple take profit levels
        tp1 = signal_data.get("tp1", take_profit)
        tp2 = signal_data.get("tp2")
        tp3 = signal_data.get("tp3")
        
        # Add emoji based on direction
        direction_emoji = "🟢" if direction.upper() == "BUY" else "🔴"
        
        # Format the message with multiple take profits if available
        message = f"<b>🎯 New Trading Signal 🎯</b>\n\n"
        message += f"<b>Instrument:</b> {instrument}\n"
        message += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
        message += f"<b>Entry Price:</b> {entry_price}\n"
        
        if stop_loss:
            message += f"<b>Stop Loss:</b> {stop_loss} 🔴\n"
        
        # Add take profit levels
        if tp1:
            message += f"<b>Take Profit 1:</b> {tp1} 🎯\n"
        if tp2:
            message += f"<b>Take Profit 2:</b> {tp2} 🎯\n"
        if tp3:
            message += f"<b>Take Profit 3:</b> {tp3} 🎯\n"
        
        message += f"\n<b>Timeframe:</b> {timeframe}\n"
        message += f"<b>Strategy:</b> TradingView Signal\n\n"
        
        message += "————————————————————\n\n"
        message += "<b>Risk Management:</b>\n"
        message += "• Position size: 1-2% max\n"
        message += "• Use proper stop loss\n"
        
        return message
    except Exception as e:
        logger.error(f"Error formatting signal: {str(e)}")
        raise

def simulate_signal_processing(instrument, direction, entry, stop_loss, take_profit, timeframe="15"):
    """Simulate processing a trading signal"""
    
    # Create signal data
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
            signal_data["tp2"] = str(round(entry_value + 1.5 * tp_diff, 5))
            signal_data["tp3"] = str(round(entry_value + 2.0 * tp_diff, 5))
        else:
            # For SELL signals, TPs should be below entry in descending order
            tp_diff = abs(entry_value - tp_value)
            signal_data["tp2"] = str(round(entry_value - 1.5 * tp_diff, 5))
            signal_data["tp3"] = str(round(entry_value - 2.0 * tp_diff, 5))
    
    # Log the signal data
    logger.info(f"Signal data: {json.dumps(signal_data, indent=2)}")
    
    # Format the signal message
    formatted_message = format_signal_message(signal_data)
    
    # Display the formatted message
    print("\n" + "=" * 50)
    print("FORMATTED SIGNAL MESSAGE:")
    print("=" * 50)
    print(formatted_message)
    print("=" * 50 + "\n")
    
    # Create the callback data for the "Analyze Market" button
    analyze_callback_data = f"analyze_from_signal_{instrument}_{instrument}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.info(f"Analyze Market button callback data: {analyze_callback_data}")
    
    return {
        "status": "success",
        "signal_data": signal_data,
        "formatted_message": formatted_message,
        "analyze_callback_data": analyze_callback_data
    }

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Simulate signal processing")
    parser.add_argument("--instrument", default="EURUSD", help="Trading instrument")
    parser.add_argument("--direction", default="BUY", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--entry", default="1.0850", help="Entry price")
    parser.add_argument("--stop-loss", default="1.0800", help="Stop loss price")
    parser.add_argument("--take-profit", default="1.0900", help="Take profit price")
    parser.add_argument("--timeframe", default="15", help="Timeframe in minutes")
    
    args = parser.parse_args()
    
    # Run the simulation
    result = simulate_signal_processing(
        args.instrument,
        args.direction,
        args.entry,
        args.stop_loss,
        args.take_profit,
        args.timeframe
    )
    
    if result["status"] == "success":
        logger.info("✅ Signal processing simulation successful!")
    else:
        logger.error("❌ Signal processing simulation failed")

if __name__ == "__main__":
    main() 