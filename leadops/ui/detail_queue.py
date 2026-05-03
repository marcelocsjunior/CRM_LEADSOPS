from __future__ import annotations

from typing import Any, Mapping

from leadops.aging import annotate_lead_aging
from leadops.db import FINAL_STATUSES
from leadops.queue import (
    BUCKET_ORDER,
    build_operational_buckets,
    operational_bucket_key,
    operational_bucket_label,
)


def searchable_text(lead: Mapping[str, Any]) -> str:
    return " ".join(
        str(lead.get(field) or "")
        for field in (
            "empresa",
            "cidade",
            "segmento",
            "email_publico",
            "telefone",
            "whatsapp_numero",
        )
    ).casefold()


def filter_active_rows(
    rows: list[Mapping[str, Any]],
    counts: Mapping[int, int],
    *,
    text_filter: str = "",
    bucket_filter: str = "Todos",
    only_new_uncontacted: bool = False,
) -> list[dict[str, Any]]:
    needle = str(text_filter or "").casefold().strip()
    out: list[dict[str, Any]] = []
    for row in rows:
        lead = dict(row)
        status = str(lead.get("status") or "")
        if status in FINAL_STATUSES:
            continue
        bucket_key = operational_bucket_key(lead, counts)
        if bucket_filter not in ("", "Todos") and bucket_key != bucket_filter:
            continue
        if only_new_uncontacted and bucket_key != "new_uncontacted":
            continue
        if needle and needle not in searchable_text(lead):
            continue
        lead["operational_bucket"] = bucket_key
        lead["operational_bucket_label"] = operational_bucket_label(bucket_key)
        lead.update(annotate_lead_aging(lead))
        out.append(lead)
    return out


def bucket_options() -> list[tuple[str, str]]:
    return [("Todos", "Todos")] + [(key, operational_bucket_label(key)) for key in BUCKET_ORDER]


def bucket_counts(rows: list[Mapping[str, Any]], counts: Mapping[int, int]) -> dict[str, int]:
    buckets = build_operational_buckets(rows, counts)
    return {key: len(buckets.get(key, [])) for key in BUCKET_ORDER}


def format_bucket_summary(rows: list[Mapping[str, Any]], counts: Mapping[int, int]) -> list[str]:
    totals = bucket_counts(rows, counts)
    return [f"{operational_bucket_label(key)}: {totals.get(key, 0)}" for key in BUCKET_ORDER]


def detail_option_label(lead: Mapping[str, Any]) -> str:
    score = int(lead.get("score") or 0)
    bucket = str(lead.get("operational_bucket_label") or lead.get("operational_bucket") or "")
    aging = lead.get("aging_days")
    aging_label = lead.get("aging_label") or ""
    aging_part = f" | {aging}d {aging_label}" if aging not in (None, "") else ""
    return f"#{lead.get('id', '')} | {lead.get('empresa', '')} | {lead.get('cidade', '')} | Score {score} | {bucket}{aging_part}"
