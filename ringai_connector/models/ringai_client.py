# -*- coding: utf-8 -*-
"""RingAI data-access layer — GEISOLEERD.

De rest van de module praat alleen met `env['ringai.client']._fetch_calls(...)`.
Nu leest die read-only rechtstreeks uit de RingAI-database (call_logs) op dezelfde
host. Voor App Store-distributie wordt enkel deze methode vervangen door een
HTTP-call naar een RingAI read-API (zelfde returnvorm) — de rest blijft gelijk.
"""
import json
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# defaults passen bij de RingAI-testhost (ringai-db op 127.0.0.1:5433, via docker
# host.docker.internal). Overschrijfbaar via Instellingen -> RingAI.
DEFAULTS = {
    "host": "host.docker.internal",
    "port": "5433",
    "dbname": "aireceptionist",
    "user": "aireceptionist",
    "password": "aireceptionist",
}


class RingaiClient(models.AbstractModel):
    _name = "ringai.client"
    _description = "RingAI data-access (read-only)"

    @api.model
    def _conn_params(self):
        icp = self.env["ir.config_parameter"].sudo()
        return {
            k: icp.get_param("ringai_connector.db_%s" % k, DEFAULTS[k])
            for k in DEFAULTS
        }

    @api.model
    def _fetch_calls(self, tenant_id, limit=200):
        """Lijst call_logs voor een RingAI tenant (uuid, als string).

        Returnt een lijst dicts met genormaliseerde sleutels. Leeg bij lege
        tenant of fout (fout wordt gelogd, niet doorgegooid) zodat een sync
        van andere bedrijven doorloopt.
        """
        if not tenant_id:
            return []
        try:
            import psycopg2
            import psycopg2.extras
        except Exception:
            _logger.error("psycopg2 niet beschikbaar op de Odoo-server")
            return []
        p = self._conn_params()
        sql = """
            SELECT id::text AS ringai_id, tenant_id::text AS tenant_id,
                   caller_number, caller_name, to_number, direction,
                   started_at, ended_at, duration_seconds, summary,
                   transcript, needs_followup, followed_up, user_note
            FROM call_logs
            WHERE tenant_id = %s
            ORDER BY started_at DESC NULLS LAST
            LIMIT %s
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=p["host"], port=p["port"], dbname=p["dbname"],
                user=p["user"], password=p["password"], connect_timeout=8,
            )
            conn.set_session(readonly=True, autocommit=True)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, (tenant_id, limit))
            rows = cur.fetchall()
        except Exception as exc:
            # nooit secrets loggen — alleen het type
            _logger.warning("RingAI fetch faalde: %s", type(exc).__name__)
            return []
        finally:
            if conn is not None:
                conn.close()

        def _naive(dt):
            # Odoo Datetime-velden willen naïeve UTC; strip tzinfo
            if dt is None:
                return False
            if getattr(dt, "tzinfo", None) is not None:
                from datetime import timezone
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt

        out = []
        for r in rows:
            tr = r.get("transcript")
            if isinstance(tr, (dict, list)):
                tr = json.dumps(tr, ensure_ascii=False, indent=2)
            out.append({
                "ringai_id": r["ringai_id"],
                "tenant_id": r["tenant_id"],
                "caller_number": r.get("caller_number") or "",
                "caller_name": r.get("caller_name") or "",
                "to_number": r.get("to_number") or "",
                "direction": (r.get("direction") or "inbound"),
                "started_at": _naive(r.get("started_at")),
                "ended_at": _naive(r.get("ended_at")),
                "duration_seconds": r.get("duration_seconds") or 0,
                "summary": r.get("summary") or "",
                "transcript": tr or "",
                "needs_followup": bool(r.get("needs_followup")),
                "followed_up": bool(r.get("followed_up")),
                "user_note": r.get("user_note") or "",
            })
        return out

    @api.model
    def _test_connection(self):
        """Simpele ping: tel tenants. Geeft (ok, msg)."""
        try:
            import psycopg2
        except Exception:
            return False, "psycopg2 ontbreekt op de server"
        p = self._conn_params()
        try:
            conn = psycopg2.connect(
                host=p["host"], port=p["port"], dbname=p["dbname"],
                user=p["user"], password=p["password"], connect_timeout=8,
            )
            conn.set_session(readonly=True, autocommit=True)
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM tenants")
            n = cur.fetchone()[0]
            conn.close()
            return True, "Verbonden met RingAI · %s tenants zichtbaar" % n
        except Exception as exc:
            return False, "Verbinding mislukt: %s" % type(exc).__name__
