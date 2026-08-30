# -*- coding: utf-8 -*-
from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ringai_base_url = fields.Char(
        string="RingAI base URL",
        config_parameter="ringai_connector.base_url",
        default="https://ringai.nl")

    def action_ringai_test_connection(self):
        self.ensure_one()
        self.set_values()
        key = self.env.company.ringai_api_key
        ok, msg = self.env["ringai.client"]._test_connection(key)
        if not key:
            ok, msg = False, _("Geen connector-key voor bedrijf %s "
                               "(Instellingen -> Bedrijven).") % self.env.company.name
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("RingAI"),
                "message": msg,
                "type": "success" if ok else "danger",
                "sticky": False,
            },
        }

    def action_ringai_sync_now(self):
        self.ensure_one()
        return self.env["ringai.call"].action_sync_all()
