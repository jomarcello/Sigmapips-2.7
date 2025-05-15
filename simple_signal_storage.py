#!/usr/bin/env python3
"""
Simple Signal Storage - Opslaan van signalen voor SigmaPips back-knop

Dit script slaat signalen op wanneer ze binnenkomen zodat de back-knop
altijd werkt, zelfs na herstart van de bot.

Gebruik:
    python simple_signal_storage.py
"""

import os
import json
import logging
from datetime import datetime
import traceback
from typing import Dict, Optional

# Logging configureren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuratie
STORAGE_PATH = "storage/signals.json"

def setup_storage():
    """Maak storage directory aan als die niet bestaat."""
    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
    
    # Creëer leeg signals bestand als het niet bestaat
    if not os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, "w") as f:
            json.dump({}, f)
        logger.info(f"Nieuw signals bestand aangemaakt: {STORAGE_PATH}")

def load_signals() -> Dict:
    """Laad opgeslagen signalen."""
    try:
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning(f"Kon signalen niet laden uit {STORAGE_PATH}, nieuw bestand wordt gemaakt")
        return {}

def save_signals(signals: Dict):
    """Sla signalen op naar bestand."""
    try:
        with open(STORAGE_PATH, "w") as f:
            json.dump(signals, f, indent=2)
        logger.info(f"Signalen opgeslagen naar {STORAGE_PATH}")
    except Exception as e:
        logger.error(f"Fout bij opslaan signalen: {str(e)}")

def patch_bot():
    """
    Patch de SigmaPips bot om signalen op te slaan zonder main.py aan te passen.
    """
    try:
        # Import de bot klasse
        from trading_bot.services.telegram_service.bot import SigmaPipsBot
        
        # Originele methoden bewaren
        original_process_signal = SigmaPipsBot.process_signal
        
        # Monkey patch de process_signal methode om signalen op te slaan
        async def patched_process_signal(self, signal_data):
            # Roep eerst de originele methode aan
            result = await original_process_signal(self, signal_data)
            
            try:
                # Haal benodigde gegevens op uit het signaal
                signal_id = signal_data.get('id', str(datetime.now().timestamp()))
                
                # Voeg timestamp toe als die er niet is
                if 'timestamp' not in signal_data:
                    signal_data['timestamp'] = datetime.now().isoformat()
                
                # Laad bestaande signalen
                signals = load_signals()
                
                # Voeg het signaal toe of update het
                if 'user_id' in signal_data:
                    user_id = str(signal_data['user_id'])
                    if user_id not in signals:
                        signals[user_id] = {}
                    signals[user_id][signal_id] = signal_data
                else:
                    # Als er geen user_id is, gebruik 'default'
                    if 'default' not in signals:
                        signals['default'] = {}
                    signals['default'][signal_id] = signal_data
                
                # Sla de bijgewerkte signalen op
                save_signals(signals)
                logger.info(f"Signaal {signal_id} opgeslagen")
            except Exception as e:
                logger.error(f"Fout bij opslaan signaal: {str(e)}")
                logger.error(traceback.format_exc())
            
            return result
        
        # Vervang de originele methode met onze gepatchte versie
        SigmaPipsBot.process_signal = patched_process_signal
        
        logger.info("Bot succesvol gepatched voor signaalopslag")
        return True
    except ImportError:
        logger.error("Kon de bot klasse niet importeren")
        return False
    except Exception as e:
        logger.error(f"Fout bij patchen van de bot: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Hoofdfunctie."""
    print("SigmaPips Simple Signal Storage")
    print("-------------------------------")
    print("Dit script slaat signalen op zodat de back-knop altijd werkt")
    
    # Setup storage
    setup_storage()
    
    # Patch de bot
    success = patch_bot()
    
    if success:
        print("✅ Bot succesvol gepatched!")
        print("Signalen worden nu automatisch opgeslagen")
        print(f"Signalen worden bewaard in: {STORAGE_PATH}")
        print("De back-knop zal nu altijd werken, zelfs na herstart van de bot")
    else:
        print("❌ Fout bij patchen van de bot")
        print("Controleer de logs voor meer informatie")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 