# -*- coding: utf-8 -*-
{
    "name": "RingAI Voice Connector",
    "version": "19.0.3.0.0",
    "category": "Sales/CRM",
    "summary": "Show your RingAI AI phone assistant calls in Odoo: AI summaries and automatic call-back tasks per customer.",
    "description": """
RingAI Voice Connector
======================
Connects your RingAI voice service (AI phone assistant) to Odoo. Inbound and
outbound calls appear as records linked to the customer (res.partner), with the
AI-generated summary, the full transcript, duration and direction. Calls that
need follow-up automatically become a call-back activity on the right contact.

* Call log in Odoo: caller, summary, transcript, duration, direction, status.
* Automatic call-back activities on the partner for calls that need follow-up.
* Multi-company: each Odoo company connects to its own RingAI tenant.
* AI feedback from RingAI, directly in your CRM.

External service and data: this module requires an active RingAI account. It sends
only a per-company connector key over HTTPS to authenticate, and reads back that
tenant's calls (caller number/name, summary, transcript, duration). No database
access is required and you keep ownership of your data at all times.
""",
    "author": "Woon IoT BV (RingAI)",
    "website": "https://ringai.nl/odoo",
    "license": "LGPL-3",
    "depends": ["base", "mail", "contacts"],
    "external_dependencies": {"python": ["requests"]},
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
