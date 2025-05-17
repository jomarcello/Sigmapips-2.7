# Flow Management Solution

## Problem Overview
The Telegram bot had issues identifying which flow a user was in at any given time, particularly with confusion between the `/menu` flow and the `signal` flow. Both flows sometimes used the same handlers, leading to inconsistencies and bugs in the user experience.

## Solution
We've implemented a centralized flow management system that clearly tracks which flow the user is in at all times and ensures proper handler dispatching based on the flow context.

### Components

1. **FlowManager (`trading_bot/utils/flow_manager.py`)**
   - Centralized state management for user flows
   - Defines clear enum types for different flows (MENU, SIGNAL, etc.)
   - Handles setting, getting, and resetting flow states
   - Maintains backward compatibility with legacy flow flags

2. **HandlerDispatcher (`trading_bot/utils/handler_dispatcher.py`)**
   - Routes callbacks to the appropriate handlers based on the current flow
   - Extracts embedded data (like instrument) from callback patterns
   - Uses flow-specific dispatching logic while maintaining fallback mechanisms
   - Prevents callbacks in one flow from triggering handlers in another flow

3. **Updated Button Callback (`fix_button_callback.py`)**
   - Replaces the old `button_callback` method with a flow-aware version
   - Uses HandlerDispatcher to route callbacks based on the current flow
   - Provides clearer error handling and logging

4. **Flow Initialization (`flow_init_fix.py`)**
   - Updates key flow entry points (menu_command, analyze_from_signal_callback)
   - Sets appropriate flow context with relevant metadata
   - Ensures consistent flow state across the application

## How It Works

1. **Flow Entry Points**
   - When a user enters a flow (e.g., via `/menu` or clicking "Analyze Market"), the flow is set using:
     ```python
     FlowManager.set_flow(context, FlowType.MENU)  # or FlowType.SIGNAL
     ```

2. **Flow-specific Routing**
   - All callbacks are dispatched through the HandlerDispatcher, which checks:
     ```python
     current_flow = FlowManager.get_current_flow(context)
     ```
   - Then routes to the appropriate handler based on the flow.

3. **Callback Handling**
   - The dispatcher recognizes patterns like `signal_flow_technical_EURUSD` and extracts:
     - The flow (signal_flow)
     - The action (technical)
     - The instrument (EURUSD)
   - It then stores the instrument in the context and calls the proper handler.

## Advantages of This Approach

1. **Clear Separation of Concerns**
   - Each flow's logic is now clearly separated and won't interfere with other flows.

2. **Consistent User Experience**
   - Back buttons will correctly navigate within the current flow.
   - Analysis options will properly maintain context of the current instrument/signal.

3. **Maintainability**
   - Flow-specific logic is centralized in the HandlerDispatcher.
   - Adding new flows requires minimal changes (just add a new FlowType enum and dispatcher method).

4. **Debugging**
   - Comprehensive logging clearly shows which flow a user is in and how callbacks are being routed.
   - Flow state is clearly maintained in the user context.

## Implementation Steps

1. Create the utility files in `trading_bot/utils/`:
   - `flow_manager.py`
   - `handler_dispatcher.py`

2. Run the fix scripts in order:
   - `python flow_init_fix.py` (updates flow entry points)
   - `python fix_button_callback.py` (updates callback routing)

3. Test the bot by manually going through both flows:
   - `/menu` flow (Menu → Analyze Markets → Select Market → Select Instrument → Analysis options)
   - Signal flow (receive signal → click "Analyze Market" → Analysis options)

## Usage Example

```python
# Setting a flow with metadata
from trading_bot.utils.flow_manager import FlowManager, FlowType

# When user enters the signal flow
metadata = {'signal_id': '12345', 'instrument': 'EURUSD'}
FlowManager.set_flow(context, FlowType.SIGNAL, metadata)

# Checking the current flow
if FlowManager.is_in_flow(context, FlowType.SIGNAL):
    # Do signal flow specific actions
    pass
``` 