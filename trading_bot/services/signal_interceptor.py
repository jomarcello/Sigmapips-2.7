import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
import json
import uuid
from datetime import datetime
import os
import sys

# Add parent directory to path so we can import signal_storage_service
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from trading_bot.services.signal_storage_service import SignalStorageService

logger = logging.getLogger(__name__)

class SignalInterceptor:
    """
    Intercepts signals and stores them in the SignalStorageService.
    Works alongside the existing bot without modifying main.py.
    """
    
    def __init__(self):
        """Initialize the signal interceptor."""
        self.signal_storage = SignalStorageService()
        self.running = False
        self.task = None
        
    async def setup(self):
        """Set up the signal interceptor."""
        # Initialize signal storage
        await self.signal_storage.load_signals()
        logger.info("Signal interceptor is ready")
        
    async def intercept_signal(self, signal_data: Dict[str, Any], user_id: str = None) -> str:
        """
        Intercept and store a signal.
        
        Args:
            signal_data: The signal data to store
            user_id: Optional user ID, defaults to "default" if not provided
            
        Returns:
            The generated signal ID
        """
        # Generate a signal ID if not present
        signal_id = signal_data.get('id', str(uuid.uuid4()))
        signal_data['id'] = signal_id
        
        # Add timestamp if not present
        if 'timestamp' not in signal_data:
            signal_data['timestamp'] = datetime.now().isoformat()
            
        # Use default user ID if not provided
        if not user_id:
            user_id = signal_data.get('user_id', 'default')
            
        # Convert user_id to string for consistency
        user_id = str(user_id)
            
        # Store the signal
        await self.signal_storage.store_signal(user_id, signal_id, signal_data)
        
        logger.info(f"Intercepted and stored signal {signal_id} for user {user_id}")
        return signal_id
        
    def start_monitoring(self, signal_callback: Callable[[Dict[str, Any]], None] = None):
        """
        Start monitoring for signals.
        
        Args:
            signal_callback: Optional callback to notify when a signal is intercepted
        """
        if self.running:
            logger.warning("Signal interceptor is already running")
            return
            
        self.running = True
        self.task = asyncio.create_task(self._monitor_signals(signal_callback))
        logger.info("Started signal monitoring")
        
    def stop_monitoring(self):
        """Stop monitoring for signals."""
        if not self.running:
            logger.warning("Signal interceptor is not running")
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
        logger.info("Stopped signal monitoring")
        
    async def _monitor_signals(self, callback: Callable[[Dict[str, Any]], None] = None):
        """
        Monitor for signals.
        
        Args:
            callback: Optional callback to notify when a signal is intercepted
        """
        try:
            # This task would normally monitor a message queue or webhook endpoint
            # Since we don't want to modify main.py, we'll just log that we're monitoring
            logger.info("Signal monitoring task started")
            
            while self.running:
                # Just keep the task alive
                await asyncio.sleep(10)
                
        except asyncio.CancelledError:
            logger.info("Signal monitoring task cancelled")
        except Exception as e:
            logger.error(f"Error in signal monitoring task: {str(e)}")
            
    async def get_signals(self, user_id: str) -> Dict[str, Any]:
        """
        Get all stored signals for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of signal ID to signal data
        """
        return await self.signal_storage.get_signals_for_user(str(user_id))
        
    async def get_signal(self, user_id: str, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific signal.
        
        Args:
            user_id: User ID
            signal_id: Signal ID
            
        Returns:
            Signal data or None if not found
        """
        return await self.signal_storage.get_signal(str(user_id), signal_id)
        
    async def get_signals_for_instrument(self, user_id: str, instrument: str) -> Dict[str, Any]:
        """
        Get all signals for a specific instrument and user.
        
        Args:
            user_id: User ID
            instrument: Instrument name (e.g., "EURUSD")
            
        Returns:
            Dictionary of signal ID to signal data
        """
        return await self.signal_storage.get_signals_for_instrument(str(user_id), instrument)
        
    async def delete_signal(self, user_id: str, signal_id: str) -> bool:
        """
        Delete a specific signal.
        
        Args:
            user_id: User ID
            signal_id: Signal ID
            
        Returns:
            True if the signal was deleted, False otherwise
        """
        return await self.signal_storage.delete_signal(str(user_id), signal_id) 