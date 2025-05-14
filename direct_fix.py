#!/usr/bin/env python3
"""
Direct fix for indentation error in main.py
"""

import os
from pathlib import Path

def fix_indentation_error():
    """Fix indentation error in main.py by direct replacement"""
    # Path to the main.py file
    main_file_path = Path("trading_bot/main.py")
    
    if not main_file_path.exists():
        print(f"File not found: {main_file_path}")
        return False
    
    # The correct function implementation
    correct_function = """async def _get_signal_related_trades(self, signal_id):
    \"\"\"Retrieve related trades from the database\"\"\"
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
        
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None

"""
    
    # Read the content of the file
    with open(main_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Create a backup of the original file
    backup_path = main_file_path.with_suffix(".py.bak")
    with open(backup_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Created backup of the original file: {backup_path}")
    
    # Replace the problematic section
    # Find the start of the imports
    import_section = "from telegram.error import TelegramError, BadRequest"
    
    # Split the content at the imports
    parts = content.split(import_section)
    
    if len(parts) != 2:
        print("Could not find the import section to split the file")
        return False
    
    # Replace everything before the imports with the correct header and function
    header = """# Import necessary modules for improved logging
import os
import sys
import json
import logging
import logging.config
from datetime import datetime

"""
    
    # Create the new content
    new_content = header + correct_function + import_section + parts[1]
    
    # Write the modified content back to the file
    with open(main_file_path, "w", encoding="utf-8") as file:
        file.write(new_content)
    
    print(f"Successfully fixed indentation error in {main_file_path}")
    return True

if __name__ == "__main__":
    fix_indentation_error() 