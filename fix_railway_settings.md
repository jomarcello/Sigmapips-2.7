# Fix Railway Settings

Om de bot weer stabiel te krijgen, moet je de volgende variabelen in je Railway project verwijderen of op de juiste waarde zetten:

1. Log in bij je [Railway dashboard](https://railway.app/)
2. Ga naar je SigmaPips project
3. Open het tabblad "Variables"
4. Zoek naar en verwijder de volgende variabelen (als ze bestaan):
   - `WEBHOOK_MODE`
   - `WEBHOOK_URL`
   - `WEBHOOK_PORT`

Als de variabelen niet aanwezig zijn, is dat geen probleem.

## Verzeker je ervan dat de bot in polling mode draait

Om er zeker van te zijn dat de bot in polling mode draait en niet probeert een webhook te gebruiken, kun je het volgende doen:

```bash
# Verwijder de webhook configuratie (je hebt dit al gedaan)
curl -X POST "https://api.telegram.org/bot[YOUR_BOT_TOKEN]/deleteWebhook?drop_pending_updates=true"

# Controleer de webhook status
curl -X POST "https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getWebhookInfo"
```

Het resultaat zou moeten aangeven dat er geen webhook is ingesteld.

## Railway deployment opnieuw starten

Nadat je de variabelen hebt verwijderd:

1. Ga naar de "Deployments" tab in je Railway project
2. Klik op de "Deploy" knop om een nieuwe deployment te starten met de schone instellingen

Dit zou de bot moeten herstarten zonder de webhook configuratie problemen. 