# Railway Setup voor TradingView naar Telegram Integratie

Deze gids helpt je bij het instellen van je Railway deployment voor optimale werking met TradingView integratie en dynamische gebruikersroutering.

## Railway Environment Variables

Voeg deze environment variables toe aan je Railway project:

| Variabele | Waarde | Beschrijving |
|-----------|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | `7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk` | De bot token voor de Telegram bot |
| `WEBHOOK_URL` | `https://railwaywebhook-production-8102.up.railway.app` | De base URL van je webhook (zonder /webhook) |
| `WEBHOOK_MODE` | `true` | Zet de Telegram bot in webhook modus |
| `INTERNAL_API_URL` | `https://railwaywebhook-production-8102.up.railway.app` | URL voor interne API communicatie |
| `DATABASE_URL` | `jouw_database_url` | Connection string voor je database (voor gebruikersdata) |

## Telegram Webhook Configuratie

De volgende stappen zijn reeds uitgevoerd, maar het is goed om te weten wat er is gebeurd:

1. We hebben de Telegram webhook ingesteld met:
   ```
   python configure_telegram_webhook.py --bot-token 7328581013:AAGDFJyvipmQsV5UQLjUeLQmX2CWIU2VMjk --webhook-url https://railwaywebhook-production-8102.up.railway.app/webhook
   ```

2. We hebben geverifieerd dat de webhook correct is ingesteld:
   ```
   python test_dynamic_routing.py
   ```

## TradingView Integratie

Volg deze stappen om TradingView te integreren:

1. In TradingView, maak een nieuwe alert aan
2. Stel de alert condities in volgens je strategie
3. Bij "Alert actions":
   - Selecteer "Webhook URL"
   - Vul in: `https://railwaywebhook-production-8102.up.railway.app/webhook`
   - Gebruik een JSON template uit `tradingview_webhook_alert_template.txt`

## Debugging en Monitoring

Als signalen niet correct worden gedistribueerd:

1. **Controleer Railway logs**:
   - Ga naar je Railway dashboard
   - Bekijk de logs voor eventuele fouten
   - Let op berichten over de webhook ontvangst en signaalverwerking

2. **Controleer database connectie**:
   - Zorg ervoor dat je database beschikbaar is
   - Verifieer dat gebruikersgegevens correct zijn opgeslagen

3. **Test de bot dynamische routing**:
   - Voer periodiek tests uit met `test_dynamic_routing.py`
   - Controleer of signalen door de logica gaan voor gebruikersfiltering

## Systeemarchitectuur

De huidige architectuur werkt als volgt:

1. **TradingView** stuurt signalen naar `https://railwaywebhook-production-8102.up.railway.app/webhook`
2. De **webhook handler** in `trading_bot/webhook_handeler.py` ontvangt deze signalen
3. De signalen worden verwerkt door de logic in `trading_bot/main.py` (TelegramService)
4. De service bepaalt op basis van je database welke gebruikers het signaal moeten ontvangen
5. Het systeem stuurt de verwerkte signalen naar de juiste Telegram-gebruikers

## Toekomstige Verbeteringen

Mogelijke verbeteringen voor de toekomst:

1. **Betere Foutafhandeling**: Verbeterde logging en error handling
2. **Webhook Security**: Implementeer authenticatie voor de webhook
3. **Prestatieoptimalisatie**: Optimaliseer voor snellere signaalverwerking
4. **Gebruikersfilters**: Uitbreiden van dynamische routeringslogica voor gedetailleerdere filters 