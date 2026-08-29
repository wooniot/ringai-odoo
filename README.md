# RingAI Voice Connector (Odoo 19)

Brengt de RingAI AI-telefoniste in Odoo: gesprekken, AI-samenvattingen, transcript
en automatische terugbel-taken per klant. Multi-company (één RingAI-tenant per bedrijf).

## Modules
- `ringai_connector` — Odoo 19 module.

## Datastroom
De data-toegang zit geïsoleerd in `models/ringai_client.py` (`_fetch_calls`). In de
test-/self-hosted opstelling leest die **read-only** rechtstreeks uit de RingAI-
database (`call_logs`) op dezelfde host. Voor App Store-distributie wordt alleen die
ene methode vervangen door een HTTP-call naar een RingAI read-API (zelfde returnvorm).

## Installeren
Kopieer `ringai_connector/` in je addons-path, update de appslijst, installeer.

## Configureren
1. **Instellingen -> RingAI**: host/poort/db/gebruiker/wachtwoord van de RingAI-bron,
   dan **Test verbinding**.
2. **Instellingen -> Bedrijven**: per bedrijf de **RingAI tenant id** (uuid) invullen.
3. **Sync nu** (of wacht op de 15-minuten cron). Gesprekken verschijnen onder **RingAI ->
   Gesprekken**; opvolg-gesprekken worden een activiteit op het contact.

## Prijs
Module gratis (LGPL-3). Waarde via het RingAI-abonnement (ringai.nl).
