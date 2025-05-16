# Railway Webhook Configuratie Gids

Deze gids legt uit hoe je de webhook correct configureert voor je SigmaPips bot, zodat signalen correct worden verwerkt.

## Benodigde Environment Variables

Voor een correcte werking van de webhook en Telegram-integratie moeten de volgende omgevingsvariabelen worden ingesteld in je Railway-project:

| Variabele | Waarde | Beschrijving |
|-----------|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | `jouw_bot_token` | Token van je Telegram bot, verkrijgbaar via @BotFather |
| `TELEGRAM_CHAT_ID` | `jouw_chat_id` | Chat ID waar signalen naartoe moeten worden gestuurd |
| `WEBHOOK_URL` | `https://railwaywebhook-production-8102.up.railway.app` | Je Railway webhook URL (zonder /webhook aan het einde) |
| `WEBHOOK_MODE` | `true` | Zet de bot in webhook modus in plaats van polling |
| `INTERNAL_API_URL` | `https://railwaywebhook-production-8102.up.railway.app` | Interne URL voor API communicatie (meestal hetzelfde als WEBHOOK_URL) |

## Stappen voor Configuratie

1. **Telegram Bot Token instellen**
   
   Zorg ervoor dat je een geldige `TELEGRAM_BOT_TOKEN` hebt ingesteld. Dit is de token die je krijgt van @BotFather wanneer je een bot aanmaakt.

2. **Telegram Chat ID instellen**
   
   De `TELEGRAM_CHAT_ID` is de ID van de chat (groep of privé) waar je wilt dat de signalen worden afgeleverd.

3. **Webhook URL instellen**
   
   Zet `WEBHOOK_URL` op de URL van je Railway app, bijvoorbeeld:
   ```
   https://railwaywebhook-production-8102.up.railway.app
   ```
   Let op: voeg NIET `/webhook` toe aan het einde - de applicatie voegt dit automatisch toe.

4. **Webhook Mode activeren**
   
   Zet `WEBHOOK_MODE` op `true` om de bot in webhook-modus te laten draaien.

5. **API URL instellen**
   
   Zet `INTERNAL_API_URL` op dezelfde waarde als je `WEBHOOK_URL`.

## De Telegram Webhook Configureren

Nadat je de omgevingsvariabelen hebt ingesteld, moet je de Telegram webhook configureren zodat Telegram weet waarheen berichten moeten worden gestuurd.

1. Voer het meegeleverde `configure_telegram_webhook.py` script uit:

```bash
python configure_telegram_webhook.py --webhook-url https://railwaywebhook-production-8102.up.railway.app/webhook
```

of als je de token niet als environment variable hebt ingesteld:

```bash
python configure_telegram_webhook.py --bot-token YOUR_BOT_TOKEN --webhook-url https://railwaywebhook-production-8102.up.railway.app/webhook
```

2. **Controleer de webhook configuratie**:

```bash
python configure_telegram_webhook.py --check
```

## Testen van de Webhook

Nadat alles is geconfigureerd, kun je de webhook testen door een signaal te sturen:

```bash
python send_new_signal.py
```

Als alles correct is ingesteld, zou dit een signaal moeten verzenden naar je Telegram bot.

## Troubleshooting

Als je nog steeds geen signalen ontvangt:

1. Controleer of de webhook correct is ingesteld:
   ```bash
   python configure_telegram_webhook.py --check
   ```

2. Controleer of je Railway app draait en bereikbaar is.

3. Bekijk de logs in je Railway dashboard voor eventuele foutmeldingen.

4. Controleer of de bot token en chat ID correct zijn door een direct bericht te sturen:
   ```bash
   python test_direct_telegram.py
   ``` 