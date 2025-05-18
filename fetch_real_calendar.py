#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import re
import sys
from datetime import datetime
import pytz
import logging

# Set up console for better output display
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see more information
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def fetch_forexfactory_calendar():
    """Fetch live ForexFactory calendar data"""
    print("🔍 Fetching real-time economic calendar data from ForexFactory...")
    
    # ForexFactory calendar URL - can specify dates with ?day=today, ?day=tomorrow, etc.
    url = "https://www.forexfactory.com/calendar?day=today"
    
    # Set up headers to mimic a browser to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.forexfactory.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        # Fetch the calendar page
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"⚠️ Error: HTTP status {response.status}")
                    return []
                
                html_content = await response.text()
                
                # Save HTML for debugging
                with open("forexfactory_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info("Saved HTML content to forexfactory_debug.html for inspection")
                
        # Extract and parse calendar data
        events = []
        
        # Look for table containing calendar data
        calendar_table_match = re.search(r'<table id="calendar_table".*?>(.*?)</table>', html_content, re.DOTALL)
        
        if not calendar_table_match:
            logger.error("Could not find calendar table in the HTML")
            print("⚠️ Could not find the economic calendar table in the HTML.")
            
            # Try alternative pattern - FF may have changed their HTML structure
            logger.info("Trying alternative patterns...")
            
            # Try to find any table that might contain calendar data
            tables = re.findall(r'<table.*?>(.*?)</table>', html_content, re.DOTALL)
            logger.info(f"Found {len(tables)} tables in the HTML")
            
            # Try to find rows with 'calendar' in class name
            calendar_rows = re.findall(r'<tr[^>]*?calendar[^>]*?>(.*?)</tr>', html_content, re.DOTALL)
            if calendar_rows:
                logger.info(f"Found {len(calendar_rows)} potential calendar rows using alternative pattern")
            else:
                return []
        else:
            calendar_table = calendar_table_match.group(1)
            logger.info("Found calendar table")
            
            # Extract rows from table
            calendar_rows = re.findall(r'<tr[^>]*?>(.*?)</tr>', calendar_table, re.DOTALL)
            logger.info(f"Found {len(calendar_rows)} rows in calendar table")
        
        if not calendar_rows:
            logger.error("No calendar rows found")
            print("⚠️ No calendar rows found in the HTML. Website structure may have changed.")
            return []
        
        print(f"📊 Found {len(calendar_rows)} potential economic events")
        
        # Impact emoji mapping
        impact_emoji = {
            "High": "🔴",
            "Medium": "🟠",
            "Low": "🟡"
        }
        
        # Currency flag mapping
        currency_flags = {
            "USD": "🇺🇸",
            "EUR": "🇪🇺",
            "GBP": "🇬🇧",
            "JPY": "🇯🇵",
            "AUD": "🇦🇺",
            "NZD": "🇳🇿",
            "CAD": "🇨🇦",
            "CHF": "🇨🇭",
            "CNY": "🇨🇳"
        }
        
        # Parse each calendar row - try multiple patterns to be more flexible
        valid_events = 0
        for row in calendar_rows:
            # Skip header rows or empty rows
            if 'calendar__row--header' in row or not row.strip():
                continue
                
            # Try multiple patterns for time
            time = "N/A"
            for pattern in [
                r'<td[^>]*?calendar__time[^>]*?>(.*?)</td>',
                r'<td[^>]*?time[^>]*?>(.*?)</td>',
                r'<td[^>]*?>(\d{1,2}:\d{2}[ap]m)</td>'
            ]:
                time_match = re.search(pattern, row, re.DOTALL)
                if time_match:
                    time = time_match.group(1).strip()
                    time = re.sub(r'<[^>]*?>', '', time)  # Remove any HTML tags
                    break
            
            # Try multiple patterns for currency
            currency = ""
            for pattern in [
                r'<td[^>]*?calendar__currency[^>]*?>(.*?)</td>',
                r'<td[^>]*?currency[^>]*?>(.*?)</td>'
            ]:
                currency_match = re.search(pattern, row, re.DOTALL)
                if currency_match:
                    currency = currency_match.group(1).strip()
                    currency = re.sub(r'<[^>]*?>', '', currency)  # Remove any HTML tags
                    break
            
            # Try to determine impact level
            impact = "Low"
            if re.search(r'high|red|important', row.lower(), re.DOTALL):
                impact = "High"
            elif re.search(r'medium|orange|moderate', row.lower(), re.DOTALL):
                impact = "Medium"
            
            # Try multiple patterns for event title
            event = "N/A"
            for pattern in [
                r'<td[^>]*?calendar__event[^>]*?>(.*?)</td>',
                r'<td[^>]*?event[^>]*?>(.*?)</td>'
            ]:
                event_match = re.search(pattern, row, re.DOTALL)
                if event_match:
                    event_html = event_match.group(1).strip()
                    event = re.sub(r'<[^>]*?>', '', event_html)  # Remove any HTML tags
                    break
            
            # Try multiple patterns for forecast
            forecast = ""
            for pattern in [
                r'<td[^>]*?calendar__forecast[^>]*?>(.*?)</td>',
                r'<td[^>]*?forecast[^>]*?>(.*?)</td>'
            ]:
                forecast_match = re.search(pattern, row, re.DOTALL)
                if forecast_match:
                    forecast = forecast_match.group(1).strip()
                    forecast = re.sub(r'<[^>]*?>', '', forecast)  # Remove any HTML tags
                    break
            
            # Try multiple patterns for previous
            previous = ""
            for pattern in [
                r'<td[^>]*?calendar__previous[^>]*?>(.*?)</td>',
                r'<td[^>]*?previous[^>]*?>(.*?)</td>'
            ]:
                previous_match = re.search(pattern, row, re.DOTALL)
                if previous_match:
                    previous = previous_match.group(1).strip()
                    previous = re.sub(r'<[^>]*?>', '', previous)  # Remove any HTML tags
                    break
            
            # Try multiple patterns for actual
            actual = ""
            for pattern in [
                r'<td[^>]*?calendar__actual[^>]*?>(.*?)</td>',
                r'<td[^>]*?actual[^>]*?>(.*?)</td>'
            ]:
                actual_match = re.search(pattern, row, re.DOTALL)
                if actual_match:
                    actual = actual_match.group(1).strip()
                    actual = re.sub(r'<[^>]*?>', '', actual)  # Remove any HTML tags
                    break
            
            # Only add event if we have at least event name or time
            if event != "N/A" or time != "N/A":
                valid_events += 1
                # Add to events list
                events.append({
                    "time": time,
                    "currency": currency,
                    "currency_flag": currency_flags.get(currency, ""),
                    "impact": impact,
                    "impact_emoji": impact_emoji.get(impact, "🟡"),
                    "event": event,
                    "forecast": forecast,
                    "previous": previous,
                    "actual": actual
                })
        
        logger.info(f"Extracted {valid_events} valid events")
        return events
    
    except Exception as e:
        logger.error(f"Error fetching ForexFactory data: {str(e)}", exc_info=True)
        print(f"⚠️ Error fetching ForexFactory data: {str(e)}")
        return []

def format_event_list(events):
    """Format event list for display in the terminal"""
    if not events:
        return "No economic events found for today."
    
    # Get current date in Singapore timezone (GMT+8)
    sg_time = datetime.now(pytz.timezone('Asia/Singapore'))
    date_str = sg_time.strftime("%Y-%m-%d")
    
    # Format header
    output = f"\n📅 ECONOMIC CALENDAR FOR {date_str}\n"
    output += "=" * 80 + "\n\n"
    
    # Create table header
    output += f"{'TIME':<10} {'CURRENCY':<10} {'IMPACT':<10} {'EVENT':<30} {'FORECAST':<10} {'PREVIOUS':<10} {'ACTUAL':<10}\n"
    output += "-" * 80 + "\n"
    
    # Add each event
    for event in events:
        time = event.get('time', 'N/A')
        currency = f"{event.get('currency_flag', '')} {event.get('currency', '')}"
        impact = f"{event.get('impact_emoji', '🟡')} {event.get('impact', 'Low')}"
        title = event.get('event', 'N/A')
        forecast = event.get('forecast', '')
        previous = event.get('previous', '')
        actual = event.get('actual', '')
        
        output += f"{time:<10} {currency:<10} {impact:<10} {title[:30]:<30} {forecast:<10} {previous:<10} {actual:<10}\n"
    
    return output

async def main():
    # Fetch real-time economic calendar data
    events = await fetch_forexfactory_calendar()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname("real_forex_factory_data.json")
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get current date
    current_date = datetime.now(pytz.timezone('Asia/Singapore')).strftime("%Y-%m-%d")
    
    # Format and display events
    if not events:
        print(f"\n📅 ECONOMIC CALENDAR FOR {current_date}")
        print("="*80)
        print("\nℹ️ No economic events today (weekend or holiday).")
        
        # Save empty list to JSON
        with open("real_forex_factory_data.json", "w") as f:
            json.dump([], f, indent=2)
            
        # Update calendar service data file as well
        with open(f"forex_factory_data_{current_date}.json", "w") as f:
            json.dump([], f, indent=2)
            
        print(f"\n✅ Saved empty event list to real_forex_factory_data.json")
        print(f"✅ Updated calendar service data file: forex_factory_data_{current_date}.json")
        return
    
    # If we have events, format them for display    
    formatted_calendar = format_event_list(events)
    
    # Save to JSON for API use
    with open("real_forex_factory_data.json", "w") as f:
        json.dump(events, f, indent=2)
        
    # Also save in format used by calendar service
    with open(f"forex_factory_data_{current_date}.json", "w") as f:
        json.dump(events, f, indent=2)
        
    print(f"✅ Saved {len(events)} economic events to real_forex_factory_data.json")
    print(f"✅ Updated calendar service data file: forex_factory_data_{current_date}.json")

if __name__ == "__main__":
    asyncio.run(main()) 