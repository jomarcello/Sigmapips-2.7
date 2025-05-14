# Telegram Bot Flow Separation Implementation

## Overview
We've successfully implemented separate flows for the Telegram bot:

1. **`/menu` Flow** - Accessed via the /menu command, allowing users to select services and instruments/markets
2. **Signal Flow** - Triggered by "Analyze Market" button when a signal arrives

## Changes Made

### 1. Signal Flow Handlers
- Added dedicated signal flow handlers for technical analysis, market sentiment, and economic calendar
- These handlers are triggered by callback data with the pattern `signal_flow_*_INSTRUMENT`
- Example: `signal_flow_technical_EURUSD`

### 2. Context Management
- Added flags in the context to track whether we're in the signal flow:
  - `from_signal`: Indicates the analysis was initiated from a signal
  - `in_signal_flow`: Indicates we're in the signal flow
- These flags are set when entering signal flow and reset when exiting

### 3. Button Callback Routing
- Updated the `button_callback` method to properly route signal flow callbacks to the appropriate handlers
- Added specific handling for `signal_flow_technical_*`, `signal_flow_sentiment_*`, and `signal_flow_calendar_*` patterns

### 4. Handler Registration
- Ensured that signal flow handlers are properly registered with the correct patterns
- Added dedicated handlers for signal flow patterns in the `_register_handlers` method

### 5. Back Button Handling
- Updated the back button handling to return to the signal when in signal flow
- Different back button behavior based on the flow:
  - In signal flow: Back button returns to signal
  - In regular flow: Back button returns to instrument selection

### 6. Analyze From Signal
- Updated the `analyze_from_signal_callback` to set the appropriate flags
- Uses signal-specific keyboard with embedded instrument information
- Stores signal information in context for later use

## Testing
To test the implementation:
1. Use the `/menu` command to access the regular flow
2. Wait for a signal and click "Analyze Market" to access the signal flow
3. Verify that the back buttons in each flow return to the appropriate screens
4. Verify that the analysis options in each flow work correctly

## Conclusion
These changes ensure that the two flows remain completely separate, with no overlapping handlers or buttons. The bot now correctly maintains separate state for each flow and provides appropriate navigation options based on the current flow. 