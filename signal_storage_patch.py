#!/usr/bin/env python
"""
Signal Storage Patch

This script modifies the TelegramService class in trading_bot/main.py
to fix the signal storage and retrieval system, solving the "Signal not found" error.
"""

import os
import sys
import re
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Main file path
MAIN_FILE_PATH = "trading_bot/main.py"

def backup_original_file():
    """Create a backup of the original main.py file"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = f"{MAIN_FILE_PATH}.backup-{timestamp}"
    
    try:
        shutil.copy2(MAIN_FILE_PATH, backup_file)
        logger.info(f"✅ Backup created at {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"❌ Failed to create backup file: {str(e)}")
        return None

def fix_init_method(content):
    """Fix __init__ method to add the signals directory"""
    init_pattern = r"(\s+self\.signals_dir\s*=\s*[\"']data/signals[\"'])"
    user_signals_dir = "\n        self.user_signals_dir = \"data/signals/users\"\n"
    create_dirs = "\n        # Create necessary directories\n        os.makedirs(self.signals_dir, exist_ok=True)\n        os.makedirs(self.user_signals_dir, exist_ok=True)\n"
    
    # Check if the user signals directory already exists
    if "self.user_signals_dir" in content:
        logger.info("User signals directory already defined, skipping")
        return content
        
    # Add user_signals_dir after signals_dir
    content = re.sub(init_pattern, r"\1" + user_signals_dir + create_dirs, content)
    logger.info("✅ Added user_signals_dir to __init__ method")
    
    return content

def add_save_user_signal_method(content):
    """Add _save_user_signal method to TelegramService"""
    # Check if the method already exists
    if "_save_user_signal" in content:
        logger.info("_save_user_signal method already exists, skipping")
        return content
    
    # Define the new method to insert
    save_user_signal_method = """
    def _save_user_signal(self, user_id: str, signal_id: str, signal_data: Dict[str, Any]) -> None:
        # Save a signal specifically for a user to ensure persistence
        try:
            # Create user's signal directory if it doesn't exist
            user_signal_dir = os.path.join(self.user_signals_dir, user_id)
            os.makedirs(user_signal_dir, exist_ok=True)
            
            # Save the signal data to the user's directory
            signal_path = os.path.join(user_signal_dir, f"{signal_id}.json")
            with open(signal_path, 'w') as f:
                json.dump(signal_data, f)
                
            logger.info(f"Saved signal for user {user_id}: {signal_path}")
        except Exception as e:
            logger.error(f"Error saving user signal: {str(e)}")
    
    """
    
    # Insert after the _format_signal_message method
    pattern = r"(def _format_signal_message.*?return message\s+\}?\s+)"
    content = re.sub(pattern, r"\1" + save_user_signal_method, content, flags=re.DOTALL)
    logger.info("✅ Added _save_user_signal method")
    
    return content

def fix_process_signal_method(content):
    """Fix the process_signal method to save signals to user directories"""
    # Check if already modified by looking for key signature
    if "_save_user_signal(" in content and "os.path.join(self.signals_dir," in content:
        logger.info("process_signal method already updated, skipping")
        return content
        
    # Update the central signal saving code
    # Old pattern
    central_signal_pattern = r"(# Save signal for history tracking.*?with open\(f\"{self\.signals_dir}/{signal_id}\.json\", 'w'\) as f:)"
    # New code
    central_signal_replacement = r"\1"
    
    # Update the central signal saving
    content = re.sub(central_signal_pattern, central_signal_replacement, content, flags=re.DOTALL)
    
    # Now update the admin user signal storage code
    admin_pattern = r"(self\.user_signals\[admin_str_id\]\[signal_id\] = normalized_data)"
    admin_replacement = r"\1\n                        \n                        # IMPROVED: Save user-specific signal\n                        self._save_user_signal(admin_str_id, signal_id, normalized_data)"
    
    content = re.sub(admin_pattern, admin_replacement, content, flags=re.DOTALL)
    
    # Finally update the subscriber signal storage code
    subscriber_pattern = r"(self\.user_signals\[user_str_id\]\[signal_id\] = normalized_data)"
    subscriber_replacement = r"\1\n                    \n                    # IMPROVED: Save user-specific signal\n                    self._save_user_signal(user_str_id, signal_id, normalized_data)"
    
    content = re.sub(subscriber_pattern, subscriber_replacement, content, flags=re.DOTALL)
    
    logger.info("✅ Updated process_signal method to store user-specific signals")
    
    return content

def fix_load_signals_method(content):
    """Fix the _load_signals method to load signals from filesystem"""
    # Check if the method has already been fixed
    if "signals_loaded = 0" in content and "for user_id in os.listdir(self.user_signals_dir)" in content:
        logger.info("_load_signals method already updated, skipping")
        return content
        
    # Find the load_signals method
    load_signals_pattern = r"(async def _load_signals\(self\):.*?self\.user_signals = \{\})"
    
    # New code for loading signals from filesystem
    filesystem_loader = r"""\1
        
        # 2. Load from file system (more reliable for persistence)
        signals_loaded = 0
            
        # Check the user signals directory
        if os.path.exists(self.user_signals_dir):
            # Iterate through each user directory
            for user_id in os.listdir(self.user_signals_dir):
                user_dir = os.path.join(self.user_signals_dir, user_id)
                
                # Skip if not a directory
                if not os.path.isdir(user_dir):
                    continue
                    
                # Initialize user dict if needed
                if user_id not in self.user_signals:
                    self.user_signals[user_id] = {}
                
                # Load each signal file for this user
                for signal_file in os.listdir(user_dir):
                    if signal_file.endswith('.json'):
                        signal_path = os.path.join(user_dir, signal_file)
                        
                        try:
                            with open(signal_path, 'r') as f:
                                signal_data = json.load(f)
                                
                            if 'id' in signal_data:
                                signal_id = signal_data['id']
                                self.user_signals[user_id][signal_id] = signal_data
                                signals_loaded += 1
                        except Exception as file_error:
                            self.logger.warning(f"Error loading signal file {signal_path}: {str(file_error)}")
        
        # 3. Check central signals directory as fallback
        if os.path.exists(self.signals_dir):
            central_signals_loaded = 0
            
            # Find json files in the signals directory
            for signal_file in os.listdir(self.signals_dir):
                if signal_file.endswith('.json') and os.path.isfile(os.path.join(self.signals_dir, signal_file)):
                    signal_path = os.path.join(self.signals_dir, signal_file)
                    
                    try:
                        with open(signal_path, 'r') as f:
                            signal_data = json.load(f)
                            
                        if 'id' in signal_data:
                            central_signals_loaded += 1
                            
                            # Store in admin user signals as fallback
                            for admin_id in self.admin_users:
                                admin_id_str = str(admin_id)
                                if admin_id_str not in self.user_signals:
                                    self.user_signals[admin_id_str] = {}
                                    
                                self.user_signals[admin_id_str][signal_data['id']] = signal_data
                    except Exception as file_error:
                        self.logger.warning(f"Error loading central signal file {signal_path}: {str(file_error)}")
            
            self.logger.info(f"Loaded {central_signals_loaded} signals from central storage")
                    
        self.logger.info(f"Loaded {signals_loaded} signals from file system for {len(self.user_signals)} users")
    """
    
    # Replace the old method with the updated one
    content = re.sub(load_signals_pattern, filesystem_loader, content, flags=re.DOTALL)
    
    logger.info("✅ Updated _load_signals method to load signals from filesystem")
    
    return content

def fix_analyze_from_signal_callback(content):
    """Fix the analyze_from_signal_callback method to properly retrieve signals"""
    # Check if already fixed
    if "signal_found = False" in content and "user_signal_path = os.path.join(self.user_signals_dir" in content:
        logger.info("analyze_from_signal_callback method already fixed, skipping")
        return content
        
    # Find context signal storage section
    signal_context_pattern = r"(# Also store info from the actual signal.*?logger\.info\(f\"Stored signal details: direction=.*?\))"
    signal_context_replacement = r"""# Try to find signal data for additional context
                    # First try user-specific signals
                    user_id = str(update.effective_user.id)
                    signal_found = False
                    signal_data = None
                    
                    # Look in user signals memory cache
                    if user_id in self.user_signals and signal_id in self.user_signals[user_id]:
                        signal_data = self.user_signals[user_id][signal_id]
                        signal_found = True
                        logger.info(f"Found signal {signal_id} in user memory cache")
                    
                    # If not found, try to load from file
                    if not signal_found:
                        user_signal_path = os.path.join(self.user_signals_dir, user_id, f"{signal_id}.json")
                        if os.path.exists(user_signal_path):
                            try:
                                with open(user_signal_path, 'r') as f:
                                    signal_data = json.load(f)
                                signal_found = True
                                logger.info(f"Found signal {signal_id} in user file storage")
                                
                                # Update memory cache
                                if user_id not in self.user_signals:
                                    self.user_signals[user_id] = {}
                                self.user_signals[user_id][signal_id] = signal_data
                            except Exception as e:
                                logger.error(f"Error loading user signal file: {str(e)}")
                    
                    # If still not found, try central storage
                    if not signal_found:
                        central_signal_path = os.path.join(self.signals_dir, f"{signal_id}.json")
                        if os.path.exists(central_signal_path):
                            try:
                                with open(central_signal_path, 'r') as f:
                                    signal_data = json.load(f)
                                signal_found = True
                                logger.info(f"Found signal {signal_id} in central storage")
                                
                                # Add to user signals for future use
                                if user_id not in self.user_signals:
                                    self.user_signals[user_id] = {}
                                self.user_signals[user_id][signal_id] = signal_data
                                
                                # Save to user specific storage
                                self._save_user_signal(user_id, signal_id, signal_data)
                            except Exception as e:
                                logger.error(f"Error loading central signal file: {str(e)}")
                    
                    # Store additional signal info if available
                    if signal_found and signal_data:
                        context.user_data['signal_direction'] = signal_data.get('direction')
                        context.user_data['signal_timeframe'] = signal_data.get('timeframe')
                        # Backup copies
                        context.user_data['signal_direction_backup'] = signal_data.get('direction')
                        context.user_data['signal_timeframe_backup'] = signal_data.get('timeframe')
                        logger.info(f"Stored signal details: direction={signal_data.get('direction')}, timeframe={signal_data.get('timeframe')}")"""
    
    # Replace the old signal lookup with the improved one
    content = re.sub(signal_context_pattern, signal_context_replacement, content, flags=re.DOTALL)
    
    logger.info("✅ Fixed analyze_from_signal_callback method for better signal retrieval")
    
    return content

def fix_back_to_signal_callback(content):
    """Fix the back_to_signal_callback method to improve signal retrieval"""
    # Check if already fixed
    if "signal_id = None" in content and "self._save_user_signal(user_id, signal_id, signal_data)" in content:
        logger.info("back_to_signal_callback method already fixed, skipping")
        return content
        
    # Find the relevant section where signal ID is extracted or assigned
    signal_id_pattern = r"(# Find the most recent signal.*?signal_id = None)"
    signal_id_replacement = r"\1"
    
    # Replace existing signal lookup code
    signal_lookup_pattern = r"# Find matching signal based on instrument and direction.*?if not signal_data:"
    signal_lookup_replacement = r"""# If we have the direct signal ID, try to find it first
            if signal_id:
                # Search in memory cache first
                if user_id in self.user_signals and signal_id in self.user_signals[user_id]:
                    signal_data = self.user_signals[user_id][signal_id]
                    logger.info(f"Found signal with ID {signal_id} in memory cache")
                
                # If not found in memory, try user-specific file storage
                if not signal_data:
                    user_signal_path = os.path.join(self.user_signals_dir, user_id, f"{signal_id}.json")
                    if os.path.exists(user_signal_path):
                        try:
                            with open(user_signal_path, 'r') as f:
                                signal_data = json.load(f)
                            logger.info(f"Found signal with ID {signal_id} in user-specific file storage")
                            
                            # Update memory cache
                            if user_id not in self.user_signals:
                                self.user_signals[user_id] = {}
                            self.user_signals[user_id][signal_id] = signal_data
                        except Exception as e:
                            logger.error(f"Error loading signal from user file: {str(e)}")
                
                # If not found in user storage, try central storage
                if not signal_data:
                    central_signal_path = os.path.join(self.signals_dir, f"{signal_id}.json")
                    if os.path.exists(central_signal_path):
                        try:
                            with open(central_signal_path, 'r') as f:
                                signal_data = json.load(f)
                            logger.info(f"Found signal with ID {signal_id} in central storage")
                            
                            # Save to user memory cache and file storage
                            if user_id not in self.user_signals:
                                self.user_signals[user_id] = {}
                            self.user_signals[user_id][signal_id] = signal_data
                            self._save_user_signal(user_id, signal_id, signal_data)
                        except Exception as e:
                            logger.error(f"Error loading signal from central file: {str(e)}")
            
            # If signal not found by ID, search by instrument and other criteria
            if not signal_data and signal_instrument:
                logger.info(f"Signal not found by ID, searching by instrument: {signal_instrument}")
                
                # Find matching signal in memory cache
                if user_id in self.user_signals:
                    user_signal_dict = self.user_signals[user_id]
                    # Find signals matching instrument, direction and timeframe
                    matching_signals = []
                    
                    for sig_id, sig in user_signal_dict.items():
                        instrument_match = sig.get('instrument') == signal_instrument
                        direction_match = True  # Default to true if we don't have direction data
                        timeframe_match = True  # Default to true if we don't have timeframe data
                        
                        if signal_direction:
                            direction_match = sig.get('direction') == signal_direction
                        if signal_timeframe:
                            timeframe_match = sig.get('timeframe') == signal_timeframe
                        
                        if instrument_match and direction_match and timeframe_match:
                            matching_signals.append((sig_id, sig))
                    
                    # Sort by timestamp, newest first
                    if matching_signals:
                        matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                        signal_id, signal_data = matching_signals[0]
                        logger.info(f"Found matching signal with ID: {signal_id}")
                    else:
                        logger.warning(f"No matching signals found for instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
                        # If no exact match, try with just the instrument
                        matching_signals = []
                        for sig_id, sig in user_signal_dict.items():
                            if sig.get('instrument') == signal_instrument:
                                matching_signals.append((sig_id, sig))
                        
                        if matching_signals:
                            matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                            signal_id, signal_data = matching_signals[0]
                            logger.info(f"Found signal with just instrument match, ID: {signal_id}")
                
                # If still no signal found, try searching in files
                if not signal_data:
                    logger.info("Searching for signals in file storage")
                    
                    # Search in user's signals directory
                    user_signal_dir = os.path.join(self.user_signals_dir, user_id)
                    if os.path.exists(user_signal_dir):
                        matching_signals = []
                        
                        for signal_file in os.listdir(user_signal_dir):
                            if signal_file.endswith('.json'):
                                try:
                                    with open(os.path.join(user_signal_dir, signal_file), 'r') as f:
                                        sig = json.load(f)
                                    
                                    instrument_match = sig.get('instrument') == signal_instrument
                                    direction_match = True
                                    timeframe_match = True
                                    
                                    if signal_direction:
                                        direction_match = sig.get('direction') == signal_direction
                                    if signal_timeframe:
                                        timeframe_match = sig.get('timeframe') == signal_timeframe
                                    
                                    if instrument_match and direction_match and timeframe_match:
                                        matching_signals.append((sig.get('id'), sig))
                                except Exception as e:
                                    logger.warning(f"Error reading signal file {signal_file}: {str(e)}")
                        
                        if matching_signals:
                            matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                            signal_id, signal_data = matching_signals[0]
                            logger.info(f"Found matching signal from file with ID: {signal_id}")
                            
                            # Update memory cache
                            if user_id not in self.user_signals:
                                self.user_signals[user_id] = {}
                            self.user_signals[user_id][signal_id] = signal_data
            
            if not signal_data:"""
    
    # Replace the signal lookup code
    content = re.sub(signal_lookup_pattern, signal_lookup_replacement, content, flags=re.DOTALL)
    
    logger.info("✅ Fixed back_to_signal_callback method for better signal retrieval")
    
    return content

def update_imports(content):
    """Make sure all necessary imports are present"""
    # Check if json is already imported
    if "import json" not in content:
        import_pattern = r"(import os)"
        content = re.sub(import_pattern, r"\1\nimport json", content)
        logger.info("✅ Added json import")
    
    return content

def apply_patch():
    """Apply the patch to fix signal storage issues"""
    try:
        # Check if main file exists
        if not os.path.exists(MAIN_FILE_PATH):
            logger.error(f"❌ Could not find {MAIN_FILE_PATH}. Make sure you're running this script from the project root.")
            return False
        
        # Create backup
        backup_file = backup_original_file()
        if not backup_file:
            logger.error("❌ Failed to create backup, aborting")
            return False
        
        # Read the file content
        with open(MAIN_FILE_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Apply fixes
        modified_content = content
        modified_content = update_imports(modified_content)
        modified_content = fix_init_method(modified_content)
        modified_content = add_save_user_signal_method(modified_content)
        modified_content = fix_process_signal_method(modified_content)
        modified_content = fix_load_signals_method(modified_content)
        modified_content = fix_analyze_from_signal_callback(modified_content)
        modified_content = fix_back_to_signal_callback(modified_content)
        
        # Check if there were any changes
        if content == modified_content:
            logger.info("⚠️ No changes were made, the file may already be patched")
            return True
            
        # Write the modified content
        with open(MAIN_FILE_PATH, 'w', encoding='utf-8') as file:
            file.write(modified_content)
            
        logger.info(f"✅ Successfully applied patches to {MAIN_FILE_PATH}")
        logger.info(f"✅ Original file backed up to {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error applying patch: {str(e)}")
        return False

def main():
    """Main function to run the script"""
    print("\n=== SIGMAPIPS SIGNAL STORAGE PATCH ===\n")
    print("This script will fix the \"Signal not found\" error by modifying how signals are stored and retrieved.")
    print("A backup of the original file will be created before making any changes.")
    
    # Ensure data directories exist
    if not os.path.exists("data/signals/users"):
        print("\nCreating signal directories...")
        os.makedirs("data/signals", exist_ok=True)
        os.makedirs("data/signals/users", exist_ok=True)
        print("✅ Created signal directories")
        
    # Prompt for confirmation
    if input("\nApply patch to fix signal storage? (y/N): ").lower() != 'y':
        print("Patch canceled. No changes made.")
        return 0
    
    # Apply the patch
    if apply_patch():
        print("\n✅ PATCH APPLIED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Run the setup_signal_storage.py script to ensure all directories are created:")
        print("   python setup_signal_storage.py --create-test")
        print("2. Restart your bot")
        print("3. The 'Analyze Market' button should now work correctly")
        return 0
    else:
        print("\n❌ PATCH FAILED!")
        print("Please check the logs for details. You may need to manually apply the changes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 