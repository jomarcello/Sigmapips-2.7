"""
Simple chronological economic calendar formatter for TradingView API data.
This module is designed to format economic calendar events from the TradingView API
in chronological order by time.

It is intended to work with existing calendar service implementations that already
handle the API integration, such as the trading_bot.services.calendar_service.tradingview_calendar
service.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

# Configureer logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Definieer de major currencies
MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "NZD", "CAD"]

# Emoji's voor valuta vlaggen
CURRENCY_FLAGS = {
    "USD": "🇺🇸",
    "EUR": "🇪🇺",
    "GBP": "🇬🇧",
    "JPY": "🇯🇵",
    "CHF": "🇨🇭",
    "AUD": "🇦🇺",
    "NZD": "🇳🇿",
    "CAD": "🇨🇦"
}

# Emoji's voor impact levels
IMPACT_EMOJI = {
    "High": "🔴",
    "Medium": "🟠",
    "Low": "🟢"
}

def format_calendar_events_chronologically(events: List[Dict], today_formatted: str = None) -> str:
    """
    Format calendar events in chronological order by time.
    
    Args:
        events: List of calendar events with at least 'time', 'country', 'impact', 'event' fields
        today_formatted: Optional formatted date string to use in the header
        
    Returns:
        Formatted calendar text with events in chronological order by time
    """
    if not events:
        today_str = today_formatted or datetime.now().strftime("%A, %d %B %Y")
        return f"📅 Economic Calendar for {today_str}\n\nNo economic events found for today."
    
    # Get today's date if not provided
    if not today_formatted:
        today_formatted = datetime.now().strftime("%A, %d %B %Y")
    
    # Format the calendar header
    output = [f"📅 Economic Calendar for {today_formatted}\n"]
    output.append("Impact: 🔴 High   🟠 Medium   🟢 Low\n")
    
    # Sort events by time if not already sorted
    if all('datetime' in event for event in events):
        events = sorted(events, key=lambda x: x["datetime"])
    elif all('time' in event for event in events):
        events = sorted(events, key=lambda x: x["time"])
    
    # Add each event in chronological order
    for event in events:
        time = event.get('time', '00:00')
        impact_emoji = event.get('impact_emoji', IMPACT_EMOJI.get(event.get('impact', 'Low'), "⚪"))
        title = event.get('event', 'Economic Event')
        
        # Get currency and flag
        currency = event.get('country', '')
        flag = event.get('flag', CURRENCY_FLAGS.get(currency, "🌐"))
        
        # Add forecast and previous values if available
        forecast = event.get('forecast')
        previous = event.get('previous')
        
        extra_info = []
        if forecast is not None:
            extra_info.append(f"F: {forecast}")
        if previous is not None:
            extra_info.append(f"P: {previous}")
        
        extra_str = f" ({', '.join(extra_info)})" if extra_info else ""
        
        # Add fallback indicator if applicable
        is_fallback = event.get('is_fallback', False)
        fallback_str = " [Est]" if is_fallback else ""
        
        # Format the event line
        output.append(f"{time} - {flag} {currency} - {impact_emoji} {title}{extra_str}{fallback_str}")
    
    return "\n".join(output)

def format_calendar_events_by_currency(events: List[Dict], today_formatted: str = None) -> str:
    """
    Format calendar events grouped by currency with chronological order within each group.
    
    Args:
        events: List of calendar events with at least 'time', 'country', 'impact', 'event' fields
        today_formatted: Optional formatted date string to use in the header
        
    Returns:
        Formatted calendar text with events grouped by currency
    """
    if not events:
        today_str = today_formatted or datetime.now().strftime("%A, %d %B %Y")
        return f"📅 Economic Calendar for {today_str}\n\nNo economic events found for today."
    
    # Get today's date if not provided
    if not today_formatted:
        today_formatted = datetime.now().strftime("%A, %d %B %Y")
    
    # Format the calendar header
    output = [f"📅 Economic Calendar for {today_formatted}\n"]
    output.append("Impact: 🔴 High   🟠 Medium   🟢 Low\n")
    
    # Group events by currency
    events_by_currency = {}
    for event in events:
        currency = event.get('country', '')
        if currency not in events_by_currency:
            events_by_currency[currency] = []
        events_by_currency[currency].append(event)
    
    # Sort events within each currency group by time
    for currency in events_by_currency:
        if all('datetime' in event for event in events_by_currency[currency]):
            events_by_currency[currency] = sorted(events_by_currency[currency], key=lambda x: x["datetime"])
        elif all('time' in event for event in events_by_currency[currency]):
            events_by_currency[currency] = sorted(events_by_currency[currency], key=lambda x: x["time"])
    
    # Add each currency section
    for currency in MAJOR_CURRENCIES:
        if currency in events_by_currency:
            currency_events = events_by_currency[currency]
            flag = CURRENCY_FLAGS.get(currency, "🌐")
            
            # Add currency header
            output.append(f"{flag} {currency}")
            
            # Add events for this currency
            for event in currency_events:
                time = event.get('time', '00:00')
                impact_emoji = event.get('impact_emoji', IMPACT_EMOJI.get(event.get('impact', 'Low'), "⚪"))
                title = event.get('event', 'Economic Event')
                
                # Add forecast and previous values if available
                forecast = event.get('forecast')
                previous = event.get('previous')
                
                extra_info = []
                if forecast is not None:
                    extra_info.append(f"F: {forecast}")
                if previous is not None:
                    extra_info.append(f"P: {previous}")
                
                extra_str = f" ({', '.join(extra_info)})" if extra_info else ""
                
                # Add fallback indicator if applicable
                is_fallback = event.get('is_fallback', False)
                fallback_str = " [Est]" if is_fallback else ""
                
                # Format the event line
                output.append(f"  {time} - {impact_emoji} {title}{extra_str}{fallback_str}")
            
            # Add blank line between currencies
            output.append("")
    
    return "\n".join(output)

# Function to integrate with existing trading_bot calendar service
def format_bot_calendar_events(events, group_by_currency=False, today_formatted=None):
    """
    Format calendar events for the trading bot.
    
    Args:
        events: List of calendar events from the trading bot's calendar service
        group_by_currency: Whether to group events by currency (default: False)
        today_formatted: Optional formatted date string to use in the header
        
    Returns:
        Formatted calendar text
    """
    if group_by_currency:
        return format_calendar_events_by_currency(events, today_formatted)
    else:
        return format_calendar_events_chronologically(events, today_formatted) 