#!/usr/bin/env python3

import re

def fix_indentation_error(file_path):
    print(f"Fixing indentation error in {file_path}")
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find and remove the duplicate function definition
    pattern = r'return MENU\s*\n\s*# Show the signal details with analyze button\s*\n\s*# Prepare analyze button with signal info embedded\s*\n\s*# Format message\s*\nasync def analyze_from_signal_callback'
    replacement = 'return MENU\n\n    async def analyze_from_signal_callback'
    
    # Replace the pattern
    new_content = re.sub(pattern, replacement, content)
    
    # Check if changes were made
    if new_content != content:
        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Successfully fixed indentation error in {file_path}")
        return True
    else:
        print(f"No changes made to {file_path}")
        return False

if __name__ == "__main__":
    file_path = "trading_bot/main.py"
    fix_indentation_error(file_path) 