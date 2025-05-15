# Analyze Market Button Fix

## Problem
The "Analyze Market" button in the Telegram bot did not work properly. When users clicked on the button from a signal notification, they would see analysis options but clicking on them did not work correctly.

## Root Cause
The main issues were:

1. The `analyze_from_signal_callback` method used a generic keyboard (`SIGNAL_ANALYSIS_KEYBOARD`) that didn't include proper instrument-specific callbacks.
2. The button callbacks for signal flow analysis (technical, sentiment) were not properly implemented to handle the instrument parameter from the callback data.
3. The button_callback method didn't properly extract the instrument from signal flow callbacks.

## Solution

The fix includes the following changes:

1. Updated the `analyze_from_signal_callback` method to:
   - Create a custom keyboard with instrument-specific callbacks:
     ```python
     keyboard = [
         [InlineKeyboardButton("📈 Technical Analysis", callback_data=f"signal_technical_{instrument}")],
         [InlineKeyboardButton("🧠 Market Sentiment", callback_data=f"signal_sentiment_{instrument}")],
         [InlineKeyboardButton("📅 Economic Calendar", callback_data=f"signal_calendar_{instrument}")],
         [InlineKeyboardButton("⬅️ Back to Signal", callback_data="back_to_signal")]
     ]
     ```
   - Improved the display message for better user experience.

2. Updated the `button_callback` method to handle the new callback patterns:
   - Added handlers for `signal_technical_INSTRUMENT` callbacks
   - Added handlers for `signal_sentiment_INSTRUMENT` callbacks
   - Ensured `signal_calendar_INSTRUMENT` callbacks are properly handled

## How to Apply the Fix

1. Run the fix script:
   ```
   python fix_analyze_market_button.py
   ```

2. Test the functionality using the test script:
   ```
   python test_analyze_market.py
   ```

3. If needed, you can restore the original file from the backup created at `trading_bot/main.py.analyze_market_backup`.

## Testing

The fix has been tested with:

1. Simulated analyze market button clicks
2. Simulated technical and sentiment analysis clicks from the analyze market menu

After this fix is applied, the analyze market button should work properly, allowing users to perform technical analysis, sentiment analysis, and check economic calendar data for any instrument from signal notifications. 