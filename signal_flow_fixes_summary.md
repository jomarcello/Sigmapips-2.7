# Signal Flow Fixes Summary

## Problem Description
The Telegram bot has two separate flows:

1. **Menu Flow** - Accessed via the `/menu` command, allowing users to select services, markets, and instruments
2. **Signal Flow** - Triggered by the "Analyze Market" button when a signal arrives, specific to the instrument in the signal

These flows were overlapping due to:
1. Missing proper flag setting in the `back_to_signal_callback` method
2. Lack of proper routing for signal flow callbacks in the `button_callback` method

## Fixes Applied

### 1. Fixed `back_to_signal_callback` in main.py
- Added proper setting of both signal flow flags:
  ```python
  context.user_data['from_signal'] = True
  context.user_data['in_signal_flow'] = True
  ```
- Fixed indentation issues in the try/except blocks
- Removed duplicate implementation of the method

### 2. Updated `button_callback` in telegram_service/bot.py
- Added specific handling for signal flow callbacks:
  ```python
  # Check if we're in signal flow and handle accordingly
  if context and hasattr(context, 'user_data') and context.user_data.get('in_signal_flow', False):
      # Handle signal flow technical analysis
      if callback_data.startswith("signal_flow_technical_"):
          parts = callback_data.split("_")
          if len(parts) >= 4:
              instrument = parts[3]  # Extract instrument from callback data
              logger.info(f"Routing signal flow technical analysis for instrument: {instrument}")
              if context and hasattr(context, 'user_data'):
                  context.user_data['instrument'] = instrument
              return await self.signal_technical_callback(update, context)
      
      # Handle signal flow sentiment analysis
      elif callback_data.startswith("signal_flow_sentiment_"):
          # Similar handling for sentiment analysis
          ...
      
      # Handle signal flow calendar analysis
      elif callback_data.startswith("signal_flow_calendar_"):
          # Similar handling for calendar analysis
          ...
  ```

## How the Fix Works

### Signal Flow Context Flags
Two flags are now properly maintained throughout the flow:
1. `from_signal` - Indicates the user came from a signal
2. `in_signal_flow` - Indicates the user is currently in the signal flow

### Signal Flow Handling
When a user is in the signal flow:
1. The `in_signal_flow` flag is set to `True`
2. Signal-specific callbacks (like `signal_flow_technical_EURUSD`) are properly routed
3. The instrument is extracted from the callback data and stored in the context
4. Back buttons return to the signal rather than to the instrument selection

## Testing
To verify the fix:
1. Start the bot and use the `/menu` command to access the menu flow
2. Wait for a signal and click "Analyze Market" to access the signal flow
3. Verify that the back buttons in each flow return to the appropriate screens
4. Ensure that moving between technical analysis, sentiment analysis, and calendar in the signal flow maintains the correct context

## Conclusion
These fixes ensure that the menu flow and signal flow remain properly separated, providing a consistent user experience regardless of how the user accesses the bot's features. 