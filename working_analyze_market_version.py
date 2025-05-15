commit c364fc5b72f06481bd232779cc213869995899bb
Author: Jovanni Tilborg <jovannitilborg@example.com>
Date:   Thu May 15 10:37:50 2025 +0700

    Fix analyze_from_signal_callback: gebruik SIGNAL_ANALYSIS_KEYBOARD en CHOOSE_ANALYSIS

diff --git a/trading_bot/main.py b/trading_bot/main.py
index 5a38153..dd6730b 100644
--- a/trading_bot/main.py
+++ b/trading_bot/main.py
@@ -2763,7 +2763,6 @@ Start your subscription today!
     async def analyze_from_signal_callback(self, update: Update, context=None) -> int:
         """Handle Analyze Market button from signal notifications"""
         query = update.callback_query
-        # Add query.answer() to acknowledge the callback
         await query.answer()
         logger.info(f"analyze_from_signal_callback called with data: {query.data}")
         
@@ -2781,20 +2780,11 @@ Start your subscription today!
                 
                 # Store in context for other handlers
                 if context and hasattr(context, 'user_data'):
-                    # Reset signal flow flags
-                    context.user_data['from_signal'] = False
-                    context.user_data['in_signal_flow'] = False
-                    logger.info(f"Reset signal flow flags: from_signal=False, in_signal_flow=False")
                     context.user_data['instrument'] = instrument
                     if signal_id:
                         context.user_data['signal_id'] = signal_id
-                    # Set signal flow flags (only once)
-                    context.user_data['from_signal'] = True
-                    context.user_data['in_signal_flow'] = True
-                    logger.info(f"Set signal flow flags: from_signal=True, in_signal_flow=True")
                     
                     # Make a backup copy to ensure we can return to signal later
-                    context.user_data['signal_instrument'] = instrument
                     context.user_data['signal_instrument_backup'] = instrument
                     if signal_id:
                         context.user_data['signal_id_backup'] = signal_id
@@ -2808,63 +2798,56 @@ Start your subscription today!
                             timeframe = signal.get('interval') or signal.get('timeframe')
                             context.user_data['signal_timeframe'] = timeframe
                             # Backup copies
-                            context.user_data['signal_timeframe_backup'] = timeframe
                             context.user_data['signal_direction_backup'] = signal.get('direction')
+                            context.user_data['signal_timeframe_backup'] = timeframe
+                            logger.info(f"Stored signal details: direction={signal.get('direction')}, timeframe={timeframe}")
+            else:
+                # Legacy support - just extract the instrument
+                instrument = parts[3] if len(parts) >= 4 else None
                 
-                # Store the original signal page for later retrieval
-                logger.info(f"Storing original signal page for: {instrument}, {signal_id}")
-                try:
-                    await self._store_original_signal_page(update, context, instrument, signal_id)
-                    logger.info(f"Successfully stored original signal page")
-                except Exception as store_err:
-                    logger.error(f"Error storing original signal page: {str(store_err)}")
-                
-                # Show analysis options for this instrument
-                keyboard = [
-                    [
-                        InlineKeyboardButton("📊 Technical", callback_data=f"analysis_technical_signal_{instrument}"),
-                        InlineKeyboardButton("🔍 Sentiment", callback_data=f"analysis_sentiment_signal_{instrument}")
-                    ],
-                    [
-                        InlineKeyboardButton("📅 Calendar", callback_data=f"analysis_calendar_signal_{instrument}"),
-                        InlineKeyboardButton("⬅️ Back to Signal", callback_data="back_to_signal")
-                    ]
-                ]
-                
-                # Add the back to menu button
-                keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_menu")])
-                
-                reply_markup = InlineKeyboardMarkup(keyboard)
-                
-                # Ask the user what type of analysis they want
+                if instrument and context and hasattr(context, 'user_data'):
+                    context.user_data['instrument'] = instrument
+                    context.user_data['signal_instrument_backup'] = instrument
+            
+            # Store the original signal page for later retrieval
+            logger.info(f"Storing original signal page for: {instrument}, {signal_id}")
+            try:
+                await self._store_original_signal_page(update, context, instrument, signal_id)
+                logger.info(f"Successfully stored original signal page")
+            except Exception as store_err:
+                logger.error(f"Error storing original signal page: {str(store_err)}")
+            
+            # Show analysis options for this instrument
+            # Use the SIGNAL_ANALYSIS_KEYBOARD for consistency
+            keyboard = SIGNAL_ANALYSIS_KEYBOARD
+            
+            # Try to edit the message text
+            try:
                 await query.edit_message_text(
-                    text=f"<b>Choose Analysis for {instrument}</b>\n\nSelect the type of market analysis you'd like to see:",
-                    reply_markup=reply_markup,
+                    text=f"Select your analysis type:",
+                    reply_markup=InlineKeyboardMarkup(keyboard),
                     parse_mode=ParseMode.HTML
                 )
-                
-                logger.info(f"Displayed analysis options for {instrument}")
-                return ANALYSIS_OPTIONS
-            else:
-                logger.warning(f"Invalid callback data format: {query.data}")
-                # Fallback to instrument selection menu
-                await query.edit_message_text(
-                    text="Sorry, there was an error processing that signal. Please select an instrument for analysis:",
-                    reply_markup=InlineKeyboardMarkup(MARKET_KEYBOARD),
+            except Exception as e:
+                logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
+                # Fall back to sending a new message
+                await query.message.reply_text(
+                    text=f"Select your analysis type:",
+                    reply_markup=InlineKeyboardMarkup(keyboard),
                     parse_mode=ParseMode.HTML
                 )
-                return MARKET_SELECTION
-                
+            
+            return CHOOSE_ANALYSIS
+            
         except Exception as e:
             logger.error(f"Error in analyze_from_signal_callback: {str(e)}")
-            logger.exception(e)  # This logs the full traceback
+            logger.exception(e)
             
             # Error recovery - show user a message and return to main menu
             try:
                 await query.edit_message_text(
-                    text="Sorry, there was an error while processing that signal. Please try again from the main menu.",
-                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD),
-                    parse_mode=ParseMode.HTML
+                    text="An error occurred. Please try again from the main menu.",
+                    reply_markup=InlineKeyboardMarkup(START_KEYBOARD)
                 )
             except Exception:
                 pass
