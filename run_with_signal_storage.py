#!/usr/bin/env python3
"""
Run SigmaPips Bot met Signal Storage

Dit script start de SigmaPips bot met de signaalopslag functionaliteit geactiveerd.
Het past de bot aan zonder main.py te wijzigen, zodat signalen worden opgeslagen
en de 'back' knop altijd werkt.

Gebruik:
    python run_with_signal_storage.py
"""

import os
import sys
import logging
import importlib
import traceback
from signal_storage_simplified import patch_bot_for_signal_storage, get_signal_storage

# Configureer logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start de bot met signaalopslag."""
    logger.info("SigmaPips Bot starten met signaalopslag...")
    
    # Initialiseer de signaalopslag
    storage = get_signal_storage()
    logger.info(f"Signaalopslag geïnitialiseerd: {storage.storage_file}")
    
    # Patch de bot voor signaalopslag
    logger.info("Bot patchen voor persistente signaalopslag...")
    success = patch_bot_for_signal_storage()
    
    if not success:
        logger.error("❌ Fout bij het patchen van de bot.")
        return 1
    
    logger.info("✅ Bot succesvol gepatched voor signaalopslag!")
    
    # Start de bot
    logger.info("De originele bot starten...")
    try:
        # Importeer de main module dynamisch
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Probeer eerst run_local_bot.py
        try:
            run_bot_module = importlib.import_module("run_local_bot")
            logger.info("run_local_bot.py gevonden, deze wordt gebruikt.")
        except ImportError:
            # Als dat niet lukt, probeer main.py
            try:
                run_bot_module = importlib.import_module("trading_bot.main")
                logger.info("trading_bot.main gevonden, deze wordt gebruikt.")
            except ImportError:
                logger.error("Kon geen bot startup script vinden (run_local_bot.py of trading_bot.main).")
                return 1
        
        # Start de bot met de main functie
        if hasattr(run_bot_module, "main"):
            logger.info("Bot wordt gestart...")
            print("\n" + "-" * 60)
            print("SigmaPips Bot met Signal Storage")
            print("-" * 60)
            print("Signalen worden automatisch opgeslagen wanneer ze binnenkomen.")
            print("De 'back' knop zal nu altijd werken, zelfs na herstart van de bot.")
            print("\nOpgeslagen signalen worden bewaard in:", storage.storage_file)
            print("-" * 60 + "\n")
            
            # Start de main functie
            run_bot_module.main()
        else:
            logger.error("Kon geen main functie vinden in de bot module.")
            return 1
            
    except Exception as e:
        logger.error(f"Fout bij het starten van de bot: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 