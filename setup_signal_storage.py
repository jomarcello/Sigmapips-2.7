#!/usr/bin/env python
"""
Setup Signal Storage Directories

This script creates the necessary directory structure for proper signal storage
to fix the "Signal not found" error in Sigmapips bot when using "Analyze Market".
"""

import os
import sys
import logging
import json
import argparse
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Define directory paths
BASE_DIR = "data"
SIGNALS_DIR = os.path.join(BASE_DIR, "signals")
USER_SIGNALS_DIR = os.path.join(SIGNALS_DIR, "users")

def create_directories():
    """Create necessary directories for signal storage"""
    directories = [BASE_DIR, SIGNALS_DIR, USER_SIGNALS_DIR]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Directory created/verified: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {directory}: {str(e)}")
            return False
    
    # Create .keep files to ensure directories are tracked in git
    for directory in directories:
        keep_file = os.path.join(directory, ".keep")
        if not os.path.exists(keep_file):
            try:
                with open(keep_file, "w") as f:
                    f.write("# This file exists to ensure the directory is tracked in git")
                logger.info(f"✅ Created .keep file in {directory}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to create .keep file in {directory}: {str(e)}")
    
    return True

def check_permissions():
    """Check if we have write permissions to the directories"""
    directories = [BASE_DIR, SIGNALS_DIR, USER_SIGNALS_DIR]
    
    for directory in directories:
        if os.path.exists(directory):
            if os.access(directory, os.W_OK):
                logger.info(f"✅ Directory {directory} is writable")
            else:
                logger.warning(f"⚠️ Directory {directory} is not writable")
                return False
    
    return True

def create_test_signal(user_id="test"):
    """Create a test signal to verify storage works"""
    # Ensure user directory exists
    user_dir = os.path.join(USER_SIGNALS_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    # Create test signal data
    timestamp = int(datetime.now().timestamp())
    signal_id = f"EURUSD_BUY_1h_{timestamp}"
    
    test_signal = {
        "id": signal_id,
        "instrument": "EURUSD",
        "direction": "BUY",
        "entry": 1.0850,
        "stop_loss": 1.0800,
        "take_profit": 1.0900,
        "timeframe": "1h",
        "timestamp": datetime.now().isoformat(),
        "message": "<b>🎯 New Trading Signal 🎯</b>\n\n<b>Instrument:</b> EURUSD\n<b>Action:</b> BUY 🟢\n\n<b>Entry:</b> 1.0850\n<b>Stop Loss:</b> 1.0800\n<b>Take Profit:</b> 1.0900\n\n<b>Timeframe:</b> 1h\n<b>Time:</b> Just now"
    }
    
    # Save to user directory
    user_signal_path = os.path.join(user_dir, f"{signal_id}.json")
    
    try:
        with open(user_signal_path, 'w') as f:
            json.dump(test_signal, f)
        logger.info(f"✅ Test signal created for user {user_id}: {user_signal_path}")
    except Exception as e:
        logger.error(f"❌ Failed to create test signal: {str(e)}")
        return None
    
    # Also save to central directory
    central_signal_path = os.path.join(SIGNALS_DIR, f"{signal_id}.json")
    
    try:
        with open(central_signal_path, 'w') as f:
            json.dump(test_signal, f)
        logger.info(f"✅ Test signal created in central storage: {central_signal_path}")
    except Exception as e:
        logger.error(f"❌ Failed to create central test signal: {str(e)}")
    
    return signal_id

def main():
    """Main function to set up signal storage"""
    parser = argparse.ArgumentParser(description="Set up signal storage directories for Sigmapips")
    parser.add_argument("--create-test", action="store_true", help="Create a test signal")
    parser.add_argument("--user-id", type=str, default="test", help="User ID for test signal")
    args = parser.parse_args()
    
    print("\n=== SIGMAPIPS SIGNAL STORAGE SETUP ===\n")
    
    # Create directories
    logger.info("Setting up signal storage directories...")
    if not create_directories():
        logger.error("❌ Failed to create required directories")
        return 1
        
    # Check permissions
    logger.info("Checking directory permissions...")
    if not check_permissions():
        logger.warning("⚠️ Permission issues detected with storage directories")
        print("\n⚠️ WARNING: The script detected permission issues with the storage directories.")
        print("You may need to run this script with administrative privileges or")
        print("adjust the permissions on the 'data' directory.")
        return 1
    
    # Create test signal if requested
    if args.create_test:
        logger.info(f"Creating test signal for user ID: {args.user_id}")
        test_signal_id = create_test_signal(args.user_id)
        
        if test_signal_id:
            print(f"\n✅ Created test signal with ID: {test_signal_id}")
            print(f"   - User signal: data/signals/users/{args.user_id}/{test_signal_id}.json")
            print(f"   - Central signal: data/signals/{test_signal_id}.json")
        else:
            print("\n❌ Failed to create test signal")
            return 1
    
    print("\n✅ Signal storage setup complete!")
    print("\nDirectory structure created:")
    print(f"  - {BASE_DIR}/")
    print(f"  - {BASE_DIR}/signals/")
    print(f"  - {BASE_DIR}/signals/users/")
    print("\nNext Steps:")
    print("1. Make sure to update your TelegramService class to use this storage")
    print("2. Restart your bot to apply the changes")
    print("3. The 'Analyze Market' button should now work correctly")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 