#!/usr/bin/env python3

import re
import os
import shutil

def fix_emoji_error(file_path):
    print(f"Fixing emoji error in {file_path}")
    
    # Maak een backup van het bestand
    backup_path = f"{file_path}.emoji_backup"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Zoek naar de oorspronkelijke backup bestanden
    backup_files = [f for f in os.listdir(os.path.dirname(file_path)) 
                    if os.path.basename(file_path) in f and f.endswith(('.bak', '.backup', '.broken'))]
    
    if not backup_files:
        print("No backup files found to restore from")
        return False
    
    # Lees het huidige bestand
    with open(file_path, 'r', encoding='utf-8') as current_file:
        current_content = current_file.read()
    
    # Zoek naar de juiste secties in de backups
    welcome_message_pattern = re.compile(r'WELCOME_MESSAGE\s*=\s*""".*?"""', re.DOTALL)
    subscription_message_pattern = re.compile(r'SUBSCRIPTION_WELCOME_MESSAGE\s*=\s*""".*?"""', re.DOTALL)
    
    # Zoek de juiste secties in het huidige bestand
    current_welcome = welcome_message_pattern.search(current_content)
    current_subscription = subscription_message_pattern.search(current_content)
    
    if not current_welcome or not current_subscription:
        print("Could not find message sections in current file")
        return False
    
    # Probeer een goede backup te vinden
    for backup_file in backup_files:
        backup_path = os.path.join(os.path.dirname(file_path), backup_file)
        try:
            with open(backup_path, 'r', encoding='utf-8') as bak_file:
                backup_content = bak_file.read()
                
            # Zoek de secties in de backup
            backup_welcome = welcome_message_pattern.search(backup_content)
            backup_subscription = subscription_message_pattern.search(backup_content)
            
            if backup_welcome and backup_subscription:
                print(f"Found valid sections in {backup_file}")
                
                # Vervang de secties in het huidige bestand
                new_content = current_content.replace(
                    current_welcome.group(0), 
                    backup_welcome.group(0)
                )
                
                new_content = new_content.replace(
                    current_subscription.group(0), 
                    backup_subscription.group(0)
                )
                
                # Schrijf de gecorrigeerde inhoud terug
                with open(file_path, 'w', encoding='utf-8') as fixed_file:
                    fixed_file.write(new_content)
                
                print(f"Successfully restored message sections from {backup_file}")
                return True
                
        except Exception as e:
            print(f"Error processing {backup_file}: {str(e)}")
    
    print("Could not find valid sections in any backup file")
    return False

if __name__ == "__main__":
    file_path = "trading_bot/main.py"
    fix_emoji_error(file_path) 