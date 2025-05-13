#!/usr/bin/env python3
"""
Script to fix the "Analyze Market" button functionality in the signal page.
This script will modify the trading_bot/main.py file to ensure the analyze_from_signal_callback
function is correctly registered and the callback data is properly formatted.
"""

import os
import re
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of the file before modifying it"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.{timestamp}.bak"
    shutil.copy2(file_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    return backup_path

def fix_analyze_from_signal_callback():
    """Fix the analyze_from_signal_callback function in main.py"""
    main_py_path = os.path.join("trading_bot", "main.py")
    
    if not os.path.exists(main_py_path):
        logger.error(f"File not found: {main_py_path}")
        return False
    
    # Create a backup of the file
    backup_file(main_py_path)
    
    # Read the file content
    with open(main_py_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the analyze_from_signal_callback function is registered
    register_handlers_pattern = r"(def _register_handlers\(self, application\):.*?# Signal from analysis.*?application\.add_handler\(CallbackQueryHandler\(self\.analyze_from_signal_callback, pattern=\"\^analyze_from_signal_.*?\$\"\)\))"
    
    if not re.search(register_handlers_pattern, content, re.DOTALL):
        logger.warning("Could not find the analyze_from_signal_callback registration in _register_handlers")
        
        # Add the registration if not found
        register_handlers_match = re.search(r"(def _register_handlers\(self, application\):.*?# Signal analysis flow handlers.*?)(\n\s+# Ensure back_instrument)", content, re.DOTALL)
        
        if register_handlers_match:
            replacement = f"{register_handlers_match.group(1)}\n            # Signal from analysis\n            application.add_handler(CallbackQueryHandler(self.analyze_from_signal_callback, pattern=\"^analyze_from_signal_.*$\"))\n{register_handlers_match.group(2)}"
            content = content.replace(register_handlers_match.group(0), replacement)
            logger.info("Added analyze_from_signal_callback registration to _register_handlers")
    
    # Check and fix the analyze_from_signal_callback function
    callback_pattern = r"(async def analyze_from_signal_callback\(self, update: Update, context=None\) -> int:.*?return MENU)"
    callback_match = re.search(callback_pattern, content, re.DOTALL)
    
    if callback_match:
        # Add query.answer() at the beginning of the function
        callback_content = callback_match.group(1)
        if "await query.answer()" not in callback_content:
            modified_callback = callback_content.replace(
                "query = update.callback_query\n",
                "query = update.callback_query\n        await query.answer()  # Acknowledge the callback query\n"
            )
            content = content.replace(callback_content, modified_callback)
            logger.info("Added query.answer() to analyze_from_signal_callback")
    else:
        logger.error("Could not find analyze_from_signal_callback function")
        return False
    
    # Check and fix the process_signal function to ensure correct callback data format
    process_signal_pattern = r"(# Prepare keyboard with analysis options.*?keyboard = \[.*?\[InlineKeyboardButton\(\"🔍 Analyze Market\", callback_data=f\"analyze_from_signal_.*?\"\)\].*?\])"
    process_signal_matches = re.findall(process_signal_pattern, content, re.DOTALL)
    
    for match in process_signal_matches:
        if "callback_data=f\"analyze_from_signal_{instrument}_{signal_id}\"" not in match:
            modified_match = match.replace(
                "callback_data=f\"analyze_from_signal_{instrument}\"",
                "callback_data=f\"analyze_from_signal_{instrument}_{signal_id}\""
            )
            content = content.replace(match, modified_match)
            logger.info("Fixed callback_data format in process_signal function")
    
    # Write the modified content back to the file
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info("Successfully fixed analyze_from_signal_callback function and its registration")
    return True

def main():
    """Main function"""
    logger.info("Starting fix for 'Analyze Market' button functionality")
    
    success = fix_analyze_from_signal_callback()
    
    if success:
        logger.info("Fix completed successfully!")
        return 0
    else:
        logger.error("Fix failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 