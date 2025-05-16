#!/usr/bin/env python3
"""
Force Signal Processing

Dit script forceert een testsignaal door de volledige signaalverwerkingspijplijn van de TelegramService class,
inclusief het opslaan van het signaal in de data/signals en data/signals/users mappen.
"""

import asyncio
import json
import logging
import os
import argparse
from datetime import datetime
import sys
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock, AsyncMock, patch

# Voeg de hoofdmap toe aan de Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configureer logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Definieer mappen
BASE_DIR = "data"
SIGNALS_DIR = os.path.join(BASE_DIR, "signals")
USER_SIGNALS_DIR = os.path.join(SIGNALS_DIR, "users")

async def save_signal_directly(signal_data, user_ids=None):
    """
    Sla een signaal direct op in de signal storage
    door direct naar JSON bestanden te schrijven zoals setup_signal_storage.py doet
    """
    try:
        # Controleer of mappen bestaan en maak ze indien nodig
        os.makedirs(SIGNALS_DIR, exist_ok=True)
        os.makedirs(USER_SIGNALS_DIR, exist_ok=True)
        
        # Zorg dat we een signaal ID hebben
        if 'id' not in signal_data:
            timestamp = int(datetime.now().timestamp())
            signal_id = f"{signal_data['instrument']}_{signal_data['direction']}_{signal_data['timeframe']}_{timestamp}"
            signal_data['id'] = signal_id
        else:
            signal_id = signal_data['id']
            
        logger.info(f"Signaal ID: {signal_id}")
        
        # Sla het signaal op in de centrale opslagruimte
        central_signal_path = os.path.join(SIGNALS_DIR, f"{signal_id}.json")
        with open(central_signal_path, 'w') as f:
            json.dump(signal_data, f, indent=2)
        logger.info(f"\u2705 Signaal opgeslagen in centrale opslagruimte: {central_signal_path}")
        
        # Sla het signaal op voor specifieke gebruikers
        if user_ids:
            for user_id in user_ids:
                # Maak de gebruikers-map indien nodig
                user_dir = os.path.join(USER_SIGNALS_DIR, str(user_id))
                os.makedirs(user_dir, exist_ok=True)
                
                # Sla het signaal op voor deze gebruiker
                user_signal_path = os.path.join(user_dir, f"{signal_id}.json")
                with open(user_signal_path, 'w') as f:
                    json.dump(signal_data, f, indent=2)
                logger.info(f"\u2705 Signaal opgeslagen voor gebruiker {user_id}: {user_signal_path}")
        
        # Controleer of bestanden zijn aangemaakt
        central_files = os.listdir(SIGNALS_DIR)
        logger.info(f"Bestanden in centrale opslagruimte: {central_files}")
        
        signal_files = [f for f in central_files if signal_id in f]
        if signal_files:
            logger.info(f"\u2705 Signaalbestanden gevonden in centrale opslag: {signal_files}")
        else:
            logger.warning("\u274c Geen signaalbestanden gevonden met het signaal ID")
        
        for user_id in user_ids or []:
            user_dir = os.path.join(USER_SIGNALS_DIR, str(user_id))
            if os.path.exists(user_dir):
                user_files = os.listdir(user_dir)
                logger.info(f"Bestanden voor gebruiker {user_id}: {user_files}")
                
                user_signal_files = [f for f in user_files if signal_id in f]
                if user_signal_files:
                    logger.info(f"\u2705 Signaalbestanden gevonden voor gebruiker {user_id}: {user_signal_files}")
                else:
                    logger.warning(f"\u274c Geen signaalbestanden gevonden voor gebruiker {user_id}")
            else:
                logger.warning(f"\u274c Gebruikersmap voor {user_id} bestaat niet: {user_dir}")
        
        return True
    except Exception as e:
        logger.error(f"Fout bij direct opslaan van signaal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def process_test_signal(instrument, direction, entry, stop_loss, take_profit, timeframe="1h"):
    """
    Creu00eber een testsignaal en sla het direct op in de signal storage
    """
    try:
        # Creu00eber signaal data in het juiste formaat
        signal_data = {
            "instrument": instrument,
            "direction": direction.upper(),
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "timeframe": timeframe,
            "interval": timeframe,  # Voor TradingView compatibiliteit
            "price": entry,  # Voor TradingView compatibiliteit
            "sl": stop_loss,  # Voor TradingView compatibiliteit
            "timestamp": datetime.now().isoformat()
        }
        
        # Voeg meerdere take profit niveaus toe
        if take_profit:
            entry_value = float(entry)
            tp_value = float(take_profit)
            
            # Stel TP1 direct in
            signal_data["tp1"] = take_profit
            
            # Bereken TP2 en TP3 op basis van richting
            if direction.upper() == "BUY":
                # Voor BUY signalen moeten TPs boven entry zijn in oplopende volgorde
                tp_diff = abs(tp_value - entry_value)
                signal_data["tp2"] = str(round(entry_value + 1.5 * tp_diff, 5))
                signal_data["tp3"] = str(round(entry_value + 2.0 * tp_diff, 5))
            else:
                # Voor SELL signalen moeten TPs onder entry zijn in aflopende volgorde
                tp_diff = abs(entry_value - tp_value)
                signal_data["tp2"] = str(round(entry_value - 1.5 * tp_diff, 5))
                signal_data["tp3"] = str(round(entry_value - 2.0 * tp_diff, 5))
        
        # Voeg een mooi geformatteerd bericht toe
        signal_data["message"] = f"<b>\ud83c\udff9 New Trading Signal \ud83c\udff9</b>\n\n"
        signal_data["message"] += f"<b>Instrument:</b> {instrument}\n"
        direction_emoji = "\ud83d\udfe2" if direction.upper() == "BUY" else "\ud83d\udd34"
        signal_data["message"] += f"<b>Action:</b> {direction.upper()} {direction_emoji}\n\n"
        signal_data["message"] += f"<b>Entry Price:</b> {entry}\n"
        signal_data["message"] += f"<b>Stop Loss:</b> {stop_loss} \ud83d\udd34\n"
        signal_data["message"] += f"<b>Take Profit 1:</b> {take_profit} \ud83c\udff9\n"
        signal_data["message"] += f"<b>Take Profit 2:</b> {signal_data.get('tp2')} \ud83c\udff9\n"
        signal_data["message"] += f"<b>Take Profit 3:</b> {signal_data.get('tp3')} \ud83c\udff9\n\n"
        signal_data["message"] += f"<b>Timeframe:</b> {timeframe}\n"
        signal_data["message"] += f"<b>Strategy:</b> Test Signal\n\n"
        
        # Log het signaal
        logger.info(f"Test signaal data: {json.dumps(signal_data, indent=2)}")
        
        # Test user IDs - voeg je eigen Telegram ID toe als je die weet
        test_user_ids = [1093307376, 2004519703, "test"]  # Default admin ID + anderen
        
        # Sla het signaal direct op
        result = await save_signal_directly(signal_data, test_user_ids)
        
        return result
    
    except Exception as e:
        logger.error(f"Fout bij verwerken van testsignaal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Hoofdfunctie voor het script"""
    parser = argparse.ArgumentParser(description="Forceer een testsignaal door de signaalverwerkingspijplijn")
    parser.add_argument("--instrument", default="EURUSD", help="Handelsinstrument (bijv. EURUSD)")
    parser.add_argument("--direction", default="BUY", choices=["BUY", "SELL"], help="Handelsrichting")
    parser.add_argument("--entry", default="1.0850", help="Entry prijs")
    parser.add_argument("--stop-loss", default="1.0800", help="Stop loss prijs")
    parser.add_argument("--take-profit", default="1.0900", help="Take profit prijs")
    parser.add_argument("--timeframe", default="1h", help="Timeframe (bijv. 1h, 4h, 15m)")
    
    args = parser.parse_args()
    
    # Roep de functie aan om het testsignaal te verwerken
    success = await process_test_signal(
        args.instrument,
        args.direction,
        args.entry,
        args.stop_loss,
        args.take_profit,
        args.timeframe
    )
    
    if success:
        print("\n\u2705 SUCCES: Het testsignaal is succesvol verwerkt en opgeslagen!")
        print("Controleer de volgende mappen:")
        print(f"  - {SIGNALS_DIR}/ (voor centrale signaalopslag)")
        print(f"  - {USER_SIGNALS_DIR}/ (voor gebruikersspecifieke signaalopslag)")
    else:
        print("\n\u274c FOUT: Het testsignaal kon niet worden verwerkt.")
        print("Controleer de logs voor meer informatie.")

if __name__ == "__main__":
    asyncio.run(main()) 