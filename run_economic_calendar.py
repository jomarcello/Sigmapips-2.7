#!/usr/bin/env python3
import asyncio
import logging
import sys
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Import the EconomicCalendarService
from trading_bot.services.calendar_service import EconomicCalendarService

async def main():
    # Create an instance of the EconomicCalendarService
    calendar_service = EconomicCalendarService()
    
    # Get current date
    current_date = datetime.now(pytz.timezone('Asia/Singapore')).strftime("%Y-%m-%d")
    
    # Get the economic calendar
    print("Fetching economic calendar data...")
    calendar_data = await calendar_service.get_economic_calendar()
    
    # Print the results
    print("\n===== ECONOMIC CALENDAR =====\n")
    
    # Check if we got a string with "No events" or similar
    if calendar_data and isinstance(calendar_data, str) and ("No events" in calendar_data or len(calendar_data.strip()) < 10):
        print(f"ℹ️ No economic events today ({current_date}) - weekend or holiday.")
    else:
        print(calendar_data)
    
    # If we need the raw events, try the get_calendar method
    print("\nFetching raw calendar events...")
    events = await calendar_service.get_calendar()
    
    print("\n===== CALENDAR EVENTS =====\n")
    
    if not events:
        print(f"ℹ️ No economic events today ({current_date}) - weekend or holiday.")
    else:
        for event in events:
            print(f"{event.get('time', 'N/A')} - {event.get('impact_emoji', event.get('impact', 'N/A'))} - {event.get('currency_flag', event.get('currency', 'N/A'))} - {event.get('event', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main()) 