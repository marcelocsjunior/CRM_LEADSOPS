from __future__ import annotations

from typing import Any, Mapping

from leadops.db import FINAL_STATUSES
from leadops.messages import followup_urgency

BUCKET_ORDER = [
    "critical_overdue",
    "today",
    "new_uncontacted",
    "waiting_response",
    "ready_to_advance",
    "upcoming",
    "other_active",
]

BUCKET_LABELS = {
    "critical_overdue": "Follow-up crítico",
    "today": "Hoje",
    "new_uncontacted": "Novos sem contato",
    "waiting_response": "Aguardando retorno",
    "ready_to_advance": "Responderam / avançar",
    "upcoming": "Agendados",
    "other_active": "Outros ativos",
}


def interaction_count(lead: Mapping[str, Any], counts: Mapping[int, int]) -> int:
    return int(counts.get(int(lead.get("id") or 0), 0))


def is_new_uncontacted(lead: Mapping[str, Any], counts: Mapping[int, int]) -> bool:
    if str(lead.get("status") or "") != "Novo":
        return False
    if str(lead.get("ultimo_contato") or "").strip():
        return False
    return interaction_count(lead, counts) == 0


def is_contacted_waiting_response(lead: Mapping[str, Any], counts: Mapping[int, int]) -> bool:
    return str(lead.get("status") or "") == "Contatado" and interaction_count(lead, counts) > 0


def operational_bucket_key(lead: Mapping[str, Any], counts: Mapping[int, int]) -> str:
    status = str(lead.get("status") or "")
    if status in FINAL_STATUSES:
        return "other_active"

    urgency = followup_urgency(lead)
    if urgency["bucket"] == "critical_overdue":
        return "critical_overdue"
    if urgency["bucket"] in {"today", "overdue"}:
        return "today"
    if is_new_uncontacted(lead, counts):
        return "new_uncontacted"
    if is_contacted_waiting_response(lead, counts):
        return "waiting_response"
    if status in {"Respondeu", "Reunião", "Proposta"}:
        return "ready_to_advance"
    if urgency["bucket"] == "upcoming":
        return "upcoming"
    return "other_active"


def operational_bucket_label(bucket_key: str) -> str:
    return BUCKET_LABELS.get(bucket_key, bucket_key)


def build_operational_buckets(rows: list[Mapping[str, Any]], counts: Mapping[int, int]) -> dict[str, list[Mapping[str, Any]]]:
    buckets = {key: [] for key in BUCKET_ORDER}
    for lead in rows:
        status = str(lead.get("status") or "")
        if status in FINAL_STATUSES:
            continue
        key = operational_bucket_key(lead, counts)
        buckets.setdefault(key, []).append(lead)
    return buckets
