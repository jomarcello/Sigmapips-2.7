import requests
import logging
import argparse
import os
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_webhook_info(bot_token):
    """Check current webhook configuration"""
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("ok"):
            webhook_info = data.get("result", {})
            current_url = webhook_info.get("url", "Not set")
            pending_updates = webhook_info.get("pending_update_count", 0)
            
            logger.info(f"Current webhook URL: {current_url}")
            logger.info(f"Pending updates: {pending_updates}")
            
            # Return current webhook info
            return webhook_info
        else:
            logger.error(f"Error getting webhook info: {data.get('description')}")
            return None
    except Exception as e:
        logger.error(f"Error checking webhook: {str(e)}")
        return None

def delete_webhook(bot_token, drop_pending=True):
    """Delete the current webhook"""
    url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    params = {"drop_pending_updates": "true" if drop_pending else "false"}
    
    try:
        response = requests.post(url, params=params)
        data = response.json()
        
        if data.get("ok"):
            logger.info("Webhook deleted successfully")
            return True
        else:
            logger.error(f"Error deleting webhook: {data.get('description')}")
            return False
    except Exception as e:
        logger.error(f"Error deleting webhook: {str(e)}")
        return False

def set_webhook(bot_token, webhook_url):
    """Set a new webhook URL"""
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    params = {
        "url": webhook_url,
        "allowed_updates": ["message", "callback_query", "inline_query"]
    }
    
    try:
        response = requests.post(url, params=params)
        data = response.json()
        
        if data.get("ok"):
            logger.info(f"Webhook set successfully to: {webhook_url}")
            return True
        else:
            logger.error(f"Error setting webhook: {data.get('description')}")
            return False
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}")
        return False

def main():
    """Main function to configure the webhook"""
    parser = argparse.ArgumentParser(description="Configure Telegram webhook")
    parser.add_argument("--bot-token", type=str, help="Telegram bot token")
    parser.add_argument("--webhook-url", type=str, help="Webhook URL to set")
    parser.add_argument("--delete", action="store_true", help="Delete the webhook")
    parser.add_argument("--check", action="store_true", help="Check webhook configuration")
    
    args = parser.parse_args()
    
    # Get bot token from args or environment
    bot_token = args.bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("No bot token provided. Use --bot-token or set TELEGRAM_BOT_TOKEN environment variable.")
        sys.exit(1)
    
    # Check current webhook configuration
    webhook_info = check_webhook_info(bot_token)
    
    # Delete webhook if requested
    if args.delete:
        logger.info("Deleting webhook...")
        if delete_webhook(bot_token):
            logger.info("Webhook deleted successfully")
        else:
            logger.error("Failed to delete webhook")
    
    # Set new webhook if URL provided
    if args.webhook_url:
        webhook_url = args.webhook_url
        
        # If URL has no path, add the standard /webhook path
        if not webhook_url.endswith("/webhook"):
            if webhook_url.endswith("/"):
                webhook_url = f"{webhook_url}webhook"
            else:
                webhook_url = f"{webhook_url}/webhook"
        
        logger.info(f"Setting webhook to: {webhook_url}")
        
        # Delete existing webhook first
        delete_webhook(bot_token)
        
        # Set new webhook
        if set_webhook(bot_token, webhook_url):
            logger.info("Webhook configured successfully")
        else:
            logger.error("Failed to set webhook")
    
    # Final check
    if args.webhook_url or args.check:
        logger.info("Final webhook configuration:")
        check_webhook_info(bot_token)

if __name__ == "__main__":
    main() 