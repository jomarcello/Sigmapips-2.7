#!/usr/bin/env python3

def fix_specific_issue():
    """Fix the specific indentation issues at lines 746-748"""
    with open('trading_bot/main.py', 'r') as file:
        lines = file.readlines()
    
    # Create a backup first
    with open('trading_bot/main.py.backup5', 'w') as file:
        file.writelines(lines)
    
    # Fix the specific issues at lines 746-748
    for i in range(len(lines)):
        if i == 745 and "except Exception as e:" in lines[i]:
            lines[i] = "        except Exception as e:\n"
        elif i == 746 and "logger.error" in lines[i] and "Error initializing services" in lines[i]:
            lines[i] = "            logger.error(f\"Error initializing services: {str(e)}\")\n"
        elif i == 747 and "raise" in lines[i]:
            lines[i] = "            raise\n"
        elif i == 748 and "#" in lines[i] and "Calendar service helpers" in lines[i]:
            lines[i] = "\n# Calendar service helpers\n"
    
    # Write the fixed content back to the file
    with open('trading_bot/main.py', 'w') as file:
        file.writelines(lines)
    
    print("Fixed specific indentation issues at lines 746-748 in trading_bot/main.py")

if __name__ == "__main__":
    fix_specific_issue() 