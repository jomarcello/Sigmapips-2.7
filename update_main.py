import re

# Read the file
with open('trading_bot/main.py', 'r') as f:
    content = f.read()

# Update the button_callback method to handle signal_flow patterns
pattern = r'(if callback_data\.startswith\("analyze_from_signal_"\):.*?return await self\.analyze_from_signal_callback\(update, context\))'
replacement = r'''if callback_data.startswith("analyze_from_signal_"):
                return await self.analyze_from_signal_callback(update, context)
                
            # Handle signal flow buttons
            if callback_data.startswith("signal_flow_technical_"):
                return await self.signal_technical_callback(update, context)
            
            if callback_data.startswith("signal_flow_sentiment_"):
                return await self.signal_sentiment_callback(update, context)
            
            if callback_data.startswith("signal_flow_calendar_"):
                return await self.signal_calendar_callback(update, context)'''

updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Update the signal_technical_callback method
pattern = r'(async def signal_technical_callback.*?# Get the instrument from context.*?instrument = None.*?if context and hasattr\(context, \'user_data\'\):.*?instrument = context\.user_data\.get\(\'instrument\'\).*?# Debug log for instrument.*?logger\.info\(f"Instrument from context: {instrument}"\))'
replacement = r'''\1
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_technical_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    context.user_data['instrument'] = instrument'''

updated_content = re.sub(pattern, replacement, updated_content, flags=re.DOTALL)

# Update the signal_sentiment_callback method
pattern = r'(async def signal_sentiment_callback.*?# Get the instrument from context.*?instrument = None.*?if context and hasattr\(context, \'user_data\'\):.*?instrument = context\.user_data\.get\(\'instrument\'\))'
replacement = r'''\1
            logger.info(f"Instrument from context: {instrument}")
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_sentiment_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    context.user_data['instrument'] = instrument'''

updated_content = re.sub(pattern, replacement, updated_content, flags=re.DOTALL)

# Write the updated content back to the file
with open('trading_bot/main.py', 'w') as f:
    f.write(updated_content)

print("Updates applied successfully") 