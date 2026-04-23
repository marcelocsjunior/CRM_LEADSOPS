from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable, Mapping

FINAL_PIPELINE_STATUSES = {"Ganhou", "Perdido", "Não contatar"}
AGING_THRESHOLDS = {
    "Novo": (3, 7),
    "Contatado": (3, 7),
    "Respondeu": (2, 5),
    "Reunião": (1, 3),
    "Proposta": (3, 7),
}


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text[:19].replace("T", " ")).date()
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None


def stage_entry_date(lead: Mapping[str, Any], audit_events: Iterable[Mapping[str, Any]] | None = None) -> date | None:
    current_status = str(lead.get("status") or "Novo")
    events = list(audit_events or [])
    for event in events:
        if str(event.get("field") or "") != "status":
            continue
        if str(event.get("new_value") or "") != current_status:
            continue
        ts = _parse_date(event.get("ts"))
        if ts:
            return ts

    if current_status == "Novo":
        return _parse_date(lead.get("created_at")) or _parse_date(lead.get("updated_at"))

    return _parse_date(lead.get("updated_at")) or _parse_date(lead.get("created_at"))


def aging_days(lead: Mapping[str, Any], audit_events: Iterable[Mapping[str, Any]] | None = None, today: date | None = None) -> int:
    status = str(lead.get("status") or "Novo")
    if status in FINAL_PIPELINE_STATUSES:
        return 0
    today = today or date.today()
    entered = stage_entry_date(lead, audit_events=audit_events)
    if not entered:
        return 0
    return max(0, (today - entered).days)


def aging_bucket(status: str | None, days: int) -> str:
    normalized = str(status or "Novo")
    warm_after, stale_after = AGING_THRESHOLDS.get(normalized, (3, 7))
    if days >= stale_after:
        return "critical"
    if days >= warm_after:
        return "warning"
    return "ok"


def aging_label(status: str | None, days: int) -> str:
    bucket = aging_bucket(status, days)
    if bucket == "critical":
        return "Envelhecido"
    if bucket == "warning":
        return "Atenção"
    return "Dentro da cadência"


def annotate_lead_aging(lead: Mapping[str, Any], audit_events: Iterable[Mapping[str, Any]] | None = None, today: date | None = None) -> dict[str, Any]:
    days = aging_days(lead, audit_events=audit_events, today=today)
    status = str(lead.get("status") or "Novo")
    entered = stage_entry_date(lead, audit_events=audit_events)
    return {
        "aging_days": days,
        "aging_bucket": aging_bucket(status, days),
        "aging_label": aging_label(status, days),
        "stage_entry_date": entered.isoformat() if entered else "",
    }
