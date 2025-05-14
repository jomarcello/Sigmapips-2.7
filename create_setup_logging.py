#!/usr/bin/env python3

def create_setup_logging(file_path):
    print(f"Creating setup_logging function in {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the problematic section
    start_marker = "# Apply the configuration"
    end_marker = "# Initialize logging early in the application startup"
    
    if start_marker in content and end_marker in content:
        # Extract the section before and after the problematic part
        before_section = content.split(start_marker)[0]
        after_section = content.split(end_marker)[1]
        
        # Create the new setup_logging function
        new_section = """# Apply the configuration
def setup_logging():
    \"\"\"Configure logging for the application\"\"\"
    import logging
    import logging.config
    import os
    import sys
    import json
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Set log file path
    log_file = os.path.join(log_dir, "trading_bot.log")
    
    # Determine log level from environment or default to INFO
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Configure logging
    logging.config.dictConfig(logging_config)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level {log_level}, writing to {log_file}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running on platform: {sys.platform}")
    
    # Log environment variables (excluding sensitive information)
    safe_env = {}
    for key, value in os.environ.items():
        if any(sensitive in key.lower() for sensitive in ['key', 'token', 'secret', 'password', 'pwd']):
            safe_env[key] = f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "[REDACTED]"
        else:
            safe_env[key] = value
    
    logger.debug(f"Environment variables: {json.dumps(safe_env, indent=2)}")
    
    return logger

# Initialize logging early in the application startup"""
        
        # Combine the sections
        new_content = before_section + new_section + after_section
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Created setup_logging function in {file_path}")
    else:
        print(f"Could not find the markers in {file_path}")

if __name__ == "__main__":
    create_setup_logging("trading_bot/main.py") 