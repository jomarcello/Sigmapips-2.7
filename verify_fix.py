#!/usr/bin/env python3
"""
Script to verify that the fix_analyze_button.py script made the necessary changes to the main.py file.
"""

import os
import re
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def verify_fix():
    """Verify that the analyze_from_signal_callback function is correctly implemented"""
    main_py_path = os.path.join("trading_bot", "main.py")
    
    if not os.path.exists(main_py_path):
        logger.error(f"File not found: {main_py_path}")
        return False
    
    # Read the file content
    with open(main_py_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the analyze_from_signal_callback function is registered
    register_handlers_pattern = r"def _register_handlers\(self, application\):.*?# Signal from analysis.*?application\.add_handler\(CallbackQueryHandler\(self\.analyze_from_signal_callback, pattern=\"\^analyze_from_signal_.*?\$\"\)\)"
    
    if not re.search(register_handlers_pattern, content, re.DOTALL):
        logger.error("analyze_from_signal_callback is not properly registered in _register_handlers")
        return False
    else:
        logger.info("analyze_from_signal_callback is properly registered in _register_handlers")
    
    # Check if the analyze_from_signal_callback function has query.answer()
    callback_pattern = r"async def analyze_from_signal_callback\(self, update: Update, context=None\) -> int:.*?query = update.callback_query\s+await query\.answer\(\)"
    
    if not re.search(callback_pattern, content, re.DOTALL):
        logger.error("analyze_from_signal_callback does not have query.answer()")
        return False
    else:
        logger.info("analyze_from_signal_callback has query.answer()")
    
    # Check if the process_signal function has the correct callback data format
    process_signal_pattern = r"keyboard = \[\s+\[InlineKeyboardButton\(\"🔍 Analyze Market\", callback_data=f\"analyze_from_signal_{instrument}_{signal_id}\"\)\]"
    
    if not re.search(process_signal_pattern, content, re.DOTALL):
        logger.error("process_signal function does not have the correct callback data format")
        return False
    else:
        logger.info("process_signal function has the correct callback data format")
    
    logger.info("All checks passed! The fix was applied successfully.")
    return True

def main():
    """Main function"""
    logger.info("Starting verification of 'Analyze Market' button fix")
    
    success = verify_fix()
    
    if success:
        logger.info("Verification completed successfully!")
        return 0
    else:
        logger.error("Verification failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 