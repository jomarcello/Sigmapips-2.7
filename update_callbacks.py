import re

# Read the file
with open('trading_bot/main.py', 'r') as f:
    content = f.read()

# Update signal_technical_callback
technical_pattern = r'(async def signal_technical_callback.*?# Get the instrument from context.*?instrument = None.*?if context and hasattr\(context, \'user_data\'\):.*?instrument = context\.user_data\.get\(\'instrument\'\).*?# Debug log for instrument.*?logger\.info\(f"Instrument from context: {instrument}"\))'
technical_replacement = r'''\1
        
        # Check if the callback data contains an instrument (signal_flow pattern)
        if query.data.startswith("signal_flow_technical_"):
            parts = query.data.split("_")
            if len(parts) >= 4:
                instrument = parts[3]  # Extract instrument from callback data
                logger.info(f"Extracted instrument from callback data: {instrument}")
                # Save to context
                if context and hasattr(context, 'user_data'):
                    context.user_data['instrument'] = instrument'''

content = re.sub(technical_pattern, technical_replacement, content, flags=re.DOTALL)

# Update signal_sentiment_callback
sentiment_pattern = r'(async def signal_sentiment_callback.*?# Get the instrument from context.*?instrument = None.*?if context and hasattr\(context, \'user_data\'\):.*?instrument = context\.user_data\.get\(\'instrument\'\))'
sentiment_replacement = r'''\1
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

content = re.sub(sentiment_pattern, sentiment_replacement, content, flags=re.DOTALL)

# Write the updated content back to the file
with open('trading_bot/main.py', 'w') as f:
    f.write(content)

print("Callbacks updated successfully") 