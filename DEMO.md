# SigmaPips Signal Storage - Demonstratie

## Probleem
Wanneer een gebruiker op de "analyze market" knop klikt na ontvangst van een signaal, en vervolgens op "back" klikt, gaat de huidige status van het signaal verloren.

## Oplossing
Sla signalen permanent op wanneer ze binnenkomen, zodat de "back" knop altijd terugkeert naar het oorspronkelijke signaal.

## Implementatie

### 1. SignalStorageService (trading_bot/services/signal_storage_service.py)
Deze service slaat signalen op in een JSON-bestand en laadt ze wanneer nodig:

```python
# Kern functionaliteit
async def store_signal(self, user_id: str, signal_id: str, signal_data: Dict) -> None:
    # Signaal opslaan in self.signals_by_user dictionary
    # en wegschrijven naar bestand
    
async def get_signal(self, user_id: str, signal_id: str) -> Optional[Dict]:
    # Signaal ophalen uit opgeslagen data
```

### 2. Patch voor ProcessSignal (signal_forward.py)
Dit script verrijkt de bestaande bot met persistente signaalopslag zonder main.py aan te passen:

```python
# Signaal onderscheppen en opslaan wanneer het binnenkomt
@wraps(original_process_signal)
async def patched_process_signal(self, signal_data):
    # Verwerk signaal met originele methode
    result = await original_process_signal(self, signal_data)
    
    # Sla signaal op in storage service
    await store_signal(signal_data)
    
    return result
```

### 3. Back-knop functionaliteit
De bestaande `_store_original_signal_page` methode wordt gebruikt om het originele signaal op te slaan wanneer "analyze market" wordt aangeklikt:

```python
async def _store_original_signal_page(self, update, context, instrument, signal_id):
    # Haal signaaldata op en bereid voor
    signal_page_data = {
        'instrument': instrument,
        'signal_id': signal_id,
        'message': original_signal.get('message') or update.callback_query.message.text
    }
    
    # Sla op in database
    await self.db.save_signal_page(update.effective_user.id, instrument, signal_page_data)
```

Wanneer de gebruiker op "back" klikt, wordt het originele signaal opgehaald uit de persistente opslag.

## Gebruik

1. Start de bot normaal
2. Wanneer een signaal binnenkomt, wordt het automatisch opgeslagen
3. Gebruik de "analyze market" knop zoals gewoonlijk
4. Druk op "back" om terug te keren naar het originele signaal

## Voordelen

1. **Persistentie** - Signalen blijven behouden, zelfs na herstart van de bot
2. **Geen wijzigingen aan main.py** - Werkt met de bestaande codebase
3. **Eenvoudig** - Minimale implementatie die precies doet wat nodig is

## Test

```bash
# Start de bot met signaalopslag
python run_local_bot.py
```

Controleer dat je kunt navigeren tussen:
- Ontvangen signaal → "analyze market" → analyses → "back" → Origineel signaal 