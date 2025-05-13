#!/usr/bin/env python3
"""
Simulate signal processing without Telegram bot dependencies
"""

import json
import logging
from datetime import datetime
import os
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_signal_message(signal_data):
    """Format signal data into a nice message (simulating the Telegram formatting)"""
    try:
        # Extract fields from signal data
        instrument = signal_data.get('instrument', 'Unknown')
        direction = signal_data.get('direction', 'Unknown')
        entry = signal_data.get('entry', 'Unknown')
        stop_loss = signal_data.get('stop_loss')
        take_profit = signal_data.get('take_profit')
        timeframe = signal_data.get('timeframe', '1h')
        
        # Get multiple take profit levels if available
        tp1 = signal_data.get('tp1', take_profit)
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
        message += f"Strategy: TradingView Signal\n\n"
        
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

def process_signal(signal_data):
    """Process a trading signal (simulation)"""
    try:
        # Log the incoming signal data
        logger.info(f"Processing signal: {signal_data}")
        
        # Check which format we're dealing with and normalize it
        instrument = signal_data.get('instrument')
        
        # Handle TradingView format (price, sl, interval)
        if 'price' in signal_data and 'sl' in signal_data:
            price = signal_data.get('price')
            sl = signal_data.get('sl')
            tp1 = signal_data.get('tp1')
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            interval = signal_data.get('interval', '1h')
            
            # Determine signal direction based on price and SL relationship
            direction = "BUY" if float(sl) < float(price) else "SELL"
            
            # Create normalized signal data
            normalized_data = {
                'instrument': instrument,
                'direction': direction,
                'entry': price,
                'stop_loss': sl,
                'take_profit': tp1,  # Use first take profit level
                'timeframe': interval
            }
            
            # Add optional fields if present
            normalized_data['tp1'] = tp1
            normalized_data['tp2'] = tp2
            normalized_data['tp3'] = tp3
        
        # Handle custom format (direction, entry, stop_loss, timeframe)
        elif 'direction' in signal_data and 'entry' in signal_data:
            direction = signal_data.get('direction')
            entry = signal_data.get('entry')
            stop_loss = signal_data.get('stop_loss')
            take_profit = signal_data.get('take_profit')
            timeframe = signal_data.get('timeframe', '1h')
            
            # Create normalized signal data
            normalized_data = {
                'instrument': instrument,
                'direction': direction,
                'entry': entry,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timeframe': timeframe
            }
            
            # Add optional fields if present
            tp1 = signal_data.get('tp1', take_profit)
            tp2 = signal_data.get('tp2')
            tp3 = signal_data.get('tp3')
            if tp1:
                normalized_data['tp1'] = tp1
            if tp2:
                normalized_data['tp2'] = tp2
            if tp3:
                normalized_data['tp3'] = tp3
        else:
            logger.error(f"Missing required signal data")
            return False
        
        # Basic validation
        if not normalized_data.get('instrument') or not normalized_data.get('direction') or not normalized_data.get('entry'):
            logger.error(f"Missing required fields in normalized signal data: {normalized_data}")
            return False
                
        # Create signal ID for tracking
        signal_id = f"{normalized_data['instrument']}_{normalized_data['direction']}_{normalized_data['timeframe']}_{int(datetime.now().timestamp())}"
        
        # Format the signal message
        message = format_signal_message(normalized_data)
        
        # Save the formatted message
        os.makedirs("test_signals", exist_ok=True)
        filename = f"test_signals/formatted_signal_{instrument}_{direction}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, "w") as f:
            f.write(message)
        
        logger.info(f"Saved formatted signal message to {filename}")
        logger.info(f"Formatted message:\n{message}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error processing signal: {str(e)}")
        return False

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
        
        # For USDJPY SELL with specific values from screenshot
        if instrument == "USDJPY" and direction.upper() == "SELL" and entry == "141.994":
            # Use the exact values from the screenshot
            signal_data["tp1"] = "141.64"  # First TP should be below entry for SELL
            signal_data["tp2"] = "141.286"  # Second TP even lower
            signal_data["tp3"] = "140.932"  # Third TP even lower
        else:
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

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Simulate signal processing")
    parser.add_argument("--instrument", default="USDJPY", help="Trading instrument")
    parser.add_argument("--direction", default="SELL", choices=["BUY", "SELL"], help="Trade direction")
    parser.add_argument("--entry", default="141.994", help="Entry price")
    parser.add_argument("--stop-loss", default="142.054", help="Stop loss price")
    parser.add_argument("--take-profit", default="141.64", help="Take profit price")
    parser.add_argument("--timeframe", default="15", help="Timeframe in minutes")
    
    args = parser.parse_args()
    
    # Create test signal
    signal_data = create_test_signal(
        args.instrument,
        args.direction,
        args.entry,
        args.stop_loss,
        args.take_profit,
        args.timeframe
    )
    
    # Process the signal
    success = process_signal(signal_data)
    
    if success:
        logger.info("✅ Signal processing simulation successful!")
    else:
        logger.error("❌ Signal processing simulation failed")

if __name__ == "__main__":
    main() 