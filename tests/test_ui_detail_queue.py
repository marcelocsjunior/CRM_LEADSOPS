from datetime import date, timedelta

from leadops.ui.detail_queue import (
    bucket_options,
    detail_option_label,
    filter_active_rows,
    format_bucket_summary,
)


def test_bucket_options_include_all_and_named_buckets():
    options = bucket_options()
    assert options[0] == ("Todos", "Todos")
    assert ("new_uncontacted", "Novos sem contato") in options
    assert ("critical_overdue", "Follow-up crítico") in options


def test_filter_active_rows_enriches_bucket_and_aging():
    today = date.today()
    rows = [
        {
            "id": 1,
            "empresa": "Clinica Alfa",
            "cidade": "Formiga",
            "status": "Novo",
            "ultimo_contato": "",
            "created_at": (today - timedelta(days=4)).isoformat(),
            "updated_at": (today - timedelta(days=4)).isoformat(),
            "score": 80,
        },
        {
            "id": 2,
            "empresa": "Empresa Perdida",
            "cidade": "Arcos",
            "status": "Perdido",
        },
    ]
    counts = {1: 0, 2: 0}

    filtered = filter_active_rows(rows, counts, bucket_filter="new_uncontacted")

    assert len(filtered) == 1
    assert filtered[0]["operational_bucket"] == "new_uncontacted"
    assert filtered[0]["operational_bucket_label"] == "Novos sem contato"
    assert filtered[0]["aging_days"] >= 4
    assert filtered[0]["aging_label"] in {"Atenção", "Envelhecido"}


def test_filter_active_rows_applies_text_search():
    rows = [
        {"id": 1, "empresa": "Clinica Alfa", "cidade": "Formiga", "status": "Novo", "ultimo_contato": ""},
        {"id": 2, "empresa": "Laboratorio Beta", "cidade": "Arcos", "status": "Novo", "ultimo_contato": ""},
    ]
    counts = {1: 0, 2: 0}

    filtered = filter_active_rows(rows, counts, text_filter="beta")

    assert len(filtered) == 1
    assert filtered[0]["empresa"] == "Laboratorio Beta"


def test_format_bucket_summary_and_detail_label():
    today = date.today()
    rows = [
        {"id": 1, "empresa": "Clinica Alfa", "cidade": "Formiga", "status": "Contatado", "proximo_followup": (today - timedelta(days=6)).isoformat()},
        {"id": 2, "empresa": "Laboratorio Beta", "cidade": "Arcos", "status": "Novo", "ultimo_contato": ""},
    ]
    counts = {1: 1, 2: 0}

    summary = format_bucket_summary(rows, counts)
    assert any(item.startswith("Follow-up crítico:") for item in summary)
    assert any(item.startswith("Novos sem contato:") for item in summary)

    filtered = filter_active_rows(rows, counts)
    label = detail_option_label(filtered[0])
    assert "Score" in label
    assert "|" in label
