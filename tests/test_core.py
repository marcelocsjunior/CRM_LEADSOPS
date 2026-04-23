from pathlib import Path
import tempfile

from leadops import __version__
from leadops.db import import_rows, get_lead, list_leads, upsert_lead, init_db, update_lead, get_dashboard_snapshot
from leadops.messages import email_body, email_subject, first_contact_message, followup_message, classify_profile
from leadops.scoring import score_lead
from leadops.utils import gmail_compose_link, lead_key_from_payload, normalize_phone, whatsapp_link, sanitize_roundcube_base_url, roundcube_session_base_url, has_cpanel_session_token, roundcube_compose_link


def test_version_is_consolidated():
    assert __version__ == "2.3.3"


def test_phone_and_whatsapp_link():
    assert normalize_phone("(37) 98803-5291") == "5537988035291"
    assert "wa.me/5537988035291" in whatsapp_link("(37) 98803-5291", "Oi")


def test_lead_key_is_stable():
    a = {"empresa": "Laboratório Diagnosis", "cidade": "Formiga/MG", "site": "https://laboratoriodiagnosis.com.br/contato"}
    b = {"empresa": "Laboratorio Diagnosis", "cidade": "Formiga MG", "site": "www.laboratoriodiagnosis.com.br"}
    assert lead_key_from_payload(a) == lead_key_from_payload(b)


def test_scoring_reasons_and_no_saturation_for_common_case():
    lead = {"empresa": "Laboratório X", "cidade": "Formiga/MG", "segmento": "laboratório", "whatsapp_status": "Sim", "email_publico": "contato@x.com", "dor_provavel": "backup e resultados"}
    result = score_lead(lead)
    assert 45 <= result.score < 100
    assert result.motivos


def test_scoring_respects_pipeline_stage():
    new_lead = score_lead({"empresa": "Empresa X", "cidade": "Formiga/MG", "segmento": "laboratório", "email_publico": "x@x.com", "telefone": "37 99999-9999", "status": "Novo"})
    proposal = score_lead({"empresa": "Empresa X", "cidade": "Formiga/MG", "segmento": "laboratório", "email_publico": "x@x.com", "telefone": "37 99999-9999", "status": "Proposta"})
    lost = score_lead({"empresa": "Empresa X", "cidade": "Formiga/MG", "segmento": "laboratório", "email_publico": "x@x.com", "telefone": "37 99999-9999", "status": "Perdido"})
    assert proposal.score > new_lead.score
    assert lost.score < new_lead.score


def test_email_links():
    link = gmail_compose_link("contato@x.com", "Assunto", "Corpo")
    assert "mail.google.com" in link
    assert "contato%40x.com" in link


def test_upsert_preserves_existing_data_when_new_empty():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "leadops.db"
        init_db(db)
        first = {"empresa": "Empresa X", "cidade": "Formiga/MG", "email_publico": "contato@x.com", "telefone": "(37) 99999-9999"}
        lead_id = upsert_lead(db, first, source="test")
        second = {"empresa": "Empresa X", "cidade": "Formiga/MG", "email_publico": "", "telefone": ""}
        upsert_lead(db, second, source="test")
        lead = get_lead(db, lead_id)
        assert lead["email_publico"] == "contato@x.com"
        assert lead["telefone"] == "(37) 99999-9999"


def test_import_deduplicates():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "leadops.db"
        rows = [
            {"empresa": "Empresa X", "cidade": "Formiga/MG", "site": "x.com", "email_publico": "contato@x.com"},
            {"empresa": "Empresa X", "cidade": "Formiga/MG", "site": "https://x.com", "email_publico": ""},
        ]
        import_rows(db, rows, source="test")
        assert len(list_leads(db)) == 1


def test_messages_are_humanized_and_email_has_no_signature():
    lead = {"empresa": "Clínica de Imagem X", "segmento": "diagnóstico por imagem", "cidade": "Formiga"}
    msg = first_contact_message(lead)
    body = email_body(lead)
    assert classify_profile(lead) == "saude_imagem"
    assert "clínicas de imagem" in msg.lower()
    assert "ultrassom" in msg.lower()
    assert email_subject(lead) == "Apresentação – suporte técnico para clínica de imagem"
    assert "comercial@biotechti.com.br" not in body
    assert "Atenciosamente" not in body


def test_general_messages():
    lead = {"empresa": "Empresa X", "segmento": "comércio", "cidade": "Formiga"}
    assert "empresas aqui da região" in first_contact_message(lead).lower()
    assert email_subject(lead) == "Apoio técnico em TI para empresas"
    assert "só reforçando" in followup_message(2).lower()


def test_roundcube_cpanel_links_preserve_cpsess_for_compose():
    url = "https://webmail.biotechti.com.br/cpsess7643228940/3rdparty/roundcube/?_task=mail&_mbox=INBOX"
    safe_base = sanitize_roundcube_base_url(url)
    session_base = roundcube_session_base_url(url)
    assert has_cpanel_session_token(url) is True
    assert safe_base == "https://webmail.biotechti.com.br/3rdparty/roundcube/"
    assert session_base == "https://webmail.biotechti.com.br/cpsess7643228940/3rdparty/roundcube/"
    link = roundcube_compose_link(url, "contato@x.com", "Assunto", "Corpo")
    assert "cpsess7643228940" in link
    assert "_action=compose" in link
    assert "contato%40x.com" in link


def test_pipeline_status_is_normalized_on_update():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "leadops.db"
        lead_id = upsert_lead(db, {"empresa": "Empresa X", "cidade": "Formiga/MG", "status": "Reunião agendada"}, source="test")
        lead = get_lead(db, lead_id)
        assert lead["status"] == "Reunião"
        update_lead(db, lead_id, {"status": "Proposta enviada"}, source="test")
        lead = get_lead(db, lead_id)
        assert lead["status"] == "Proposta"


def test_operational_snapshot_counts():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "leadops.db"
        upsert_lead(db, {"empresa": "Empresa X", "cidade": "Formiga/MG", "status": "Novo"}, source="test")
        snap = get_dashboard_snapshot(db)
        assert snap["leads_total"] == 1
        assert snap["new_total"] == 1


def test_app_has_no_removed_streamlit_patterns():
    app_text = Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
    assert "st.components.v1.html" not in app_text
    assert "use_container_width=" not in app_text


def test_detail_tab_uses_stable_selectbox_and_textareas():
    app_text = Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
    assert 'session_key = "detail_selected_lead_id"' in app_text
    assert 'st.text_area(' in app_text


def test_detail_tab_has_operational_queue_filters():
    app_text = Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
    assert 'Novos/não contactados' in app_text
    assert 'Abrir app e-mail (Android)' in app_text
    assert 'detail_only_new_uncontacted' in app_text


def test_interaction_counts_helper():
    from leadops.db import add_interaction, list_interaction_counts

    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "leadops.db"
        lead_id = upsert_lead(db, {"empresa": "Empresa Y", "cidade": "Arcos/MG", "status": "Novo"}, source="test")
        assert list_interaction_counts(db).get(lead_id, 0) == 0
        add_interaction(db, lead_id, "WhatsApp", "Primeiro contato", "teste", "", "Contatado")
        assert list_interaction_counts(db)[lead_id] == 1
