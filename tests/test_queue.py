from datetime import date, timedelta

from leadops.queue import (
    build_operational_buckets,
    operational_bucket_key,
    operational_bucket_label,
)


def test_operational_bucket_key_uses_followup_and_stage():
    counts = {1: 0, 2: 1, 3: 0, 4: 0, 5: 0}
    today = date.today()

    critical = {"id": 1, "status": "Contatado", "proximo_followup": (today - timedelta(days=6)).isoformat()}
    due_today = {"id": 2, "status": "Contatado", "proximo_followup": today.isoformat()}
    new_uncontacted = {"id": 3, "status": "Novo", "ultimo_contato": ""}
    replied = {"id": 4, "status": "Respondeu"}
    upcoming = {"id": 5, "status": "Proposta", "proximo_followup": (today + timedelta(days=2)).isoformat()}

    assert operational_bucket_key(critical, counts) == "critical_overdue"
    assert operational_bucket_key(due_today, counts) == "today"
    assert operational_bucket_key(new_uncontacted, counts) == "new_uncontacted"
    assert operational_bucket_key(replied, counts) == "ready_to_advance"
    assert operational_bucket_key(upcoming, counts) == "ready_to_advance"


def test_build_operational_buckets_groups_active_leads():
    today = date.today()
    rows = [
        {"id": 1, "status": "Contatado", "proximo_followup": (today - timedelta(days=6)).isoformat()},
        {"id": 2, "status": "Novo", "ultimo_contato": ""},
        {"id": 3, "status": "Reunião"},
        {"id": 4, "status": "Perdido"},
    ]
    counts = {1: 1, 2: 0, 3: 0, 4: 0}
    buckets = build_operational_buckets(rows, counts)

    assert len(buckets["critical_overdue"]) == 1
    assert len(buckets["new_uncontacted"]) == 1
    assert len(buckets["ready_to_advance"]) == 1
    assert all(str(item.get("status")) != "Perdido" for items in buckets.values() for item in items)
    assert operational_bucket_label("today") == "Hoje"
