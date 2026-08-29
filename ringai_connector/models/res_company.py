# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ringai_tenant_id = fields.Char(
        string="RingAI tenant id",
        help="De RingAI-tenant (uuid) waarvan de gesprekken bij dit bedrijf horen.",
    )
