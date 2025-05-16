# SigmaPips Signaalopslag - Gebruiksaanwijzing

## Probleem

Wanneer je op de "analyze market" knop klikt na het ontvangen van een signaal, en vervolgens op de "back" knop drukt, gaat het huidige signaal verloren. Dit betekent dat je niet meer terug kunt naar het originele signaal.

## Oplossing

De signaalopslag functionaliteit slaat automatisch alle binnenkomende signalen op, zodat de "back" knop altijd werkt, zelfs na het herstarten van de bot.

## Hoe te gebruiken

### Optie 1: Start de bot met signaalopslag

```bash
python run_with_signal_storage.py
```

Dit script start de bot met de signaalopslag functionaliteit geactiveerd. Het wijzigt niets aan de main.py file, maar voegt de functionaliteit toe via "monkey patching".

### Optie 2: Activeer signaalopslag in een bestaande bot

Als je de bot al op een andere manier start, kun je de signaalopslag activeren door het volgende script uit te voeren voordat je de bot start:

```bash
python quick_start.py
```

### Optie 3: Bekijk opgeslagen signalen

Om te zien welke signalen zijn opgeslagen, kun je het volgende script uitvoeren:

```bash
python view_signals.py
```

Dit toont een interactief menu waarmee je:
1. Een overzicht van alle opgeslagen signalen kunt bekijken
2. Details van signalen per gebruiker kunt inzien
3. Specifieke signalen kunt opzoeken op ID

## Hoe het werkt

1. **Signaal ontvangen**: Wanneer een signaal binnenkomt, wordt het automatisch opgeslagen
2. **Analyze Market**: Als je op de "analyze market" knop drukt, wordt het originele signaal bewaard
3. **Back knop**: Als je op "back" drukt, wordt het originele signaal opgehaald uit de persistente opslag

## Voordelen

1. **Geen wijzigingen aan main.py**: De oplossing werkt zonder de kern van de bot aan te passen
2. **Persistentie**: Signalen blijven bewaard, zelfs na herstart van de bot
3. **Eenvoudig**: Minimale implementatie die precies doet wat nodig is

## Bestanden

- **signal_storage_simplified.py**: De kern van de signaalopslag functionaliteit
- **run_with_signal_storage.py**: Script om de bot te starten met signaalopslag
- **quick_start.py**: Script om signaalopslag te activeren in een bestaande bot
- **view_signals.py**: Script om opgeslagen signalen te bekijken
- **DEMO.md**: Demonstratie van de functionaliteit
- **GEBRUIKSAANWIJZING.md**: Deze gebruiksaanwijzing

## Opgeslagen signalen

Signalen worden opgeslagen in het bestand `signals_data.json` in de `storage` directory van de bot. Deze directory wordt automatisch aangemaakt als deze nog niet bestaat.

## Problemen oplossen

Als de "back" knop nog steeds niet werkt na het activeren van de signaalopslag, controleer dan:

1. Of de `storage` directory is aangemaakt met daarin het bestand `signals_data.json`
2. Of er geen foutmeldingen zijn in de console
3. Of het signaal correct is opgeslagen (je kunt het bestand `storage/signals_data.json` bekijken of `python view_signals.py` uitvoeren)

Als er problemen zijn, start dan de bot opnieuw met:

```bash
python run_with_signal_storage.py
```

## Vragen?

Als je vragen hebt over de signaalopslag functionaliteit, neem dan contact op met de ontwikkelaar. 