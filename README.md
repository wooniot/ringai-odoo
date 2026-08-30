# RingAI Voice Connector (Odoo 19)

Brengt de RingAI AI-telefoniste in Odoo: gesprekken, AI-samenvattingen, transcript
en automatische terugbel-taken per klant. Multi-company (één RingAI-tenant per bedrijf).

## Module
- `ringai_connector` — Odoo 19 module.

## Datastroom
De connector praat met de beveiligde **RingAI read-API** (`/api/connector`, per-tenant
`X-Connector-Key`). Geen databasetoegang bij de klant, geen cross-tenant toegang. De
datalaag zit geïsoleerd in `models/ringai_client.py`.

## Installeren
Kopieer `ringai_connector/` in je addons-path, update de appslijst, installeer.

## Configureren
1. **Instellingen -> RingAI**: base URL (doorgaans `https://ringai.nl`), dan **Test verbinding**.
2. **Instellingen -> Bedrijven**: per bedrijf de **RingAI connector-key** invullen.
3. **Sync nu** (of wacht op de 15-minuten cron). Gesprekken verschijnen onder
   **RingAI -> Gesprekken**; opvolg-gesprekken worden een activiteit op het contact.

## Prijs
Module gratis (LGPL-3). Waarde via het RingAI-abonnement (ringai.nl).
