#!/usr/bin/env python3
"""
Script to update the button_callback method in telegram_service/bot.py to ensure it properly handles signal flow callbacks.

This script:
1. Finds the button_callback method in telegram_service/bot.py
2. Updates it to properly handle signal flow callbacks
3. Ensures proper separation between menu flow and signal flow
"""

import re
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Constants
BOT_PY_PATH = 'trading_bot/services/telegram_service/bot.py'
BACKUP_SUFFIX = f".backup_button_callback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def backup_file(file_path):
    """Create a backup of the file before making changes"""
    backup_path = file_path + BACKUP_SUFFIX
    try:
        with open(file_path, 'r', encoding='utf-8') as source_file:
            content = source_file.read()
        
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        
        logger.info(f"Created backup at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return False

def fix_button_callback():
    """Fix the button_callback method to use the flow manager and handler dispatcher"""
    with open('trading_bot/main.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create a backup first
    with open('trading_bot/main.py.backup_button_callback_new', 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Find the button_callback method
    start_marker = "async def button_callback(self, update, context):"
    start_index = content.find(start_marker)
    
    if start_index == -1:
        print("Could not find button_callback method")
        return
    
    # Find the end of the method - look for the next async def
    next_method = content.find("async def", start_index + len(start_marker))
    if next_method == -1:
        print("Could not find the end of button_callback method")
        return
    
    # Extract the button_callback method
    button_callback = content[start_index:next_method]
    
    # Create the updated button_callback method
    updated_button_callback = '''async def button_callback(self, update, context):
        """
        Handle all button callbacks that don't match a specific pattern
        This method will use the FlowManager and HandlerDispatcher to route
        callbacks to the appropriate handler based on the current flow.
        """
        try:
            # Import flow utilities
            from trading_bot.utils.flow_manager import FlowManager, FlowType
            from trading_bot.utils.handler_dispatcher import HandlerDispatcher
            
            query = update.callback_query
            user_id = update.effective_user.id
            callback_data = query.data
            
            # Log the callback
            logger.info(f"Callback button pressed by user {user_id}: {callback_data}")
            
            # Try to dispatch using the HandlerDispatcher
            handled = await HandlerDispatcher.dispatch_callback(update, context, self)
            if handled:
                return
                
            # If not handled by the dispatcher, use the fallback logic
            # Answer the callback query
            await query.answer()
            
            # Log the callback data and user context for debugging
            if hasattr(context, 'user_data'):
                logger.info(f"User context: {context.user_data}")
            
            # Fallback message for unhandled callbacks
            await update.effective_message.edit_text(
                "This button is not currently active or under maintenance. "
                "Please try another option or use /menu to return to the main menu.",
                reply_markup=None
            )
            
            logger.warning(f"Unhandled callback data: {callback_data}")
            
        except Exception as e:
            logger.error(f"Error in button_callback: {str(e)}")
            logger.exception(e)
            try:
                await update.effective_message.edit_text(
                    "An error occurred while processing your request. "
                    "Please try again or use /menu to return to the main menu.",
                    reply_markup=None
                )
            except Exception as reply_e:
                logger.error(f"Could not send error message: {str(reply_e)}")
    '''
    
    # Replace the old method with the updated one
    fixed_content = content[:start_index] + updated_button_callback + content[next_method:]
    
    # Write the fixed content back to the file
    with open('trading_bot/main.py', 'w', encoding='utf-8') as file:
        file.write(fixed_content)
    
    print("Fixed button_callback method")

if __name__ == "__main__":
    fix_button_callback() 