# SigmaPips Signal Storage Systeem

Dit systeem slaat trading signalen op die binnenkomen in de SigmaPips trading bot, zonder wijzigingen aan te brengen aan de main.py file.

## Overzicht

Het Signal Storage systeem bestaat uit de volgende componenten:

1. **SignalStorageService** - De kernservice die signalen persistent opslaat
2. **SignalInterceptor** - Onderschept signalen en levert ze aan de storage service
3. **signal_saver.py** - Standalone webhook server die signalen ontvangt en opslaat
4. **signal_forward.py** - Script dat signalen uit de bot onderschept en doorstuurt
5. **Web UI** - Eenvoudige interface om opgeslagen signalen te bekijken

## Installatievereisten

```
pip install aiofiles aiohttp
```

## Gebruik

### 1. Start de Signal Saver service (Methode 1 - aanbevolen)

```bash
python signal_saver.py
```

Opties:
- `--port 8005` - Poort waarop de webhook server draait
- `--path /webhook` - Pad voor webhook endpoint
- `--storage ./storage` - Map waar signalen worden opgeslagen
- `--log-level INFO` - Logniveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### 2. Integreer met de bot (kies een methode)

**Methode A: Use signal_forward.py (patch-methode, geen wijzigingen aan main.py)**

```bash
python signal_forward.py
```

Dit script patcht de SignalPipsBot klasse on-the-fly om signalen te onderscheppen zonder wijzigingen aan het originele bestand.

**Methode B: Stuur direct webhooks**

Stuur signalen rechtstreeks naar de webhook:

```bash
curl -X POST http://localhost:8005/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123456", "instrument": "EURUSD", "direction": "buy", "price": "1.2345", "timeframe": "1h"}'
```

### 3. Bekijk opgeslagen signalen

1. Open in een browser: `http://localhost:8005/ui/`
2. Voer de user ID in en optioneel een instrument om te filteren
3. Bekijk de opgeslagen signalen

## API Endpoints

- `POST /webhook` - Ontvang en sla signaal op
- `GET /api/signals?user_id=123&instrument=EURUSD` - Haal signalen op
- `GET /api/signal/SIGNAL_ID?user_id=123` - Haal specifiek signaal op

## Hoe het werkt

1. **Signaal opslag** - Wanneer signalen binnenkomen, worden ze persistent opgeslagen in JSON formaat.
2. **Geen wijzigingen aan main.py** - De oplossing werkt parallel met de hoofdapplicatie.
3. **Herstellen na herstart** - Signalen blijven bewaard, zelfs na herstart van de bot.

### Signaal stroom

```
Bot ontvangst -> Signal Forward -> Webhook -> Signal Storage -> JSON Bestand
                          |
                          V
                    Web UI Toegang
```

## Map structuur

```
.
├── storage/                   # Map voor opgeslagen signalen
│   └── signals.json           # Opgeslagen signalen in JSON formaat
├── ui/                        # Web interface
│   └── index.html             # Dashboard voor signalen
├── trading_bot/               
│   └── services/              
│       ├── signal_storage_service.py  # Kern opslagservice
│       └── signal_interceptor.py      # Signal interceptor 
├── signal_saver.py            # Webhook server
└── signal_forward.py          # Bot integratie script
```

## Voordelen

1. **Geen wijzigingen aan main.py** - Werkt naast de bestaande codebase
2. **Persistente opslag** - Signalen gaan niet verloren bij herstart
3. **Gemakkelijke toegang** - UI en API voor toegang tot signalen
4. **Filtering** - Zoek signalen per gebruiker en instrument
5. **Historie** - Bewaar signaalgeschiedenis voor latere analyse

## Probleemoplossing

**Signal Saver start niet:**
- Controleer of de poort niet al in gebruik is
- Controleer of je de vereiste packages hebt geïnstalleerd

**Signalen worden niet opgeslagen:**
- Zorg dat de storage map schrijfbaar is
- Controleer signal_forward logs voor connectieproblemen

**Web UI toont geen signalen:**
- Zorg dat het juiste user_id wordt gebruikt
- Controleer browser console voor JavaScript errors

## Configuratie via Environment Variables

```bash
export WEBHOOK_PORT=8005
export WEBHOOK_PATH=/webhook
export STORAGE_DIR=./storage
export LOG_LEVEL=INFO
export SIGNAL_SAVER_URL=http://localhost:8005/webhook
```

## Voorbeeld

Stel je wilt alle signalen voor gebruiker 123456 en instrument EURUSD bekijken:

1. Start Signal Saver: `python signal_saver.py`
2. Start Signal Forward: `python signal_forward.py` 
3. Open browser: `http://localhost:8005/ui/`
4. Voer gebruikers-ID in: `123456`
5. Voer instrument in: `EURUSD`
6. Klik op Filter 