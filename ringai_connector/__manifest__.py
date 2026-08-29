# -*- coding: utf-8 -*-
{
    "name": "RingAI Voice Connector",
    "version": "19.0.1.0.0",
    "category": "Sales/CRM",
    "summary": "Breng je RingAI AI-telefoniste in Odoo — gesprekken, AI-samenvattingen en automatische terugbel-taken per klant.",
    "description": """
RingAI Voice Connector
======================
Koppelt je RingAI (AI-telefoniste, Voys/SIP) aan Odoo. Inkomende en uitgaande
gesprekken verschijnen als records op de klant (res.partner), met de door AI
gegenereerde **samenvatting**, het volledige **transcript**, de duur en de
gespreksrichting. Gemiste of op te volgen gesprekken worden automatisch een
**terugbel-activiteit** op de juiste contactpersoon.

* **Gesprekslog in Odoo** — beller, samenvatting, transcript, duur, richting, status.
* **Automatische terugbel-taken** — needs_followup -> mail.activity op de partner.
* **Per bedrijf** — elk Odoo-bedrijf koppelt aan zijn eigen RingAI-tenant.
* **AI-terugkoppeling** — de samenvatting en score van RingAI, direct in je CRM.

RingAI levert de spraak + intelligentie; Odoo is je klant- en opvolgsysteem.
""",
    "author": "Woon IoT BV (RingAI)",
    "website": "https://ringai.nl",
    "license": "LGPL-3",
    "depends": ["base", "mail", "contacts"],
    "external_dependencies": {"python": ["psycopg2"]},
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/ringai_call_views.xml",
        "views/res_company_views.xml",
        "views/res_config_settings_views.xml",
        "views/ringai_menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
}
