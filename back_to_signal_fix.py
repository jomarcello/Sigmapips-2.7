async def back_to_signal_callback(self, update: Update, context=None) -> int:
    """Handle back_to_signal button press"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Get the current signal being viewed
        user_id = update.effective_user.id
        
        # First try to get signal data from backup in context
        signal_instrument = None
        signal_direction = None
        signal_timeframe = None
        
        if context and hasattr(context, 'user_data'):
            # Try to get from backup fields first (these are more reliable after navigation)
            signal_instrument = context.user_data.get('signal_instrument_backup') or context.user_data.get('signal_instrument')
            signal_direction = context.user_data.get('signal_direction_backup') or context.user_data.get('signal_direction')
            signal_timeframe = context.user_data.get('signal_timeframe_backup') or context.user_data.get('signal_timeframe')
            
            # Set both signal flow flags to ensure proper context is maintained
            context.user_data['from_signal'] = True
            context.user_data['in_signal_flow'] = True
            
            # Log retrieved values for debugging
            logger.info(f"Retrieved signal data from context: instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
            logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
        
        # Find the most recent signal for this user based on context data
        signal_data = None
        signal_id = None
        
        # Find matching signal based on instrument and direction
        if str(user_id) in self.user_signals:
            user_signal_dict = self.user_signals[str(user_id)]
            # Find signals matching instrument, direction and timeframe
            matching_signals = []
            
            for sig_id, sig in user_signal_dict.items():
                instrument_match = sig.get('instrument') == signal_instrument
                direction_match = True  # Default to true if we don't have direction data
                timeframe_match = True  # Default to true if we don't have timeframe data
                
                if signal_direction:
                    direction_match = sig.get('direction') == signal_direction
                if signal_timeframe:
                    timeframe_match = sig.get('interval') == signal_timeframe
                
                if instrument_match and direction_match and timeframe_match:
                    matching_signals.append((sig_id, sig))
            
            # Sort by timestamp, newest first
            if matching_signals:
                matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                signal_id, signal_data = matching_signals[0]
                logger.info(f"Found matching signal with ID: {signal_id}")
            else:
                logger.warning(f"No matching signals found for instrument={signal_instrument}, direction={signal_direction}, timeframe={signal_timeframe}")
                # If no exact match, try with just the instrument
                matching_signals = []
                for sig_id, sig in user_signal_dict.items():
                    if sig.get('instrument') == signal_instrument:
                        matching_signals.append((sig_id, sig))
                
                if matching_signals:
                    matching_signals.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                    signal_id, signal_data = matching_signals[0]
                    logger.info(f"Found signal with just instrument match, ID: {signal_id}")
        
        if not signal_data:
            # Try to get signal from database if we have signal_id in context
            signal_id_from_context = context.user_data.get('signal_id_backup') if context and hasattr(context, 'user_data') else None
            
            if signal_id_from_context and hasattr(self, 'db') and self.db:
                logger.info(f"Trying to retrieve signal {signal_id_from_context} from database")
                try:
                    signal_data = await self.db.get_signal(user_id, signal_id_from_context)
                    if signal_data:
                        signal_id = signal_id_from_context
                        logger.info(f"Retrieved signal {signal_id} from database")
                        
                        # Store in memory for future use
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                        
                        user_str_id = str(user_id)
                        if user_str_id not in self.user_signals:
                            self.user_signals[user_str_id] = {}
                            
                        self.user_signals[user_str_id][signal_id] = signal_data
                except Exception as db_error:
                    logger.error(f"Error retrieving signal from database: {str(db_error)}")
            
            # If still no signal data, try to get signals for this instrument from database
            if not signal_data and signal_instrument and hasattr(self, 'db') and self.db:
                logger.info(f"Trying to retrieve signals for instrument {signal_instrument} from database")
                try:
                    signals = await self.db.get_user_signals(user_id, signal_instrument)
                    if signals and len(signals) > 0:
                        # Use the most recent signal
                        signal_data = signals[0]  # Already sorted by timestamp, newest first
                        signal_id = signal_data.get('id')
                        logger.info(f"Retrieved signal {signal_id} for instrument {signal_instrument} from database")
                        
                        # Store in memory for future use
                        if not hasattr(self, 'user_signals'):
                            self.user_signals = {}
                        
                        user_str_id = str(user_id)
                        if user_str_id not in self.user_signals:
                            self.user_signals[user_str_id] = {}
                            
                        self.user_signals[user_str_id][signal_id] = signal_data
                except Exception as db_error:
                    logger.error(f"Error retrieving signals from database: {str(db_error)}")
        
        if not signal_data:
            # Fallback message if signal not found
            await query.edit_message_text(
                text="Signal not found. Please use the main menu to continue.",
                reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
            )
            return MENU
        
        # Show the signal details with analyze button
        # Prepare analyze button with signal info embedded
        keyboard = [
            [InlineKeyboardButton("🔍 Analyze Market", callback_data=f"analyze_from_signal_{signal_instrument}_{signal_id}")]
        ]
        
        # Get the formatted message from the signal
        signal_message = signal_data.get('message', "Signal details not available.")
        
        # Edit current message to show signal
        await query.edit_message_text(
            text=signal_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        
        return SIGNAL_DETAILS
        
    except Exception as e:
        logger.error(f"Error in back_to_signal_callback: {str(e)}")
        
        # Error recovery
        try:
            await query.edit_message_text(
                text="An error occurred. Please try again from the main menu.",
                reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
            )
        except Exception:
            pass
        
        return MENU 