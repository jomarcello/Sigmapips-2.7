import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiofiles

logger = logging.getLogger(__name__)

class SignalStorageService:
    """
    Service for storing trading signals persistently.
    Works as an extension to the current in-memory storage system without modifying main.py.
    """
    
    def __init__(self, storage_dir: str = "storage"):
        """
        Initialize the signal storage service.
        
        Args:
            storage_dir: Directory where signal data will be stored
        """
        self.storage_dir = storage_dir
        self.signals_file = os.path.join(storage_dir, "signals.json")
        self.signals_by_user: Dict[str, Dict[str, Any]] = {}
        self.loaded = False
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
            logger.info(f"Created storage directory: {storage_dir}")
    
    async def load_signals(self) -> None:
        """Load signals from the persistent storage file."""
        try:
            if not os.path.exists(self.signals_file):
                logger.info(f"Signals file doesn't exist yet: {self.signals_file}")
                self.signals_by_user = {}
                self.loaded = True
                return
                
            async with aiofiles.open(self.signals_file, "r") as f:
                content = await f.read()
                self.signals_by_user = json.loads(content)
                logger.info(f"Loaded {len(self.signals_by_user)} users with signals from {self.signals_file}")
                
            self.loaded = True
        except Exception as e:
            logger.error(f"Error loading signals from {self.signals_file}: {str(e)}")
            self.signals_by_user = {}
            self.loaded = True
    
    async def save_signals(self) -> None:
        """Save signals to the persistent storage file."""
        try:
            # Ensure storage directory exists
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir, exist_ok=True)
            
            # Save to file
            async with aiofiles.open(self.signals_file, "w") as f:
                await f.write(json.dumps(self.signals_by_user, indent=2))
                
            logger.info(f"Saved {len(self.signals_by_user)} users with signals to {self.signals_file}")
        except Exception as e:
            logger.error(f"Error saving signals to {self.signals_file}: {str(e)}")
    
    async def store_signal(self, user_id: str, signal_id: str, signal_data: Dict) -> None:
        """
        Store a signal for a user.
        
        Args:
            user_id: User ID as a string
            signal_id: Signal ID
            signal_data: Signal data to store
        """
        # Ensure data is loaded
        if not self.loaded:
            await self.load_signals()
            
        # Ensure user exists in the dictionary
        if user_id not in self.signals_by_user:
            self.signals_by_user[user_id] = {}
        
        # Add timestamp if not present
        if "timestamp" not in signal_data:
            signal_data["timestamp"] = datetime.now().isoformat()
        
        # Store the signal
        self.signals_by_user[user_id][signal_id] = signal_data
        logger.info(f"Stored signal {signal_id} for user {user_id}")
        
        # Save signals to file
        await self.save_signals()
    
    async def get_signal(self, user_id: str, signal_id: str) -> Optional[Dict]:
        """
        Get a signal for a user.
        
        Args:
            user_id: User ID as a string
            signal_id: Signal ID
            
        Returns:
            The signal data or None if not found
        """
        # Ensure data is loaded
        if not self.loaded:
            await self.load_signals()
            
        # Get the signal
        if user_id in self.signals_by_user and signal_id in self.signals_by_user[user_id]:
            logger.info(f"Retrieved signal {signal_id} for user {user_id}")
            return self.signals_by_user[user_id][signal_id]
        
        logger.warning(f"Signal {signal_id} not found for user {user_id}")
        return None
        
    async def get_signals_for_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get all signals for a user.
        
        Args:
            user_id: User ID as a string
            
        Returns:
            Dictionary of signal ID to signal data
        """
        # Ensure data is loaded
        if not self.loaded:
            await self.load_signals()
            
        # Get signals for user
        return self.signals_by_user.get(user_id, {})
        
    async def get_signals_for_instrument(self, user_id: str, instrument: str) -> Dict[str, Any]:
        """
        Get all signals for a user and instrument.
        
        Args:
            user_id: User ID as a string
            instrument: Instrument name (e.g., "EURUSD")
            
        Returns:
            Dictionary of signal ID to signal data for the specified instrument
        """
        # Get all signals for the user
        user_signals = await self.get_signals_for_user(user_id)
        
        # Filter by instrument
        instrument_signals = {}
        for signal_id, signal_data in user_signals.items():
            if signal_data.get("instrument") == instrument or signal_data.get("symbol") == instrument:
                instrument_signals[signal_id] = signal_data
                
        return instrument_signals
        
    async def delete_signal(self, user_id: str, signal_id: str) -> bool:
        """
        Delete a signal for a user.
        
        Args:
            user_id: User ID as a string
            signal_id: Signal ID
            
        Returns:
            True if the signal was deleted, False otherwise
        """
        # Ensure data is loaded
        if not self.loaded:
            await self.load_signals()
            
        # Delete the signal
        if user_id in self.signals_by_user and signal_id in self.signals_by_user[user_id]:
            del self.signals_by_user[user_id][signal_id]
            await self.save_signals()
            logger.info(f"Deleted signal {signal_id} for user {user_id}")
            return True
            
        logger.warning(f"Signal {signal_id} not found for user {user_id} - cannot delete")
        return False
        
    async def delete_signals_for_user(self, user_id: str) -> bool:
        """
        Delete all signals for a user.
        
        Args:
            user_id: User ID as a string
            
        Returns:
            True if signals were deleted, False otherwise
        """
        # Ensure data is loaded
        if not self.loaded:
            await self.load_signals()
            
        # Delete signals for user
        if user_id in self.signals_by_user:
            del self.signals_by_user[user_id]
            await self.save_signals()
            logger.info(f"Deleted all signals for user {user_id}")
            return True
            
        logger.warning(f"No signals found for user {user_id} - nothing to delete")
        return False 