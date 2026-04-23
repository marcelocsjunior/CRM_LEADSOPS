from datetime import date

from leadops.aging import (
    aging_bucket,
    aging_days,
    aging_label,
    annotate_lead_aging,
    stage_entry_date,
)


def test_stage_entry_date_prefers_last_status_change_event():
    lead = {
        "status": "Proposta",
        "created_at": "2026-04-01 09:00:00",
        "updated_at": "2026-04-20 10:00:00",
    }
    audit = [
        {"field": "status", "new_value": "Proposta", "ts": "2026-04-18 08:00:00"},
        {"field": "status", "new_value": "Reunião", "ts": "2026-04-12 08:00:00"},
    ]
    assert stage_entry_date(lead, audit) == date(2026, 4, 18)


def test_stage_entry_date_falls_back_to_created_at_for_novo():
    lead = {
        "status": "Novo",
        "created_at": "2026-04-10 09:00:00",
        "updated_at": "2026-04-20 10:00:00",
    }
    assert stage_entry_date(lead, []) == date(2026, 4, 10)


def test_aging_days_uses_stage_entry_date():
    lead = {
        "status": "Contatado",
        "created_at": "2026-04-01 09:00:00",
        "updated_at": "2026-04-20 10:00:00",
    }
    audit = [
        {"field": "status", "new_value": "Contatado", "ts": "2026-04-19 08:00:00"},
    ]
    assert aging_days(lead, audit, today=date(2026, 4, 23)) == 4


def test_aging_bucket_changes_by_threshold_and_stage():
    assert aging_bucket("Novo", 1) == "ok"
    assert aging_bucket("Novo", 3) == "warning"
    assert aging_bucket("Novo", 7) == "critical"
    assert aging_bucket("Reunião", 1) == "warning"
    assert aging_bucket("Reunião", 3) == "critical"


def test_aging_label_and_annotation():
    lead = {
        "status": "Respondeu",
        "created_at": "2026-04-01 09:00:00",
        "updated_at": "2026-04-20 10:00:00",
    }
    audit = [
        {"field": "status", "new_value": "Respondeu", "ts": "2026-04-20 08:00:00"},
    ]
    annotated = annotate_lead_aging(lead, audit, today=date(2026, 4, 23))
    assert annotated["aging_days"] == 3
    assert annotated["aging_bucket"] == "warning"
    assert annotated["aging_label"] == aging_label("Respondeu", 3)
    assert annotated["stage_entry_date"] == "2026-04-20"


def test_final_status_has_zero_aging():
    lead = {
        "status": "Ganhou",
        "created_at": "2026-04-01 09:00:00",
    }
    assert aging_days(lead, today=date(2026, 4, 23)) == 0
