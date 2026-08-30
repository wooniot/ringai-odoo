# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timezone
from odoo import api, models
_logger = logging.getLogger(__name__)
DEFAULT_BASE_URL = "https://ringai.nl"
class RingaiClient(models.AbstractModel):
    _name = "ringai.client"
    _description = "RingAI API-client (read-only)"
    @api.model
    def _base_url(self):
        base = self.env["ir.config_parameter"].sudo().get_param(
            "ringai_connector.base_url") or DEFAULT_BASE_URL
        return base.rstrip("/")
    @api.model
    def _get(self, path, api_key):
        if not api_key:
            return None
        try:
            import requests
        except Exception:
            _logger.error("python 'requests' ontbreekt op de Odoo-server")
            return None
        url = self._base_url() + path
        try:
            resp = requests.get(url, headers={"X-Connector-Key": api_key}, timeout=15)
        except Exception as exc:
            _logger.warning("RingAI-API onbereikbaar: %s", type(exc).__name__)
            return None
        if resp.status_code == 401:
            _logger.warning("RingAI-API 401 (ongeldige connector-key)")
            return None
        if resp.status_code != 200:
            _logger.warning("RingAI-API status %s", resp.status_code)
            return None
        try:
            return resp.json()
        except Exception:
            return None
    @api.model
    def _parse_dt(self, s):
        if not s:
            return False
        try:
            dt = datetime.fromisoformat(s)
        except Exception:
            return False
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    @api.model
    def _fetch_calls(self, api_key, limit=200):
        data = self._get("/api/connector/calls?limit=%d" % int(limit), api_key)
        if not data:
            return []
        out = []
        for r in data.get("calls", []):
            out.append({
                "ringai_id": r.get("id"),
                "caller_number": r.get("caller_number") or "",
                "caller_name": r.get("caller_name") or "",
                "to_number": r.get("to_number") or "",
                "direction": r.get("direction") or "inbound",
                "started_at": self._parse_dt(r.get("started_at")),
                "ended_at": self._parse_dt(r.get("ended_at")),
                "duration_seconds": r.get("duration_seconds") or 0,
                "summary": r.get("summary") or "",
                "transcript": r.get("transcript") or "",
                "needs_followup": bool(r.get("needs_followup")),
                "followed_up": bool(r.get("followed_up")),
                "user_note": r.get("user_note") or "",
            })
        return out
    @api.model
    def _test_connection(self, api_key):
        data = self._get("/api/connector/me", api_key)
        if data and data.get("tenant"):
            return True, "Verbonden met RingAI · tenant: %s" % data["tenant"]
        return False, "Verbinding mislukt — controleer de base URL en de connector-key."
