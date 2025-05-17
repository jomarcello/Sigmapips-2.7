#!/usr/bin/env python3
import asyncio
import logging
import sys

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
    
    # Get the economic calendar
    print("Fetching economic calendar data...")
    calendar_data = await calendar_service.get_economic_calendar()
    
    # Print the results
    print("\n===== ECONOMIC CALENDAR =====\n")
    print(calendar_data)
    
    # If get_economic_calendar returns a string, also try the get_calendar method
    if isinstance(calendar_data, str):
        print("\nTrying alternative calendar method...")
        events = await calendar_service.get_calendar()
        print("\n===== CALENDAR EVENTS =====\n")
        for event in events:
            print(f"{event.get('time', 'N/A')} - {event.get('impact', 'N/A')} - {event.get('country', 'N/A')} - {event.get('event', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main()) 