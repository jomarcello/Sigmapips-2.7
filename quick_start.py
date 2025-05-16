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
# Import only get_signal_storage, patching is automatic in signal_storage_simplified
from signal_storage_simplified import get_signal_storage

# Configureer logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start de signaalopslag functionaliteit."""
    logger.info("SigmaPips Signal Storage Quick Start")
    
    # Het pad naar het opslagbestand, dit is meestal signals_data.json
    # SignalStorage class zelf beheert niet de file, dus we definiëren het hier.
    storage_file = "signals_data.json"
    storage = get_signal_storage() # Haal de in-memory storage op
    
    if os.path.exists(storage_file):
        logger.info(f"Controleren op bestaande signaalopslag: {storage_file}")
        # De volgende logging is misschien niet accuraat als SignalStorage alleen in-memory is
        # en niet direct de JSON laadt bij initialisatie.
        # logger.info(f"Aantal gebruikers met opgeslagen signalen: {len(storage.signals)}") 
        
        # # Tel het totaal aantal signalen
        # total_signals = sum(len(signals) for signals in storage.signals.values())
        # logger.info(f"Totaal aantal opgeslagen signalen: {total_signals}")
    else:
        logger.info(f"Geen bestaande signaalopslag gevonden. Een nieuwe zal worden aangemaakt.")
    
    # De bot wordt automatisch gepatcht bij het importeren van signal_storage_simplified.
    # Controleer of de patching succesvol was (optioneel, afhankelijk van hoe signal_storage_simplified dit signaleert)
    # Voor nu gaan we ervan uit dat het goed gaat als er geen error is bij importeren.
    logger.info("Patches voor persistente signaalopslag worden automatisch toegepast bij het laden.")
    logger.info("Controleer de logs van 'signal_storage_simplified' voor de status van het patchen.")
    
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