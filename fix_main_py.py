#!/usr/bin/env python3
"""
Fix indentation error in main.py by replacing the problematic part
"""

import os
import sys
from pathlib import Path

def fix_main_py():
    """Fix the indentation error in main.py"""
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
    
    # The correct beginning of the file
    correct_beginning = """# Import necessary modules for improved logging
import os
import sys
import json
import logging
import logging.config
from datetime import datetime


async def _get_signal_related_trades(self, signal_id):
    \"""Retrieve related trades from the database\"""
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


from telegram.error import TelegramError, BadRequest"""
    
    # Find the position of the first occurrence of "from telegram.error import TelegramError, BadRequest"
    marker = "from telegram.error import TelegramError, BadRequest"
    marker_pos = content.find(marker)
    
    if marker_pos == -1:
        print(f"Could not find the marker: {marker}")
        return False
    
    # Replace everything from the beginning of the file up to and including the marker
    new_content = correct_beginning + content[marker_pos + len(marker):]
    
    # Write the modified content back to the file
    with open(main_file_path, "w", encoding="utf-8") as file:
        file.write(new_content)
    
    print(f"Successfully fixed indentation error in {main_file_path}")
    return True

if __name__ == "__main__":
    fix_main_py() 