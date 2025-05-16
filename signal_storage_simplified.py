#!/usr/bin/env python3
"""
Signal Storage Simplified - Enhanced signal storage integration for SigmaPips bot.

This module patches the SigmaPipsBot class to enhance signal storage functionality.
"""

import logging
import json
import os
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import functools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalStorage:
    """
    Simple signal storage to keep track of signals and ensure we can retrieve them later.
    This is used to enhance the existing _store_original_signal_page and _get_original_signal_page methods.
    """
    
    def __init__(self):
        """Initialize storage"""
        self.signals = {}
        self.signals_by_instrument = {}
        self.signals_by_user = {}
    
    def store_signal(self, user_id: str, signal_id: str, instrument: str, signal_data: Dict[str, Any]) -> bool:
        """Store a signal by ID"""
        user_id = str(user_id)
        
        # Store signal by ID
        self.signals[signal_id] = signal_data
        
        # Store by user
        if user_id not in self.signals_by_user:
            self.signals_by_user[user_id] = {}
        self.signals_by_user[user_id][signal_id] = signal_data
        
        # Store by instrument
        if instrument not in self.signals_by_instrument:
            self.signals_by_instrument[instrument] = {}
        self.signals_by_instrument[instrument][signal_id] = signal_data
        
        logger.info(f"Stored signal {signal_id} for user {user_id} and instrument {instrument}")
        return True
    
    def get_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Get a signal by ID"""
        return self.signals.get(signal_id)
    
    def get_signal_by_user(self, user_id: str, signal_id: str) -> Optional[Dict[str, Any]]:
        """Get a signal by user ID and signal ID"""
        user_id = str(user_id)
        if user_id in self.signals_by_user and signal_id in self.signals_by_user[user_id]:
            return self.signals_by_user[user_id][signal_id]
        return None
    
    def get_signals_by_instrument(self, user_id: str, instrument: str) -> Dict[str, Dict[str, Any]]:
        """Get all signals for a specific instrument and user"""
        user_id = str(user_id)
        result = {}
        
        # Check signals for this instrument
        if instrument in self.signals_by_instrument:
            # Filter by user ID
            for signal_id, signal_data in self.signals_by_instrument[instrument].items():
                if user_id in self.signals_by_user and signal_id in self.signals_by_user[user_id]:
                    result[signal_id] = signal_data
                    
        return result
    
    def get_latest_signal_for_instrument(self, user_id: str, instrument: str) -> Optional[Dict[str, Any]]:
        """Get the latest signal for a specific instrument and user"""
        user_id = str(user_id)
        signals = self.get_signals_by_instrument(user_id, instrument)
        
        if not signals:
            return None
            
        # Find the latest signal based on timestamp
        latest_signal = None
        latest_time = datetime.min
        
        for signal_id, signal_data in signals.items():
            signal_time = signal_data.get("timestamp")
            if signal_time:
                try:
                    # Parse the timestamp
                    dt = datetime.fromisoformat(signal_time)
                    if dt > latest_time:
                        latest_time = dt
                        latest_signal = signal_data
                except (ValueError, TypeError):
                    # If unable to parse timestamp, use the signal ID as a fallback
                    # This isn't ideal but should work for most cases
                    pass
                    
        return latest_signal

# Singleton instantie
_signal_storage = None

def get_signal_storage() -> SignalStorage:
    """Haal de singleton instantie van SignalStorage op."""
    global _signal_storage
    if _signal_storage is None:
        _signal_storage = SignalStorage()
    return _signal_storage

def patch_signal_methods(bot_class):
    """
    Patch the signal storage methods in the bot class.
    
    Args:
        bot_class: The class to patch (should be SigmaPipsBot)
    """
    # Save original methods
    original_store_signal_page = bot_class._store_original_signal_page
    # original_get_original_signal_page = bot_class._get_original_signal_page # This line causes AttributeError

    # Define a dummy original_get_original_signal_page if it doesn't exist
    if not hasattr(bot_class, '_get_original_signal_page'):
        async def dummy_get_original_signal_page(self, update, context=None, signal_id=None):
            return None
        original_get_original_signal_page = dummy_get_original_signal_page
        logger.info("'_get_original_signal_page' not found on bot_class. Using a dummy.")
    else:
        original_get_original_signal_page = bot_class._get_original_signal_page
    
    # Create patched methods
    @functools.wraps(original_store_signal_page)
    async def patched_store_signal_page(self, update, context, instrument, signal_id):
        """Patched version of _store_original_signal_page that uses SignalStorage as well."""
        try:
            # Call the original method first
            result = await original_store_signal_page(self, update, context, instrument, signal_id)
            
            # Store in our additional storage for redundancy
            try:
                storage = get_signal_storage()
                
                # Get user ID
                user_id = update.effective_user.id if update and hasattr(update, 'effective_user') else "default"
                
                # Get the signal data
                signal_data = None
                
                # Try to get from context first
                if context and hasattr(context, 'user_data') and 'original_signal' in context.user_data:
                    signal_data = context.user_data['original_signal']
                    
                # If not in context, try user_signals
                if not signal_data and hasattr(self, 'user_signals'):
                    user_str_id = str(user_id)
                    if user_str_id in self.user_signals and signal_id in self.user_signals[user_str_id]:
                        signal_data = self.user_signals[user_str_id][signal_id]
                
                # Store if we have signal data
                if signal_data:
                    storage.store_signal(user_id, signal_id, instrument, signal_data)
                    logger.info(f"Additional signal storage: stored signal {signal_id} for user {user_id}")
                
            except Exception as e:
                logger.error(f"Error in additional signal storage: {str(e)}")
                
            # Return the original result
            return result
            
        except Exception as e:
            logger.error(f"Error in patched store_signal_page: {str(e)}")
            # Try the original method if our patch fails
            return await original_store_signal_page(self, update, context, instrument, signal_id)
    
    @functools.wraps(original_get_original_signal_page)
    async def patched_get_original_signal_page(self, update, context=None, signal_id=None):
        """Patched version of _get_original_signal_page that also checks SignalStorage and SignalStorageService."""
        try:
            # Try the original method first
            original_result = await original_get_original_signal_page(self, update, context, signal_id)
            
            # If we have a result from the original method, use it
            if original_result:
                logger.info("Original signal page found using original method")
                return original_result
                
            # No result from original method, try our additional storage
            # Get the instrument and signal ID from the callback data or context
            extracted_signal_id = None
            instrument = None
            
            # First try the passed signal_id
            if signal_id:
                extracted_signal_id = signal_id
            
            # Then try from update.callback_query.data
            if not extracted_signal_id and update and hasattr(update, 'callback_query') and update.callback_query and update.callback_query.data:
                parts = update.callback_query.data.split('_')
                if len(parts) >= 4:
                    if "signal" in update.callback_query.data:
                        instrument = parts[3]
                        extracted_signal_id = parts[4] if len(parts) >= 5 else None
            
            # Try from context as a last resort
            if not extracted_signal_id and context and hasattr(context, 'user_data'):
                extracted_signal_id = context.user_data.get('signal_id')
                instrument = context.user_data.get('instrument')
            
            # If we have a signal ID, try to get it from storage
            if extracted_signal_id:
                # Get user ID
                user_id = update.effective_user.id if update and hasattr(update, 'effective_user') else "default"
                user_str_id = str(user_id)
                
                # First, try our simplified storage
                storage = get_signal_storage()
                signal_data = storage.get_signal_by_user(user_str_id, extracted_signal_id)
                
                if signal_data:
                    logger.info(f"Signal found in simplified storage: {extracted_signal_id}")
                    return signal_data
                
                # If not in simplified storage, try SignalStorageService if available
                try:
                    # Check if SignalStorageService is available
                    from trading_bot.services.signal_storage_service import SignalStorageService
                    from trading_bot.services.signal_interceptor import SignalInterceptor
                    
                    interceptor = SignalInterceptor()
                    await interceptor.setup()  # This initializes the storage service
                    
                    # Try to get the signal from storage service
                    signal_data = await interceptor.get_signal(user_str_id, extracted_signal_id)
                    
                    if signal_data:
                        logger.info(f"Signal found in SignalStorageService: {extracted_signal_id}")
                        # Format it into the expected structure for original_signal
                        original_signal = {
                            'instrument': signal_data.get('instrument'),
                            'signal_id': extracted_signal_id,
                            'message': signal_data.get('message'),
                            'timestamp': signal_data.get('timestamp'),
                            'direction': signal_data.get('direction'),
                            'timeframe': signal_data.get('timeframe'),
                            'entry': signal_data.get('entry'),
                            'stop_loss': signal_data.get('stop_loss'),
                            'take_profit': signal_data.get('take_profit')
                        }
                        return original_signal
                        
                except Exception as storage_error:
                    logger.error(f"Error retrieving from SignalStorageService: {str(storage_error)}")
                    
                # If signal not found and we have instrument, get the latest signal for this instrument
                if instrument:
                    latest_signal = storage.get_latest_signal_for_instrument(user_str_id, instrument)
                    if latest_signal:
                        logger.info(f"Found latest signal for instrument {instrument}")
                        return latest_signal
            
            # Not found anywhere
            logger.warning("Original signal page not found in any storage")
            return None
            
        except Exception as e:
            logger.error(f"Error in patched get_original_signal_page: {str(e)}")
            # Try the original method if our patch fails
            return await original_get_original_signal_page(self, update, context, signal_id)
    
    # Apply the patches
    bot_class._store_original_signal_page = patched_store_signal_page
    bot_class._get_original_signal_page = patched_get_original_signal_page
    
    logger.info("Signal storage methods patched successfully")

# Function to apply the patches
def apply_patches(bot_class=None):
    """Apply all patches to the bot class."""
    if bot_class:
        patch_signal_methods(bot_class)
        logger.info(f"Patches applied to {bot_class.__name__}")
    else:
        logger.warning("No bot class provided to patch")
        
# Auto-apply patches if imported directly into the bot
if __name__ != "__main__":
    try:
        # Try to import the bot class dynamically
        from trading_bot.main import TelegramService as SigmaPipsBot
        apply_patches(SigmaPipsBot)
    except ImportError:
        logger.warning("Could not import TelegramService - patches will not be applied automatically")
        logger.info("You must call apply_patches(YourBotClass) manually") 