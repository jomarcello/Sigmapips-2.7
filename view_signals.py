#!/usr/bin/env python3
"""
Bekijk opgeslagen signalen voor SigmaPips

Dit script toont een overzicht van alle opgeslagen signalen in de signaalopslag.
"""

import os
import sys
import json
import logging
from signal_storage_simplified import get_signal_storage, view_stored_signals

# Configureer logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Toon opgeslagen signalen."""
    print("\n" + "=" * 60)
    print("SIGMAPIPS SIGNAALOPSLAG VIEWER")
    print("=" * 60)
    
    # Haal de signaalopslag op
    storage = get_signal_storage()
    storage_file = storage.storage_file
    
    if not os.path.exists(storage_file):
        print(f"\nGeen signaalopslag gevonden in {storage_file}")
        print("Er zijn nog geen signalen opgeslagen.")
        return 1
    
    # Toon informatie over het opslag bestand
    file_size = os.path.getsize(storage_file) / 1024  # KB
    print(f"\nSignaalopslag bestand: {storage_file}")
    print(f"Bestandsgrootte: {file_size:.2f} KB")
    
    # Toon samenvatting
    view_stored_signals()
    
    # Vraag of gebruiker details wil zien
    user_ids = storage.list_users()
    if user_ids:
        while True:
            print("\nKies een optie:")
            print("1. Toon details van een specifieke gebruiker")
            print("2. Toon details van een specifiek signaal")
            print("3. Afsluiten")
            
            choice = input("\nKeuze (1-3): ")
            
            if choice == "1":
                print("\nBeschikbare gebruikers:")
                for i, user_id in enumerate(user_ids, 1):
                    signal_count = len(storage.list_signals_for_user(user_id))
                    print(f"{i}. Gebruiker {user_id} ({signal_count} signalen)")
                
                user_choice = input("\nKies een gebruiker (nummer): ")
                try:
                    user_index = int(user_choice) - 1
                    if 0 <= user_index < len(user_ids):
                        selected_user = user_ids[user_index]
                        _show_user_signals(storage, selected_user)
                    else:
                        print("Ongeldige keuze.")
                except ValueError:
                    print("Voer een geldig nummer in.")
            
            elif choice == "2":
                user_id = input("\nVoer gebruiker ID in: ")
                signal_id = input("Voer signaal ID in: ")
                
                signal = storage.get_signal(user_id, signal_id)
                if signal:
                    _show_signal_details(signal)
                else:
                    print(f"Geen signaal gevonden met ID {signal_id} voor gebruiker {user_id}")
            
            elif choice == "3":
                break
            
            else:
                print("Ongeldige keuze. Kies 1, 2 of 3.")
    
    return 0

def _show_user_signals(storage, user_id):
    """Toon alle signalen voor een gebruiker."""
    signals = storage.signals.get(user_id, {})
    
    print("\n" + "-" * 60)
    print(f"SIGNALEN VOOR GEBRUIKER {user_id}")
    print("-" * 60)
    
    if not signals:
        print("Geen signalen gevonden voor deze gebruiker.")
        return
    
    for signal_id, signal_data in signals.items():
        instrument = signal_data.get('instrument', 'Onbekend')
        timestamp = signal_data.get('timestamp', 'Onbekend')
        direction = signal_data.get('direction', 'Onbekend')
        price = signal_data.get('price', 'Onbekend')
        
        print(f"Signaal ID: {signal_id}")
        print(f"Instrument: {instrument}")
        print(f"Richting: {direction}")
        print(f"Prijs: {price}")
        print(f"Tijdstip: {timestamp}")
        print("-" * 40)

def _show_signal_details(signal):
    """Toon details van een signaal."""
    print("\n" + "-" * 60)
    print("SIGNAAL DETAILS")
    print("-" * 60)
    
    # Toon de belangrijkste velden eerst
    important_fields = ['id', 'instrument', 'direction', 'price', 'timestamp', 'message']
    for field in important_fields:
        if field in signal:
            print(f"{field.capitalize()}: {signal[field]}")
    
    # Toon overige velden
    print("\nOverige velden:")
    for key, value in signal.items():
        if key not in important_fields:
            print(f"{key}: {value}")

if __name__ == "__main__":
    sys.exit(main()) 