# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ringai_api_key = fields.Char(
        string="RingAI connector-key",
        help="De per-tenant connector-key uit RingAI (ringai.nl). Bepaalt van welke "
             "RingAI-tenant de gesprekken bij dit bedrijf horen.",
    )
    ringai_tenant_id = fields.Char(
        string="RingAI tenant id",
        help="Ter referentie — de RingAI-tenant (uuid) achter de connector-key.",
    )
