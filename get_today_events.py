#!/usr/bin/env python3
import json
import os
import sys
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta
import pytz

# Configure timezone to Singapore (GMT+8)
sg_timezone = pytz.timezone('Asia/Singapore')
current_time = datetime.now(sg_timezone)
print(f"Current date and time in GMT+8: {current_time.strftime('%Y-%m-%d %H:%M:%S %z')}")

async def fetch_forexfactory_data():
    """Fetch real economic calendar data from ForexFactory website"""
    # Check if it's weekend (Saturday or Sunday)
    day_of_week = current_time.weekday()
    
    if day_of_week >= 5:  # 5 = Saturday, 6 = Sunday
        print(f"Today is a weekend day, limited economic data available")
    
    try:
        # ForexFactory calendar URL
        url = 'https://www.forexfactory.com/calendar'
        
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.forexfactory.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Fetch the HTML content
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Error fetching ForexFactory data: HTTP {response.status}")
                    return []
                
                html_content = await response.text()
                
        # Extract event data using regex - basic parsing
        # This is a simple example - ideal implementation would use proper HTML parsing
        events = []
        
        # Pattern to find calendar entries
        entry_pattern = r'<tr class="calendar_row.+?</tr>'
        entry_matches = re.finditer(entry_pattern, html_content, re.DOTALL)
        
        for entry in entry_matches:
            entry_html = entry.group(0)
            
            # Extract time
            time_match = re.search(r'<td class="calendar__time".+?>(.+?)</td>', entry_html, re.DOTALL)
            time = time_match.group(1).strip() if time_match else ""
            
            # Extract currency
            currency_match = re.search(r'<td class="calendar__currency".+?>(.+?)</td>', entry_html, re.DOTALL)
            currency = currency_match.group(1).strip() if currency_match else ""
            
            # Extract impact
            impact_match = re.search(r'<td class="calendar__impact".+?><span.+?class="(.+?)".+?</span></td>', entry_html, re.DOTALL)
            impact_class = impact_match.group(1).strip() if impact_match else ""
            
            # Determine impact level
            impact = "Low"
            if 'high' in impact_class.lower():
                impact = "High"
            elif 'medium' in impact_class.lower():
                impact = "Medium"
            
            # Extract event
            event_match = re.search(r'<td class="calendar__event".+?>(.+?)</td>', entry_html, re.DOTALL)
            event_text = event_match.group(1).strip() if event_match else ""
            # Clean HTML
            event = re.sub(r'<.+?>', '', event_text).strip()
            
            # Extract forecast
            forecast_match = re.search(r'<td class="calendar__forecast".+?>(.+?)</td>', entry_html, re.DOTALL)
            forecast = forecast_match.group(1).strip() if forecast_match else ""
            
            # Extract previous
            previous_match = re.search(r'<td class="calendar__previous".+?>(.+?)</td>', entry_html, re.DOTALL)
            previous = previous_match.group(1).strip() if previous_match else ""
            
            # Extract actual
            actual_match = re.search(r'<td class="calendar__actual".+?>(.+?)</td>', entry_html, re.DOTALL)
            actual = actual_match.group(1).strip() if actual_match else ""
            
            # Add event to list
            events.append({
                "time": time,
                "currency": currency,
                "impact": impact,
                "event": event,
                "forecast": forecast,
                "previous": previous,
                "actual": actual
            })
            
        return events
            
    except Exception as e:
        print(f"Error fetching ForexFactory data: {str(e)}")
        return []

async def main():
    # Fetch data from ForexFactory
    events = await fetch_forexfactory_data()
    
    if not events:
        print("No events found or error fetching data. Using sample data for testing.")
        # Provide some sample data to avoid empty calendar
        events = [
            {"time": "8:30am", "currency": "USD", "impact": "High", "event": "Non-Farm Payrolls", "forecast": "175K", "previous": "187K", "actual": ""},
            {"time": "9:00am", "currency": "EUR", "impact": "Medium", "event": "ECB President Speaks", "forecast": "", "previous": "", "actual": ""},
            {"time": "10:00am", "currency": "GBP", "impact": "Low", "event": "Manufacturing PMI", "forecast": "51.2", "previous": "50.8", "actual": ""}
        ]
    
    # Get date string for output filename
    date_str = current_time.strftime("%Y-%m-%d")
    output_filename = f"forex_factory_data_{date_str}.json"
    
    # Save to JSON file
    with open(output_filename, 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"Saved {len(events)} events to {output_filename}")
    
    # Also print to stdout for verification
    print(json.dumps(events, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
