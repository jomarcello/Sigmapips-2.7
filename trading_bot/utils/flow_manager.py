"""
Flow state manager for Telegram bot
Centrally manages which flow (menu, signal, etc.) a user is currently in
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)

class FlowType(Enum):
    MENU = "menu"
    SIGNAL = "signal"
    UNKNOWN = "unknown"

class FlowManager:
    """
    Centralized flow state manager to track and control user flows
    """
    
    @staticmethod
    def set_flow(context, flow_type, metadata=None):
        """
        Set the current flow for a user
        
        Args:
            context: The telegram context object
            flow_type: The FlowType value
            metadata: Additional flow-related data (e.g., signal_id, instrument)
        """
        if not context or not hasattr(context, 'user_data'):
            logger.warning("Cannot set flow: Invalid context")
            return False
            
        # Reset all flow flags first
        FlowManager.reset_all_flows(context)
        
        # Set the new flow
        flow_name = flow_type.value
        context.user_data['current_flow'] = flow_name
        
        # Set flow-specific flags
        if flow_type == FlowType.MENU:
            context.user_data['in_menu_flow'] = True
            context.user_data['from_menu'] = True
            context.user_data['in_signal_flow'] = False
            context.user_data['from_signal'] = False
        elif flow_type == FlowType.SIGNAL:
            context.user_data['in_signal_flow'] = True
            context.user_data['from_signal'] = True
            context.user_data['in_menu_flow'] = False
            context.user_data['from_menu'] = False
        
        # Store metadata if provided
        if metadata:
            for key, value in metadata.items():
                context.user_data[key] = value
                
        logger.info(f"Set flow: {flow_name} with metadata: {metadata}")
        return True
    
    @staticmethod
    def get_current_flow(context):
        """
        Get the current flow for a user
        
        Args:
            context: The telegram context object
            
        Returns:
            FlowType: The current flow type
        """
        if not context or not hasattr(context, 'user_data'):
            return FlowType.UNKNOWN
            
        flow_name = context.user_data.get('current_flow')
        
        if flow_name == FlowType.MENU.value:
            return FlowType.MENU
        elif flow_name == FlowType.SIGNAL.value:
            return FlowType.SIGNAL
        
        # Backward compatibility - check for legacy flow flags
        if context.user_data.get('in_signal_flow', False):
            return FlowType.SIGNAL
        elif context.user_data.get('in_menu_flow', False):
            return FlowType.MENU
            
        return FlowType.UNKNOWN
    
    @staticmethod
    def reset_all_flows(context):
        """
        Reset all flow flags
        
        Args:
            context: The telegram context object
        """
        if not context or not hasattr(context, 'user_data'):
            return
            
        # Clear all flow flags
        context.user_data['current_flow'] = None
        context.user_data['in_menu_flow'] = False
        context.user_data['from_menu'] = False
        context.user_data['in_signal_flow'] = False
        context.user_data['from_signal'] = False
    
    @staticmethod
    def is_in_flow(context, flow_type):
        """
        Check if the user is in a specific flow
        
        Args:
            context: The telegram context object
            flow_type: The FlowType to check
            
        Returns:
            bool: True if in the specified flow, False otherwise
        """
        current_flow = FlowManager.get_current_flow(context)
        return current_flow == flow_type 