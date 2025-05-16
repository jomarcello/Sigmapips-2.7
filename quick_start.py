#!/usr/bin/env python3
"""
Quick Start voor SigmaPips Signal Storage

Dit script start de signaalopslag functionaliteit en patcht de bot
zodat signalen automatisch worden opgeslagen zonder main.py aan te passen.

Gebruik:
    python quick_start.py
"""

import os
import sys
import logging
from signal_storage_simplified import patch_bot_for_signal_storage, get_signal_storage

# Configureer logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start de signaalopslag functionaliteit."""
    logger.info("SigmaPips Signal Storage Quick Start")
    
    # Controleer of het signals_data.json bestand bestaat
    storage = get_signal_storage()
    storage_file = storage.storage_file
    
    if os.path.exists(storage_file):
        logger.info(f"Bestaande signaalopslag gevonden: {storage_file}")
        logger.info(f"Aantal gebruikers met opgeslagen signalen: {len(storage.signals)}")
        
        # Tel het totaal aantal signalen
        total_signals = sum(len(signals) for signals in storage.signals.values())
        logger.info(f"Totaal aantal opgeslagen signalen: {total_signals}")
    else:
        logger.info(f"Geen bestaande signaalopslag gevonden. Een nieuwe zal worden aangemaakt.")
    
    # Patch de bot
    logger.info("De bot patchen voor persistente signaalopslag...")
    success = patch_bot_for_signal_storage()
    
    if success:
        logger.info("✅ Bot succesvol gepatched!")
        logger.info("Signalen worden nu automatisch opgeslagen.")
        logger.info("De 'back' knop zal nu altijd werken, zelfs na herstart van de bot.")
    else:
        logger.error("❌ Fout bij het patchen van de bot.")
        logger.error("Controleer of de bot correct is geïnstalleerd.")
        return 1
    
    # Instructies tonen
    print("\n" + "-" * 60)
    print("SigmaPips Signal Storage is actief!")
    print("-" * 60)
    print("Signalen worden automatisch opgeslagen wanneer ze binnenkomen.")
    print("De 'back' knop zal nu altijd werken, zelfs na herstart van de bot.")
    print("\nOpgeslagen signalen worden bewaard in:", storage_file)
    print("-" * 60 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 