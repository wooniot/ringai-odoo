# -*- coding: utf-8 -*-
from odoo import fields, models
class ResCompany(models.Model):
    _inherit = "res.company"
    ringai_api_key = fields.Char(string="RingAI connector-key")
    ringai_tenant_id = fields.Char(string="RingAI tenant id")
