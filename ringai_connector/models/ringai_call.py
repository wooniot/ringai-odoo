# -*- coding: utf-8 -*-
import logging
from odoo import _, api, fields, models
_logger = logging.getLogger(__name__)
class RingaiCall(models.Model):
    _name = "ringai.call"
    _description = "RingAI gesprek"
    _order = "started_at desc"
    _rec_name = "display_title"
    ringai_id = fields.Char(string="RingAI id", index=True, required=True)
    company_id = fields.Many2one(
        "res.company", string="Bedrijf", required=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one("res.partner", string="Contact")
    caller_number = fields.Char(string="Nummer")
    caller_name = fields.Char(string="Beller")
    to_number = fields.Char(string="Naar nummer")
    direction = fields.Selection(
        [("inbound", "Inkomend"), ("outbound", "Uitgaand")],
        string="Richting", default="inbound",
    )
    started_at = fields.Datetime(string="Gestart")
    ended_at = fields.Datetime(string="Beëindigd")
    duration_seconds = fields.Integer(string="Duur (s)")
    summary = fields.Text(string="AI-samenvatting")
    transcript = fields.Text(string="Transcript")
    needs_followup = fields.Boolean(string="Opvolgen")
    followed_up = fields.Boolean(string="Opgevolgd")
    user_note = fields.Text(string="Notitie")
    display_title = fields.Char(string="Titel", compute="_compute_title", store=True)
    _sql_constraints = [
        ("ringai_id_uniq", "unique(ringai_id)", "Dit RingAI-gesprek bestaat al."),
    ]
    @api.depends("caller_name", "caller_number", "started_at")
    def _compute_title(self):
        for c in self:
            who = c.caller_name or c.caller_number or _("Onbekend")
            c.display_title = "%s — %s" % (who, c.started_at or "")
    @api.model
    def _match_partner(self, company, number, name):
        if not number:
            return False
        Partner = self.env["res.partner"]
        digits = "".join(ch for ch in number if ch.isdigit())[-9:]
        partner = False
        if digits:
            partner = Partner.search([
                ("phone", "ilike", digits),
                "|", ("company_id", "=", company.id), ("company_id", "=", False),
            ], limit=1)
        if not partner and name:
            partner = Partner.create({
                "name": name, "phone": number,
                "company_id": company.id, "is_company": False,
            })
        return partner and partner.id
    @api.model
    def _sync_company(self, company):
        key = (company.ringai_api_key or "").strip()
        if not key:
            return 0
        rows = self.env["ringai.client"]._fetch_calls(key)
        made = 0
        for r in rows:
            existing = self.search([("ringai_id", "=", r["ringai_id"])], limit=1)
            vals = {
                "company_id": company.id,
                "caller_number": r["caller_number"],
                "caller_name": r["caller_name"],
                "to_number": r["to_number"],
                "direction": r["direction"],
                "started_at": r["started_at"] or False,
                "ended_at": r["ended_at"] or False,
                "duration_seconds": r["duration_seconds"],
                "summary": r["summary"],
                "transcript": r["transcript"],
                "needs_followup": r["needs_followup"],
                "followed_up": r["followed_up"],
                "user_note": r["user_note"],
            }
            if existing:
                if not existing.partner_id:
                    vals["partner_id"] = self._match_partner(
                        company, r["caller_number"], r["caller_name"])
                existing.with_context(ringai_no_push=True).write(vals)
                rec = existing
            else:
                vals["ringai_id"] = r["ringai_id"]
                vals["partner_id"] = self._match_partner(
                    company, r["caller_number"], r["caller_name"])
                rec = self.create(vals)
                made += 1
            rec._ensure_followup_activity()
        return made
    def _ensure_followup_activity(self):
        """Ensure followup activity."""
        self.ensure_one()
        if not (self.needs_followup and not self.followed_up and self.partner_id):
            return
        Act = self.env["mail.activity"]
        model_id = self.env["ir.model"]._get_id("res.partner")
        act_type = self.env.ref("mail.mail_activity_data_call", raise_if_not_found=False)
        exists = Act.search([
            ("res_model_id", "=", model_id),
            ("res_id", "=", self.partner_id.id),
            ("summary", "=", "RingAI: terugbellen"),
        ], limit=1)
        if exists:
            return
        Act.create({
            "res_model_id": model_id,
            "res_id": self.partner_id.id,
            "activity_type_id": act_type.id if act_type else False,
            "summary": "RingAI: terugbellen",
            "note": (self.summary or "")[:2000],
            "date_deadline": fields.Date.context_today(self),
        })
    @api.model
    def action_sync_all(self):
        total = 0
        for company in self.env["res.company"].search([("ringai_api_key", "!=", False)]):
            total += self._sync_company(company)
        _logger.info("RingAI sync: %s nieuwe gesprekken", total)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("RingAI sync"),
                "message": _("%s nieuwe gesprekken opgehaald.") % total,
                "type": "success", "sticky": False,
            },
        }
    def action_mark_followed_up(self):
        self.write({"followed_up": True})

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("ringai_no_push") and (
                "followed_up" in vals or "user_note" in vals):
            Client = self.env["ringai.client"]
            for rec in self:
                key = rec.company_id.ringai_api_key
                if not key or not rec.ringai_id:
                    continue
                if "followed_up" in vals:
                    Client._push_followup(key, rec.ringai_id, rec.followed_up)
                if "user_note" in vals:
                    Client._push_note(key, rec.ringai_id, rec.user_note or "")
        return res
