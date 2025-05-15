#!/usr/bin/env python3
"""
Simple script to get the chat ID of users who message the bot
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    await update.message.reply_text(
        f'Hi {user.first_name}! Your chat ID is: {chat_id}'
    )
    logger.info(f"User {user.first_name} ({user.id}) has chat ID: {chat_id}")

async def echo(update: Update, context) -> None:
    """Echo the user message and show chat ID."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    await update.message.reply_text(
        f'You said: {update.message.text}\nYour chat ID is: {chat_id}'
    )
    logger.info(f"User {user.first_name} ({user.id}) with chat ID {chat_id} sent: {update.message.text}")

async def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = "7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk"
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot
    logger.info("Bot started. Send a message to get your chat ID.")
    
    # Gebruik de aanbevolen methode om de bot te starten
    await application.initialize()
    await application.updater.start_polling()

if __name__ == '__main__':
    import asyncio
    try:
        # Gebruik een nieuw event loop patroon dat beter omgaat met fouten
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error running bot: {e}") 