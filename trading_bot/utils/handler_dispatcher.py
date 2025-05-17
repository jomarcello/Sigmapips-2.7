"""
Handler dispatcher for Telegram bot
Routes callbacks to the appropriate handlers based on the current flow
"""

import logging
import re
from .flow_manager import FlowManager, FlowType

logger = logging.getLogger(__name__)

class HandlerDispatcher:
    """
    Centralized handler dispatcher to route callbacks based on the current flow
    """
    
    @staticmethod
    async def dispatch_callback(update, context, bot_instance):
        """
        Dispatch a callback query to the appropriate handler based on the current flow
        
        Args:
            update: The telegram update object
            context: The telegram context object
            bot_instance: The TelegramService instance
            
        Returns:
            bool: True if handled, False otherwise
        """
        if not update.callback_query:
            return False
            
        callback_data = update.callback_query.data
        if not callback_data:
            return False
            
        current_flow = FlowManager.get_current_flow(context)
        logger.info(f"Dispatching callback: {callback_data} in flow: {current_flow}")
        
        # Extract any instrument from the callback data
        instrument = HandlerDispatcher._extract_instrument(callback_data)
        if instrument:
            context.user_data['instrument'] = instrument
            logger.info(f"Extracted instrument from callback: {instrument}")
        
        # Handle based on current flow
        if current_flow == FlowType.SIGNAL:
            return await HandlerDispatcher._dispatch_signal_flow(update, context, callback_data, bot_instance)
        elif current_flow == FlowType.MENU:
            return await HandlerDispatcher._dispatch_menu_flow(update, context, callback_data, bot_instance)
        else:
            # Default handling - check callback patterns
            return await HandlerDispatcher._dispatch_by_pattern(update, context, callback_data, bot_instance)
    
    @staticmethod
    async def _dispatch_signal_flow(update, context, callback_data, bot_instance):
        """Handle signal flow callbacks"""
        # Technical analysis in signal flow
        if callback_data.startswith("signal_flow_technical_") or callback_data == "signal_technical":
            logger.info(f"Routing to signal technical analysis")
            return await bot_instance.signal_technical_callback(update, context)
            
        # Sentiment analysis in signal flow
        elif callback_data.startswith("signal_flow_sentiment_") or callback_data == "signal_sentiment":
            logger.info(f"Routing to signal sentiment analysis")
            return await bot_instance.signal_sentiment_callback(update, context)
            
        # Calendar analysis in signal flow
        elif callback_data.startswith("signal_flow_calendar_") or callback_data == "signal_calendar":
            logger.info(f"Routing to signal calendar analysis")
            return await bot_instance.signal_calendar_callback(update, context)
            
        # Back to signal
        elif callback_data == "back_to_signal":
            logger.info(f"Routing to back to signal")
            return await bot_instance.back_to_signal_callback(update, context)
            
        # Back to signal analysis
        elif callback_data == "back_to_signal_analysis":
            logger.info(f"Routing to back to signal analysis")
            return await bot_instance.back_to_signal_analysis_callback(update, context)
            
        # If no specific signal flow handler, try pattern matching
        return await HandlerDispatcher._dispatch_by_pattern(update, context, callback_data, bot_instance)
    
    @staticmethod
    async def _dispatch_menu_flow(update, context, callback_data, bot_instance):
        """Handle menu flow callbacks"""
        # Market selection
        if callback_data.startswith("menu_analyse"):
            logger.info(f"Routing to menu analysis")
            return await bot_instance.menu_analyse_callback(update, context)
            
        # Signals management
        elif callback_data.startswith("menu_signals"):
            logger.info(f"Routing to menu signals")
            return await bot_instance.menu_signals_callback(update, context)
            
        # Market callbacks
        elif callback_data.startswith("market_"):
            logger.info(f"Routing to market callback")
            return await bot_instance.market_callback(update, context)
            
        # Instrument callbacks (not signals)
        elif callback_data.startswith("instrument_") and not callback_data.endswith("_signals"):
            logger.info(f"Routing to instrument callback")
            return await bot_instance.instrument_callback(update, context)
            
        # Instrument signals callbacks
        elif callback_data.startswith("instrument_") and callback_data.endswith("_signals"):
            logger.info(f"Routing to instrument signals callback")
            return await bot_instance.instrument_signals_callback(update, context)
            
        # Analysis in menu flow - technical
        elif callback_data == "analysis_technical":
            logger.info(f"Routing to analysis technical")
            return await bot_instance.analysis_technical_callback(update, context)
            
        # Analysis in menu flow - sentiment
        elif callback_data == "analysis_sentiment":
            logger.info(f"Routing to analysis sentiment")
            return await bot_instance.analysis_sentiment_callback(update, context)
            
        # Analysis in menu flow - calendar
        elif callback_data == "analysis_calendar":
            logger.info(f"Routing to analysis calendar")
            return await bot_instance.analysis_calendar_callback(update, context)
            
        # Back buttons
        elif callback_data == "back_market":
            logger.info(f"Routing to back market")
            return await bot_instance.back_market_callback(update, context)
        elif callback_data == "back_instrument":
            logger.info(f"Routing to back instrument")
            return await bot_instance.back_instrument_callback(update, context)
        elif callback_data == "back_signals":
            logger.info(f"Routing to back signals")
            return await bot_instance.back_signals_callback(update, context)
        elif callback_data == "back_menu":
            logger.info(f"Routing to back menu")
            return await bot_instance.back_menu_callback(update, context)
            
        # If no specific menu flow handler, try pattern matching
        return await HandlerDispatcher._dispatch_by_pattern(update, context, callback_data, bot_instance)
    
    @staticmethod
    async def _dispatch_by_pattern(update, context, callback_data, bot_instance):
        """Dispatch by pattern matching"""
        # Try to match callback data against known patterns
        if re.match(r"^menu_analyse$", callback_data):
            return await bot_instance.menu_analyse_callback(update, context)
        elif re.match(r"^menu_signals$", callback_data):
            return await bot_instance.menu_signals_callback(update, context)
        elif re.match(r"^signals_add$", callback_data):
            return await bot_instance.signals_add_callback(update, context)
        elif re.match(r"^signals_manage$", callback_data):
            return await bot_instance.signals_manage_callback(update, context)
        elif re.match(r"^market_", callback_data):
            return await bot_instance.market_callback(update, context)
        elif re.match(r"^instrument_(?!.*_signals)", callback_data):
            return await bot_instance.instrument_callback(update, context)
        elif re.match(r"^instrument_.*_signals$", callback_data):
            return await bot_instance.instrument_signals_callback(update, context)
        elif re.match(r"^back_market$", callback_data):
            return await bot_instance.back_market_callback(update, context)
        elif re.match(r"^back_instrument$", callback_data):
            return await bot_instance.back_instrument_callback(update, context)
        elif re.match(r"^back_signals$", callback_data):
            return await bot_instance.back_signals_callback(update, context)
        elif re.match(r"^back_menu$", callback_data):
            return await bot_instance.back_menu_callback(update, context)
        elif re.match(r"^analysis_technical$", callback_data):
            return await bot_instance.analysis_technical_callback(update, context)
        elif re.match(r"^analysis_sentiment$", callback_data):
            return await bot_instance.analysis_sentiment_callback(update, context)
        elif re.match(r"^analysis_calendar$", callback_data):
            return await bot_instance.analysis_calendar_callback(update, context)
        elif re.match(r"^signal_flow_technical_.*$", callback_data):
            return await bot_instance.signal_technical_callback(update, context)
        elif re.match(r"^signal_flow_sentiment_.*$", callback_data):
            return await bot_instance.signal_sentiment_callback(update, context)
        elif re.match(r"^signal_flow_calendar_.*$", callback_data):
            return await bot_instance.signal_calendar_callback(update, context)
        elif re.match(r"^signal_technical$", callback_data):
            return await bot_instance.signal_technical_callback(update, context)
        elif re.match(r"^signal_sentiment$", callback_data):
            return await bot_instance.signal_sentiment_callback(update, context)
        elif re.match(r"^signal_calendar$", callback_data):
            return await bot_instance.signal_calendar_callback(update, context)
        elif re.match(r"^back_to_signal$", callback_data):
            return await bot_instance.back_to_signal_callback(update, context)
        elif re.match(r"^back_to_signal_analysis$", callback_data):
            return await bot_instance.back_to_signal_analysis_callback(update, context)
        elif re.match(r"^analyze_from_signal_.*$", callback_data):
            return await bot_instance.analyze_from_signal_callback(update, context)
            
        # No specific handler found
        logger.warning(f"No specific handler found for callback: {callback_data}")
        return False
    
    @staticmethod
    def _extract_instrument(callback_data):
        """Extract instrument from callback data if present"""
        # Try to extract from signal flow technical pattern
        match = re.match(r"^signal_flow_technical_(.+)$", callback_data)
        if match:
            return match.group(1)
            
        # Try to extract from signal flow sentiment pattern
        match = re.match(r"^signal_flow_sentiment_(.+)$", callback_data)
        if match:
            return match.group(1)
            
        # Try to extract from signal flow calendar pattern
        match = re.match(r"^signal_flow_calendar_(.+)$", callback_data)
        if match:
            return match.group(1)
            
        # Try to extract from analyze_from_signal pattern
        match = re.match(r"^analyze_from_signal_(.+)$", callback_data)
        if match:
            return match.group(1)
            
        # Try to extract from instrument pattern
        match = re.match(r"^instrument_(.+?)(?:_signals)?$", callback_data)
        if match:
            return match.group(1)
            
        return None 