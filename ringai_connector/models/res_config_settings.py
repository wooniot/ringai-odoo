# -*- coding: utf-8 -*-
from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ringai_db_host = fields.Char(
        string="RingAI host", config_parameter="ringai_connector.db_host",
        default="host.docker.internal")
    ringai_db_port = fields.Char(
        string="RingAI poort", config_parameter="ringai_connector.db_port",
        default="5433")
    ringai_db_name = fields.Char(
        string="RingAI database", config_parameter="ringai_connector.db_dbname",
        default="aireceptionist")
    ringai_db_user = fields.Char(
        string="RingAI gebruiker", config_parameter="ringai_connector.db_user",
        default="aireceptionist")
    ringai_db_password = fields.Char(
        string="RingAI wachtwoord", config_parameter="ringai_connector.db_password")

    def action_ringai_test_connection(self):
        self.ensure_one()
        self.set_values()
        ok, msg = self.env["ringai.client"]._test_connection()
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
