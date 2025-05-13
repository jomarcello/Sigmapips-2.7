#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime, timedelta
import pytz

# Set timezone to GMT+8
gmt8 = pytz.timezone('Asia/Singapore')

# Get current date in GMT+8
now_gmt8 = datetime.now(pytz.UTC).astimezone(gmt8)
date_str = now_gmt8.strftime("%Y-%m-%d")
formatted_date = now_gmt8.strftime("%A, %B %d, %Y")

print(f"Current date and time in GMT+8: {now_gmt8.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Using predefined calendar data for {formatted_date}")

# Predefined events for May 13, 2025
events = [
    {"time": "12:00am", "currency": "GBP", "impact": "Low", "event": "MPC Member Taylor Speaks", "actual": "", "forecast": "", "previous": ""},
    {"time": "2:00am", "currency": "USD", "impact": "Low", "event": "Federal Budget Balance", "actual": "", "forecast": "256.4B", "previous": "-160.5B"},
    {"time": "Tentative", "currency": "USD", "impact": "Low", "event": "Loan Officer Survey", "actual": "", "forecast": "", "previous": ""},
    {"time": "7:01am", "currency": "GBP", "impact": "Low", "event": "BRC Retail Sales Monitor y/y", "actual": "", "forecast": "2.4%", "previous": "0.9%"},
    {"time": "7:50am", "currency": "JPY", "impact": "Low", "event": "BOJ Summary of Opinions", "actual": "", "forecast": "", "previous": ""},
    {"time": "", "currency": "JPY", "impact": "Low", "event": "M2 Money Stock y/y", "actual": "", "forecast": "0.6%", "previous": "0.8%"},
    {"time": "8:30am", "currency": "AUD", "impact": "Low", "event": "Westpac Consumer Sentiment", "actual": "", "forecast": "", "previous": "-6.0%"},
    {"time": "9:30am", "currency": "AUD", "impact": "Low", "event": "NAB Business Confidence", "actual": "", "forecast": "", "previous": "-3"},
    {"time": "11:35am", "currency": "JPY", "impact": "Low", "event": "30-y Bond Auction", "actual": "", "forecast": "", "previous": "2.41|3.0"},
    {"time": "2:00pm", "currency": "GBP", "impact": "High", "event": "Claimant Count Change", "actual": "", "forecast": "22.3K", "previous": "18.7K"},
    {"time": "", "currency": "GBP", "impact": "Medium", "event": "Average Earnings Index 3m/y", "actual": "", "forecast": "5.2%", "previous": "5.6%"},
    {"time": "", "currency": "GBP", "impact": "Low", "event": "Unemployment Rate", "actual": "", "forecast": "4.5%", "previous": "4.4%"},
    {"time": "Tentative", "currency": "CNY", "impact": "Low", "event": "New Loans", "actual": "", "forecast": "710B", "previous": "3640B"},
    {"time": "Tentative", "currency": "CNY", "impact": "Low", "event": "M2 Money Supply y/y", "actual": "", "forecast": "7.2%", "previous": "7.0%"},
    {"time": "All Day", "currency": "EUR", "impact": "Low", "event": "ECOFIN Meetings", "actual": "", "forecast": "", "previous": ""},
    {"time": "4:45pm", "currency": "GBP", "impact": "Low", "event": "MPC Member Pill Speaks", "actual": "", "forecast": "", "previous": ""},
    {"time": "5:00pm", "currency": "EUR", "impact": "Medium", "event": "German ZEW Economic Sentiment", "actual": "", "forecast": "10.7", "previous": "-14.0"},
    {"time": "", "currency": "EUR", "impact": "Low", "event": "ZEW Economic Sentiment", "actual": "", "forecast": "-3.5", "previous": "-18.5"},
    {"time": "6:00pm", "currency": "USD", "impact": "Low", "event": "NFIB Small Business Index", "actual": "", "forecast": "94.9", "previous": "97.4"},
    {"time": "8:30pm", "currency": "USD", "impact": "High", "event": "Core CPI m/m", "actual": "", "forecast": "0.3%", "previous": "0.1%"},
    {"time": "", "currency": "USD", "impact": "High", "event": "CPI m/m", "actual": "", "forecast": "0.3%", "previous": "-0.1%"},
    {"time": "", "currency": "USD", "impact": "High", "event": "CPI y/y", "actual": "", "forecast": "2.4%", "previous": "2.4%"},
    {"time": "9:30pm", "currency": "GBP", "impact": "Low", "event": "CB Leading Index m/m", "actual": "", "forecast": "", "previous": "-0.3%"},
    {"time": "11:00pm", "currency": "GBP", "impact": "High", "event": "BOE Gov Bailey Speaks", "actual": "", "forecast": "", "previous": ""}
]

# Create calendar data
calendar_data = {
    "date": formatted_date,
    "events": events
}

# Save to JSON file
json_file = f"forex_factory_data_{date_str}.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(calendar_data, f, indent=2)
print(f"Calendar data saved to {json_file}")

# Format events for text display
impact_emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟡"}
currency_flags = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵", "CHF": "🇨🇭",
    "AUD": "🇦🇺", "NZD": "🇳🇿", "CAD": "🇨🇦", "CNY": "🇨🇳", "HKD": "🇭🇰"
}

text_output = f"ForexFactory Economic Calendar for {formatted_date} (GMT+8)\n"
text_output += "=" * 80 + "\n\n"
text_output += "| Tijd      | Valuta | Impact | Evenement                       | Actueel | Verwacht | Vorig    |\n"
text_output += "|-----------|--------|--------|--------------------------------|---------|----------|----------|\n"

for event in events:
    time = event["time"].ljust(10)
    currency_flag = currency_flags.get(event["currency"], "")
    currency = f"{currency_flag} {event['currency']}".ljust(8)
    impact_icon = impact_emoji.get(event["impact"], "🟡").ljust(8)
    title = event["event"].ljust(32)
    actual = event["actual"].ljust(9)
    forecast = event["forecast"].ljust(10)
    previous = event["previous"].ljust(10)
    
    text_output += f"| {time} | {currency} | {impact_icon} | {title} | {actual} | {forecast} | {previous} |\n"

# Save formatted events to text file
txt_file = f"forex_factory_events_{date_str}.txt"
with open(txt_file, "w", encoding="utf-8") as f:
    f.write(text_output)
print(f"Formatted events saved to {txt_file}")
