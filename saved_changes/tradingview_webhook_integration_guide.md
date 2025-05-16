# TradingView naar Telegram Integratie Gids

Deze gids legt uit hoe je de correcte integratie opzet tussen TradingView, je Railway webhook, en de Telegram bot met ondersteuning voor dynamische gebruikerstoewijzing.

## Systeemoverzicht

Het systeem werkt als volgt:
1. TradingView stuurt trading signalen naar je Railway webhook endpoint
2. Je Railway applicatie verwerkt deze signalen
3. De applicatie bepaalt dynamisch welke gebruikers het signaal moeten ontvangen (op basis van abonnementen, voorkeuren, etc.)
4. De Telegram bot verstuurt de berichten naar de juiste gebruikers

## Vereiste Configuraties

### 1. Railway Environment Variables

| Variabele | Waarde | Beschrijving |
|-----------|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | `jouw_bot_token` | Token van je Telegram bot |
| `WEBHOOK_URL` | `https://railwaywebhook-production-8102.up.railway.app` | Je Railway webhook URL (zonder /webhook aan het einde) |
| `WEBHOOK_MODE` | `true` | Zet de bot in webhook modus |
| `INTERNAL_API_URL` | `https://railwaywebhook-production-8102.up.railway.app` | Interne URL voor API communicatie |

### 2. Telegram Webhook Configuratie

De Telegram webhook moet geconfigureerd worden zodat Telegram weet waar het berichten voor je bot naartoe moet sturen:

```bash
python configure_telegram_webhook.py --bot-token JOUW_BOT_TOKEN --webhook-url https://railwaywebhook-production-8102.up.railway.app/webhook
```

### 3. TradingView Alert Configuratie

In TradingView, configureer je alerts om naar je webhook URL te sturen:

1. Ga naar de TradingView chart en maak een nieuwe alert
2. Bij "Alert actions" kies "Webhook URL"
3. Voer de volgende URL in: `https://railwaywebhook-production-8102.up.railway.app/webhook`
4. Configureer het JSON bericht in dit formaat:

```json
{
  "instrument": "{{ticker}}",
  "direction": "{{strategy.order.action}}",
  "entry": "{{strategy.order.price}}",
  "stop_loss": "{{strategy.order.stop_price}}",
  "take_profit": ["{{strategy.order.tp1}}", "{{strategy.order.tp2}}", "{{strategy.order.tp3}}"],
  "timeframe": "{{interval}}",
  "strategy": "TradingView Strategy",
  "timestamp": "{{time}}"
}
```

Pas de velden aan volgens je eigen strategie en vereisten.

## Dataflow en Verwerking

1. **TradingView → Railway Webhook**:
   - TradingView stuurt een JSON payload naar de webhook endpoint
   - De webhook endpoint accepteert en valideert de data

2. **Webhook Handler → Signaalverwerking**:
   - De webhook handler verwerkt het inkomende signaal
   - Het signaal wordt in de juiste format omgezet

3. **Dynamische Gebruikersroutering**:
   - Het systeem bepaalt welke gebruikers het signaal moeten ontvangen
   - Dit gebeurt op basis van abonnementen, filters, en gebruikersvoorkeuren
   - Er wordt geen hardcoded chat ID gebruikt

4. **Telegram Berichten**:
   - De Telegram bot stuurt de geformatteerde signalen naar de juiste gebruikers

## Testen van de Integratie

### Test 1: Handmatig Webhook Test

Test of je webhook endpoint signalen correct ontvangt:

```bash
python send_new_signal.py
```

### Test 2: TradingView Test

1. Maak een test alert in TradingView
2. Activeer de alert handmatig
3. Controleer of het signaal correct wordt verwerkt

### Test 3: Dynamische Routing Test

Test of de signalen naar de juiste gebruikers worden gerouteerd:

```bash
python test_dynamic_routing.py
```

## Troubleshooting

Als signalen niet correct worden verwerkt:

1. **Check webhook configuratie**:
   ```bash
   python configure_telegram_webhook.py --bot-token JOUW_BOT_TOKEN --check
   ```

2. **Controleer Railway logs**:
   Bekijk de logs in je Railway dashboard voor verwerkingsfouten

3. **Controleer het formaat van TradingView alerts**:
   Zorg ervoor dat het JSON formaat correct is en alle vereiste velden bevat

4. **Test de bot verbinding**:
   ```bash
   python test_direct_telegram.py
   ```

5. **Verifieer de database connectie**:
   Zorg ervoor dat de app verbinding kan maken met de database om gebruikersinformatie op te halen

## Code Aanpassingen (indien nodig)

Als je problemen hebt met de dynamische routing, controleer:

1. `trading_bot/webhook_handeler.py` - Verwerkt inkomende webhook verzoeken
2. `trading_bot/main.py` - Bevat de TelegramService die signalen verwerkt
3. `trading_bot/unified_app.py` - Integreert de API en Telegram bot

Zorg ervoor dat de Railway deployment de nieuwste codeversie gebruikt en dat alle environment variables correct zijn ingesteld. 