#!/usr/bin/env python3
"""
Fix indentation error in main.py
"""

import os
import sys
import re
from pathlib import Path

def fix_indentation_error():
    """Fix indentation error in main.py"""
    # Path to the main.py file
    main_file_path = Path("trading_bot/main.py")
    
    if not main_file_path.exists():
        print(f"File not found: {main_file_path}")
        return False
    
    # Read the content of the file
    with open(main_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Create a backup of the original file
    backup_path = main_file_path.with_suffix(".py.bak")
    with open(backup_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Created backup of the original file: {backup_path}")
    
    # Fix the first indentation error (line ~1525)
    fixed_content = re.sub(
        r'    except Exception as e:\n        logger.error\(f"Error initializing Telegram service: {str\(e\)}"\)\n            raise',
        r'    except Exception as e:\n        logger.error(f"Error initializing Telegram service: {str(e)}")\n        raise',
        content
    )
    
    # Fix the second indentation error (line ~1531)
    fixed_content = re.sub(
        r'    async def initialize_services\(self\):\n        """Initialize services that require an asyncio event loop"""\n    try:',
        r'    async def initialize_services(self):\n        """Initialize services that require an asyncio event loop"""\n        try:',
        fixed_content
    )
    
    # Fix the third indentation error (in periodic_cleanup function)
    fixed_content = re.sub(
        r'                    while True:\n                    try:',
        r'                    while True:\n                        try:',
        fixed_content
    )
    
    # Fix the fourth indentation error (raise statement after initializing services)
    fixed_content = re.sub(
        r'    except Exception as e:\n        logger.error\(f"Error initializing services: {str\(e\)}"\)\n            raise',
        r'    except Exception as e:\n        logger.error(f"Error initializing services: {str(e)}")\n        raise',
        fixed_content
    )
    
    # Fix the fifth indentation error (in _format_calendar_events)
    fixed_content = re.sub(
        r'        # Sort events by time\n    try:',
        r'        # Sort events by time\n        try:',
        fixed_content
    )
    
    # Fix the sixth indentation error (in parse_time_for_sorting)
    fixed_content = re.sub(
        r'                time_str = event.get\(\'time\', \'\'\)\n            try:',
        r'                time_str = event.get(\'time\', \'\')\n                try:',
        fixed_content
    )
    
    # Fix the seventh indentation error (in sorting calendar events except block)
    fixed_content = re.sub(
        r'    except Exception as e:\n            self.logger.error',
        r'        except Exception as e:\n            self.logger.error',
        fixed_content
    )
    
    # Fix the eighth indentation error (in update_message)
    fixed_content = re.sub(
        r'    async def update_message\(self, query, text, keyboard=None, parse_mode=ParseMode.HTML\):\n        """Utility to update a message with error handling"""\n    try:',
        r'    async def update_message(self, query, text, keyboard=None, parse_mode=ParseMode.HTML):\n        """Utility to update a message with error handling"""\n        try:',
        fixed_content
    )
    
    # Fix the ninth indentation error (in update_message)
    fixed_content = re.sub(
        r'            elif len\(text\) > MAX_MESSAGE_LENGTH:\n            logger.warning',
        r'            elif len(text) > MAX_MESSAGE_LENGTH:\n                logger.warning',
        fixed_content
    )
    
    # Fix the tenth indentation error (in update_message else block)
    fixed_content = re.sub(
        r'        else:\n                # Normal case',
        r'            else:\n                # Normal case',
        fixed_content
    )
    
    # Fix the eleventh indentation error (in update_message except block)
    fixed_content = re.sub(
        r'    except Exception as e:\n        logger.warning\(f"Could not update message text: {str\(e\)}"\)\n            ',
        r'        except Exception as e:\n            logger.warning(f"Could not update message text: {str(e)}")\n            ',
        fixed_content
    )
    
    # Fix the twelfth indentation error (in caption too long block)
    fixed_content = re.sub(
        r'                if len\(text\) > MAX_CAPTION_LENGTH:\n                logger.warning',
        r'                if len(text) > MAX_CAPTION_LENGTH:\n                    logger.warning',
        fixed_content
    )
    
    # Write the modified content back to the file
    with open(main_file_path, "w", encoding="utf-8") as file:
        file.write(fixed_content)
    
    print(f"Successfully fixed indentation error in {main_file_path}")
    return True

if __name__ == "__main__":
    fix_indentation_error() 