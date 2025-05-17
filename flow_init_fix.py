#!/usr/bin/env python3

def fix_flow_initialization():
    """Update flow initialization in the TelegramService class"""
    with open('trading_bot/main.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create a backup first
    with open('trading_bot/main.py.backup_flow_init', 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Find the menu_command method
    menu_start = content.find("async def menu_command(self, update, context):")
    if menu_start == -1:
        print("Could not find menu_command method")
        return
    
    # Find the end of the menu_command method (next async def)
    menu_end = content.find("async def", menu_start + 10)
    if menu_end == -1:
        print("Could not find the end of menu_command method")
        return
    
    # Extract the menu_command method
    menu_command = content[menu_start:menu_end]
    
    # Create the updated menu_command method with flow management
    updated_menu_command = '''async def menu_command(self, update, context):
        """
        Handle /menu command - display the main menu 
        and set the menu flow context
        """
        try:
            from trading_bot.utils.flow_manager import FlowManager, FlowType
            
            # Set the flow to MENU
            FlowManager.set_flow(context, FlowType.MENU)
            logger.info("Set flow to MENU")
            
            # Create inline keyboard with menu options
            keyboard = [
                [InlineKeyboardButton("📊 Analyze Markets", callback_data="menu_analyse")],
                [InlineKeyboardButton("🔔 Manage Signals", callback_data="menu_signals")]
            ]
            
            # Add AI Assistant if enabled
            if os.environ.get("AI_SERVICES_ENABLED", "false").lower() == "true":
                keyboard.append([InlineKeyboardButton("🤖 AI Assistant", callback_data="menu_ai")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message with menu options
            await update.message.reply_text(
                "Welcome to SigmaPips Trading Bot! Please select an option:",
                reply_markup=reply_markup
            )
            
            logger.info(f"Menu displayed for user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in menu_command: {str(e)}")
            logger.exception(e)
            await update.message.reply_text(
                "An error occurred while displaying the menu. Please try again."
            )
    '''
    
    # Replace the old method with the updated one
    updated_content = content[:menu_start] + updated_menu_command + content[menu_end:]
    
    # Find the analyze_from_signal_callback method
    signal_start = updated_content.find("async def analyze_from_signal_callback(self, update, context):")
    if signal_start == -1:
        print("Could not find analyze_from_signal_callback method")
        with open('trading_bot/main.py', 'w', encoding='utf-8') as file:
            file.write(updated_content)
        return
    
    # Find the end of the analyze_from_signal_callback method (next async def)
    signal_end = updated_content.find("async def", signal_start + 10)
    if signal_end == -1:
        print("Could not find the end of analyze_from_signal_callback method")
        with open('trading_bot/main.py', 'w', encoding='utf-8') as file:
            file.write(updated_content)
        return
    
    # Extract the analyze_from_signal_callback method
    analyze_from_signal = updated_content[signal_start:signal_end]
    
    # Create the updated analyze_from_signal_callback method with flow management
    updated_analyze_from_signal = '''async def analyze_from_signal_callback(self, update, context):
        """
        Handle analyze button from signal message - display analysis options for the signal instrument
        and set the signal flow context
        """
        try:
            from trading_bot.utils.flow_manager import FlowManager, FlowType
            
            query = update.callback_query
            await query.answer()
            
            callback_data = query.data
            parts = callback_data.split("_")
            
            # Extract signal ID and instrument from callback data
            if len(parts) >= 4:
                signal_id = parts[3]
                
                # If the callback has an instrument, use it
                instrument = None
                if len(parts) >= 5:
                    instrument = parts[4]
                
                logger.info(f"Analyze from signal: {signal_id}, instrument: {instrument}")
                
                # Store signal ID in context
                context.user_data['signal_id'] = signal_id
                
                # Set the flow to SIGNAL with metadata
                metadata = {'signal_id': signal_id}
                if instrument:
                    metadata['instrument'] = instrument
                
                FlowManager.set_flow(context, FlowType.SIGNAL, metadata)
                logger.info(f"Set flow to SIGNAL with metadata: {metadata}")
                
                # Fetch the signal from storage
                signal = await self._get_signal_from_storage(signal_id)
                
                if signal:
                    # Extract instrument if not already provided
                    if not instrument and 'instrument' in signal:
                        instrument = signal['instrument']
                        context.user_data['instrument'] = instrument
                    
                    # Build analysis keyboard for the instrument
                    keyboard = [
                        [
                            InlineKeyboardButton("📈 Technical", callback_data=f"signal_flow_technical_{instrument}"),
                            InlineKeyboardButton("📊 Sentiment", callback_data=f"signal_flow_sentiment_{instrument}"),
                        ],
                        [
                            InlineKeyboardButton("📅 Economic Calendar", callback_data=f"signal_flow_calendar_{instrument}")
                        ],
                        [
                            InlineKeyboardButton("⬅️ Back to Signal", callback_data="back_to_signal")
                        ]
                    ]
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # Send analysis options
                    await query.edit_message_text(
                        f"Analysis options for {instrument} from Signal #{signal_id}:",
                        reply_markup=reply_markup
                    )
                    
                    logger.info(f"Signal analysis menu displayed for user {update.effective_user.id}, instrument: {instrument}")
                    
                else:
                    logger.warning(f"Signal {signal_id} not found in storage")
                    await query.edit_message_text(
                        f"Sorry, signal #{signal_id} is no longer available. Use /menu to return to the main menu.",
                        reply_markup=None
                    )
            else:
                logger.error(f"Invalid callback data format: {callback_data}")
                await query.edit_message_text(
                    "Invalid callback data. Use /menu to return to the main menu.",
                    reply_markup=None
                )
                
        except Exception as e:
            logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
            logger.exception(e)
            try:
                await update.effective_message.edit_text(
                    "An error occurred while processing your request. "
                    "Please try again or use /menu to return to the main menu.",
                    reply_markup=None
                )
            except Exception as reply_e:
                logger.error(f"Could not send error message: {str(reply_e)}")
    '''
    
    # Replace the old method with the updated one
    updated_content = updated_content[:signal_start] + updated_analyze_from_signal + updated_content[signal_end:]
    
    # Write the fixed content back to the file
    with open('trading_bot/main.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("Fixed flow initialization methods")

if __name__ == "__main__":
    fix_flow_initialization() 