#!/usr/bin/env python3
"""
Test script to verify that the analyze_from_signal_callback handler is correctly registered
in the main.py file.
"""

import re
import os

def check_handler_registration():
    """Check if the analyze_from_signal_callback handler is correctly registered"""
    try:
        with open('trading_bot/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use a more specific pattern to find the function
        function_pattern = r'async def analyze_from_signal_callback\(self, update: Update, context=None\) -> int:'
        function_matches = re.findall(function_pattern, content)
        
        if not function_matches:
            print("ERROR: analyze_from_signal_callback function not found with exact pattern!")
            # Try to find with a simpler pattern
            simple_pattern = r'def analyze_from_signal_callback'
            simple_matches = re.findall(simple_pattern, content)
            if simple_matches:
                print(f"Found {len(simple_matches)} matches with simpler pattern")
            else:
                print("No matches found with simpler pattern either")
                
            # Try to find similar functions
            similar_functions = re.findall(r'async def (\w+signal\w+)', content)
            if similar_functions:
                print("Found similar functions:")
                for func in set(similar_functions):
                    print(f"  - {func}")
            return False
        
        print(f"Found {len(function_matches)} analyze_from_signal_callback function definitions")
        
        # Check if the handler is registered
        pattern = r'application\.add_handler\(CallbackQueryHandler\(self\.analyze_from_signal_callback'
        matches = re.findall(pattern, content)
        
        if not matches:
            print("ERROR: No handler registration found for analyze_from_signal_callback!")
            return False
        
        print(f"Found {len(matches)} handler registrations for analyze_from_signal_callback")
        
        # Check if the button is created with the correct callback data
        button_pattern = r'InlineKeyboardButton\("🔍 Analyze Market", callback_data=f"analyze_from_signal_'
        button_matches = re.findall(button_pattern, content)
        
        if not button_matches:
            print("ERROR: No Analyze Market button found with analyze_from_signal callback data!")
            return False
        
        print(f"Found {len(button_matches)} Analyze Market buttons")
        
        # Check if the signal_technical button is registered
        signal_pattern = r'application\.add_handler\(CallbackQueryHandler\(self\.signal_technical_callback'
        signal_matches = re.findall(signal_pattern, content)
        
        if not signal_matches:
            print("ERROR: No handler registration found for signal_technical_callback!")
            return False
        
        print(f"Found {len(signal_matches)} handler registrations for signal_technical_callback")
        
        # Check if the back_to_signal button is registered
        back_pattern = r'application\.add_handler\(CallbackQueryHandler\(self\.back_to_signal_callback'
        back_matches = re.findall(back_pattern, content)
        
        if not back_matches:
            print("ERROR: No handler registration found for back_to_signal_callback!")
            return False
        
        print(f"Found {len(back_matches)} handler registrations for back_to_signal_callback")
        
        # Check if the signal_technical button is used in the keyboard
        keyboard_pattern = r'\[InlineKeyboardButton\("📈 Technical Analysis", callback_data="signal_technical"\)\]'
        keyboard_matches = re.findall(keyboard_pattern, content)
        
        if not keyboard_matches:
            print("ERROR: No Technical Analysis button found with signal_technical callback data!")
            return False
        
        print(f"Found {len(keyboard_matches)} Technical Analysis buttons")
        
        return True
    
    except Exception as e:
        print(f"Error checking handler registration: {str(e)}")
        return False

def main():
    """Main function"""
    print("Checking analyze_from_signal_callback handler registration...")
    success = check_handler_registration()
    
    if success:
        print("\nAll checks passed! The analyze_from_signal_callback handler is correctly registered.")
    else:
        print("\nSome checks failed! Please review the analyze_from_signal_callback implementation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    main() 