import re

def fix_file():
    # Read the file
    with open('trading_bot/main.py', 'r') as f:
        content = f.read()
    
    # Make a simple change
    content = content.replace(
        'context.user_data[\'signal_id\'] = signal_id', 
        'context.user_data[\'signal_id\'] = signal_id\n                    \n                    # Set signal flow flags\n                    context.user_data[\'from_signal\'] = True\n                    context.user_data[\'in_signal_flow\'] = True\n                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")'
    )
    
    # Write back to file
    with open('trading_bot/main.py', 'w') as f:
        f.write(content)
    
    print("File updated successfully")

if __name__ == "__main__":
    fix_file() 