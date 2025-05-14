#!/usr/bin/env python3
import re

# Open the file and read its contents
with open('trading_bot/services/calendar_service/tradingview_calendar.py', 'r') as f:
    content = f.read()

# Find the problematic section and fix its indentation
content = re.sub(
    r'                    \n                if not isinstance\(data, list\):', 
    r'                    \n                if not isinstance(data, list):', 
    content
)

# Fix all the indentation in this section
lines = content.split('\n')
indented_section = False
for i in range(len(lines)):
    if 'if not isinstance(data, list):' in lines[i]:
        indented_section = True
    elif indented_section and '                    logger.info(f"Received {len(data)} items from API")' in lines[i]:
        indented_section = False
    
    if indented_section and lines[i].startswith('                        '):
        lines[i] = lines[i].replace('                        ', '                    ', 1)

# Write the fixed content back to the file
with open('trading_bot/services/calendar_service/tradingview_calendar.py', 'w') as f:
    f.write('\n'.join(lines))

print("Fixed indentation issues in tradingview_calendar.py")

def fix_indentation_issues():
    """Fix the remaining indentation issues in main.py"""
    with open('trading_bot/main.py', 'r') as file:
        lines = file.readlines()
    
    # Fix specific indentation issues
    
    # Line ~711: Unexpected indent in the except block
    for i in range(700, 720):
        if "raise" in lines[i] and lines[i].startswith("            raise"):
            lines[i] = "        raise\n"
    
    # Line ~724: Indentation in the initialize_services method
    for i in range(720, 740):
        if "try:" in lines[i] and lines[i].startswith("    try:"):
            lines[i] = "        try:\n"
    
    # Line ~739: Indentation in the periodic_cleanup function
    for i in range(735, 750):
        if "try:" in lines[i] and lines[i].startswith("                    try:"):
            lines[i] = "                        try:\n"
    
    # Line ~759: Indentation in the except block
    for i in range(750, 770):
        if "raise" in lines[i] and lines[i].startswith("            raise"):
            lines[i] = "        raise\n"
    
    # Line ~802: Indentation in the try block
    for i in range(790, 810):
        if "try:" in lines[i] and lines[i].startswith("    try:"):
            lines[i] = "        try:\n"
    
    # Line ~811: Indentation in the nested try block
    for i in range(805, 820):
        if "try:" in lines[i] and lines[i].startswith("            try:"):
            lines[i] = "                try:\n"
    
    # Line ~828: Indentation in the except block
    for i in range(820, 840):
        if "self.logger.error" in lines[i] and lines[i].startswith("            self.logger.error"):
            lines[i] = "        self.logger.error" + lines[i][12:]
    
    # Line ~861: Indentation in the try block
    for i in range(850, 870):
        if "try:" in lines[i] and lines[i].startswith("    try:"):
            lines[i] = "        try:\n"
    
    # Line ~880: Indentation in the elif block
    for i in range(870, 890):
        if "logger.warning" in lines[i] and lines[i].startswith("            logger.warning"):
            lines[i] = "                logger.warning" + lines[i][12:]
    
    # Line ~899: Indentation in the else block
    for i in range(890, 910):
        if "else:" in lines[i] and lines[i].startswith("        else:"):
            lines[i] = "            else:\n"
    
    # Line ~920: Indentation in the try block
    for i in range(910, 930):
        if "try:" in lines[i] and lines[i].startswith("        try:"):
            lines[i] = "            try:\n"
    
    # Line ~935: Indentation in the if block
    for i in range(930, 950):
        if "logger.warning" in lines[i] and lines[i].startswith("                logger.warning"):
            lines[i] = "                    logger.warning" + lines[i][16:]
    
    # Write the fixed content back to the file
    with open('trading_bot/main.py', 'w') as file:
        file.writelines(lines)
    
    print("Fixed remaining indentation issues in trading_bot/main.py")

if __name__ == "__main__":
    fix_indentation_issues()
