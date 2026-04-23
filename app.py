from __future__ import annotations

import os
import hashlib
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

from leadops import __version__
from leadops.db import (
    FINAL_STATUSES,
    STATUS_DEFAULTS,
    add_interaction,
    backup_db,
    get_dashboard_snapshot,
    get_lead,
    get_settings,
    import_rows,
    init_db,
    list_audit_events,
    list_interactions,
    list_leads,
    list_interaction_counts,
    update_lead,
    update_settings,
    upsert_lead,
)
from leadops.messages import (
    call_script,
    email_body,
    email_subject,
    first_contact_message,
    followup_message,
    recommend_next_action,
    signature,
    signature_html,
)
from leadops.scoring import score_lead
from leadops.utils import (
    add_days_iso,
    first_email,
    gmail_compose_link,
    mailto_link,
    outlook_compose_link,
    has_cpanel_session_token,
    roundcube_compose_link,
    roundcube_simple_compose_link,
    roundcube_session_base_url,
    sanitize_roundcube_base_url,
    read_csv_rows,
    today_iso,
    whatsapp_link,
)

APP_TITLE = f"LeadOps TI v{__version__}"
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "data" / "leadops.db"
SEED_CSV = BASE_DIR / "data" / "leads_seed.csv"

st.set_page_config(page_title=APP_TITLE, page_icon="📇", layout="wide")


PIPELINE_ORDER = STATUS_DEFAULTS


def db_path() -> Path:
    return Path(os.getenv("LEADOPS_DB", DEFAULT_DB))


def refresh() -> None:
    st.rerun()


def normalize_df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    preferred = [
        "id",
        "empresa",
        "cidade",
        "segmento",
        "score",
        "prioridade",
        "status",
        "canal_prioritario",
        "whatsapp_status",
        "whatsapp_numero",
        "email_publico",
        "telefone",
        "proximo_followup",
        "ultimo_contato",
        "dor_provavel",
        "confianca_contato",
        "fonte_contato",
    ]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    return df[cols]


def due_today(rows: list[dict]) -> list[dict]:
    today = today_iso()
    due = []
    for r in rows:
        status = str(r.get("status") or "")
        if status in FINAL_STATUSES:
            continue
        follow = str(r.get("proximo_followup") or "")
        if follow and follow <= today:
            due.append(r)
    return due


def new_leads(rows: list[dict]) -> list[dict]:
    return [r for r in rows if str(r.get("status") or "") == "Novo"]


def interaction_count(lead: dict, counts: dict[int, int]) -> int:
    return int(counts.get(int(lead.get("id") or 0), 0))


def is_new_uncontacted(lead: dict, counts: dict[int, int]) -> bool:
    if str(lead.get("status") or "") != "Novo":
        return False
    if str(lead.get("ultimo_contato") or "").strip():
        return False
    return interaction_count(lead, counts) == 0


def is_contacted_waiting_response(lead: dict, counts: dict[int, int]) -> bool:
    status = str(lead.get("status") or "")
    return status == "Contatado" and interaction_count(lead, counts) > 0


def detail_reason_label(lead: dict, counts: dict[int, int]) -> str:
    status = str(lead.get("status") or "")
    follow = str(lead.get("proximo_followup") or "")
    if status in FINAL_STATUSES:
        return status
    if follow and follow <= today_iso():
        return f"Follow-up {follow}"
    if is_new_uncontacted(lead, counts):
        return "Novo / não contactado"
    if is_contacted_waiting_response(lead, counts):
        return "Contatado / aguardando retorno"
    if status == "Respondeu":
        return "Respondeu / avançar"
    if status == "Reunião":
        return "Reunião / preparar proposta"
    if status == "Proposta":
        return "Proposta / acompanhar"
    return status or "Sem status"


def detail_sort_key(lead: dict, counts: dict[int, int]) -> tuple:
    status = str(lead.get("status") or "")
    follow = str(lead.get("proximo_followup") or "")
    score = int(lead.get("score") or 0)
    last_touch = str(lead.get("ultimo_contato") or lead.get("created_at") or "9999-12-31")
    empresa = str(lead.get("empresa") or "")

    if status in FINAL_STATUSES:
        bucket = 9
    elif follow and follow <= today_iso():
        bucket = 0
    elif is_new_uncontacted(lead, counts):
        bucket = 1
    elif is_contacted_waiting_response(lead, counts):
        bucket = 2
    elif status == "Respondeu":
        bucket = 3
    elif status == "Reunião":
        bucket = 4
    elif status == "Proposta":
        bucket = 5
    elif status == "Novo":
        bucket = 6
    else:
        bucket = 7

    return (bucket, last_touch, -score, empresa.casefold())


def pipeline_counts(rows: list[dict]) -> dict[str, int]:
    counts = {status: 0 for status in PIPELINE_ORDER}
    for row in rows:
        status = str(row.get("status") or "")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _stable_widget_key(*parts: object) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def copy_widget(label: str, text: str, height: int = 150, context: str = "") -> None:
    value = "" if text is None else str(text)
    st.markdown(f"**{label}**")
    st.text_area(
        label,
        value=value,
        height=height,
        key=f"copy_{_stable_widget_key(context, label, value)}",
        label_visibility="collapsed",
    )
    st.caption("Dica: toque/clique no campo acima para selecionar e copiar o conteúdo.")


def render_sidebar(db: Path) -> None:
    st.sidebar.title(APP_TITLE)
    st.sidebar.caption("Mini-CRM local para prospecção B2B + Roundcube/cPanel assistido")
    st.sidebar.write(f"DB: `{db}`")

    if st.sidebar.button("Inicializar / migrar banco", width="stretch"):
        init_db(db)
        st.sidebar.success("Banco inicializado/migrado.")

    if st.sidebar.button("Backup manual do banco", width="stretch"):
        target = backup_db(db, "manual")
        if target:
            st.sidebar.success(f"Backup criado: {target.name}")
        else:
            st.sidebar.info("Banco ainda não existe.")

    if st.sidebar.button("Carregar seed inicial", width="stretch"):
        init_db(db)
        backup_db(db, "antes_seed")
        rows = read_csv_rows(SEED_CSV)
        count = import_rows(db, rows, source="seed")
        st.sidebar.success(f"{count} leads importados/atualizados sem duplicar.")
        refresh()

    st.sidebar.divider()
    uploaded = st.sidebar.file_uploader("Importar CSV", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded, dtype=str).fillna("")
        if "empresa" not in [c.lower() for c in df.columns]:
            st.sidebar.error("CSV precisa ter coluna 'empresa' ou 'Empresa'.")
        elif st.sidebar.button("Confirmar importação CSV", width="stretch"):
            init_db(db)
            backup_db(db, "antes_import_csv")
            rows = df.rename(columns={c: c.lower() for c in df.columns}).to_dict(orient="records")
            count = import_rows(db, rows, source="csv_upload")
            st.sidebar.success(f"{count} leads importados/atualizados sem apagar dados bons.")
            refresh()

    st.sidebar.divider()
    st.sidebar.info("O app não dispara WhatsApp/e-mail automaticamente. Ele prepara e registra a ação.")


def quick_register_buttons(db: Path, lead: dict) -> None:
    lead_id = int(lead["id"])
    c1, c2, c3 = st.columns(3)
    if c1.button("Registrar WhatsApp enviado + D+2", width="stretch", key=f"quick_whatsapp_{lead_id}"):
        add_interaction(db, lead_id, "WhatsApp", "Primeiro contato", "Mensagem enviada/preparada pelo LeadOps", add_days_iso(2), "Contatado")
        st.success("WhatsApp registrado. Follow-up D+2 definido.")
        refresh()
    if c2.button("Registrar e-mail enviado + D+3", width="stretch", key=f"quick_email_{lead_id}"):
        add_interaction(db, lead_id, "E-mail", "E-mail enviado", "E-mail de apresentação enviado/preparado pelo LeadOps", add_days_iso(3), "Contatado")
        st.success("E-mail registrado. Follow-up D+3 definido.")
        refresh()
    if c3.button("Marcar Não contatar", width="stretch", key=f"quick_nocontact_{lead_id}"):
        update_lead(db, lead_id, {"status": "Não contatar", "nao_contatar_motivo": "Marcado manualmente"}, source="ui")
        add_interaction(db, lead_id, "Sistema", "Não contatar", "Lead removido da cadência", "", "Não contatar")
        st.warning("Lead marcado como Não contatar.")
        refresh()


def render_dashboard(db: Path) -> None:
    settings = get_settings(db)
    st.title(f"📇 {APP_TITLE}")
    st.caption("Prospecção controlada: lead público, score calibrado, funil comercial, webmail pronto, follow-up e histórico.")

    rows = list_leads(db)
    df = normalize_df(rows)
    snapshot = get_dashboard_snapshot(db)
    counts = pipeline_counts(rows)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Leads", snapshot["leads_total"])
    c2.metric("Ativos", snapshot["active_total"])
    c3.metric("Interações", snapshot["interactions_total"])
    c4.metric("Follow-up hoje", snapshot["due_total"])
    c5.metric("Novos", snapshot["new_total"])
    c6.metric("Alta prioridade", sum(1 for r in rows if str(r.get("prioridade")) == "Alta"))

    if snapshot["interactions_total"] == 0 and snapshot["leads_total"] > 0:
        st.warning("Operação ainda não começou no banco atual: há leads carregados, mas nenhuma interação registrada.")

    tabs = st.tabs(["Hoje", "Funil", "Leads", "Adicionar", "Detalhe", "Exportar", "Config"])

    with tabs[0]:
        st.subheader("Ataque do dia")
        due = due_today(rows)
        if due:
            st.warning(f"{len(due)} follow-up(s) vencido(s) ou para hoje.")
            st.dataframe(normalize_df(due), width="stretch", hide_index=True)
        else:
            st.success("Nada vencido para hoje.")

        st.subheader("Próximos 5 contatos recomendados")
        candidates = [r for r in rows if str(r.get("status") or "") not in FINAL_STATUSES]
        stage_rank = {"Proposta": 1, "Reunião": 2, "Respondeu": 3, "Contatado": 4, "Novo": 5}
        candidates = sorted(candidates, key=lambda r: (stage_rank.get(str(r.get("status") or ""), 9), -int(r.get("score") or 0)))[:5]
        if candidates:
            for r in candidates:
                action, reason = recommend_next_action(r)
                st.markdown(f"**#{r['id']} — {r['empresa']}** | {r.get('cidade','')} | Score {r.get('score',0)} | Status {r.get('status','')}")
                st.caption(f"Ação: {action}. Motivo: {reason}")
        else:
            st.info("Sem candidatos ativos.")

        st.subheader("Top 10 por score")
        st.dataframe(df.head(10), width="stretch", hide_index=True)

    with tabs[1]:
        st.subheader("Visão de funil")
        funnel_rows = []
        total = max(1, snapshot["leads_total"])
        for status in PIPELINE_ORDER:
            qty = counts.get(status, 0)
            funnel_rows.append({"status": status, "total": qty, "% base": round((qty / total) * 100, 1)})
        funnel_df = pd.DataFrame(funnel_rows)
        st.dataframe(funnel_df, width="stretch", hide_index=True)

        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Respondeu+", counts.get("Respondeu", 0) + counts.get("Reunião", 0) + counts.get("Proposta", 0))
        f2.metric("Reuniões", counts.get("Reunião", 0))
        f3.metric("Propostas", counts.get("Proposta", 0))
        f4.metric("Conversão", counts.get("Ganhou", 0))

        st.caption("Funil padrão: Novo → Contatado → Respondeu → Reunião → Proposta → Ganhou/Perdido. 'Não contatar' fica fora da conversão.")

    with tabs[2]:
        st.subheader("Base de leads")
        if df.empty:
            st.info("Sem leads. Carregue o seed inicial ou importe um CSV.")
        else:
            status_options = ["Todos"] + STATUS_DEFAULTS
            col1, col2 = st.columns([1, 2])
            status_filter = col1.selectbox("Filtrar por status", status_options)
            text_filter = col2.text_input("Filtrar por cidade/empresa/segmento")
            view = df.copy()
            if status_filter != "Todos":
                view = view[view["status"].fillna("") == status_filter]
            if text_filter:
                mask = view.apply(lambda row: text_filter.lower() in " ".join(map(str, row.values)).lower(), axis=1)
                view = view[mask]
            st.dataframe(view, width="stretch", hide_index=True)

    with tabs[3]:
        st.subheader("Adicionar / atualizar lead")
        with st.form("lead_form"):
            col1, col2 = st.columns(2)
            empresa = col1.text_input("Empresa *")
            cidade = col2.text_input("Cidade")
            segmento = col1.text_input("Segmento")
            site = col2.text_input("Site")
            email = col1.text_input("E-mail público")
            telefone = col2.text_input("Telefone")
            whatsapp_status = col1.selectbox("WhatsApp", ["", "Sim", "Provável", "Não"])
            whatsapp_numero = col2.text_input("Número WhatsApp")
            decisor = col1.text_input("Decisor provável")
            canal = col2.selectbox("Canal prioritário", ["WhatsApp", "Telefone → e-mail", "E-mail → WhatsApp", "E-mail", "Telefone"])
            fonte = col1.text_input("Fonte do contato")
            confianca = col2.selectbox("Confiança", ["", "Alta", "Média", "Baixa", "Inferida"])
            dor = st.text_area("Dor provável / sinal de oportunidade")
            observacoes = st.text_area("Observações")
            submitted = st.form_submit_button("Salvar lead")

        if submitted:
            if not empresa.strip():
                st.error("Empresa é obrigatória.")
            else:
                payload = {
                    "empresa": empresa.strip(),
                    "cidade": cidade.strip(),
                    "segmento": segmento.strip(),
                    "site": site.strip(),
                    "email_publico": email.strip(),
                    "telefone": telefone.strip(),
                    "whatsapp_status": whatsapp_status.strip(),
                    "whatsapp_numero": whatsapp_numero.strip(),
                    "decisor": decisor.strip(),
                    "canal_prioritario": canal.strip(),
                    "dor_provavel": dor.strip(),
                    "observacoes": observacoes.strip(),
                    "fonte_contato": fonte.strip(),
                    "confianca_contato": confianca.strip(),
                    "status": "Novo",
                }
                result = score_lead(payload)
                payload["score"] = result.score
                payload["prioridade"] = result.prioridade
                upsert_lead(db, payload, source="ui", preserve_commercial_state=True)
                st.success(f"Lead salvo/atualizado. Score {result.score} / prioridade {result.prioridade}.")
                refresh()

    with tabs[4]:
        st.subheader("Detalhe e ação")
        if not rows:
            st.info("Sem leads carregados.")
        else:
            interaction_counts = list_interaction_counts(db)
            queue_rows = sorted(rows, key=lambda r: detail_sort_key(r, interaction_counts))

            filter_col1, filter_col2 = st.columns([2, 1])
            detail_text_filter = filter_col1.text_input("Buscar lead na fila", key="detail_search", placeholder="Empresa, cidade, segmento, e-mail ou telefone")
            only_new_uncontacted = filter_col2.checkbox(
                "Novos/não contactados",
                value=False,
                key="detail_only_new_uncontacted",
                help="Mostra somente leads em status Novo e sem qualquer contato/interação registrado.",
            )

            filtered_rows = [r for r in queue_rows if str(r.get("status") or "") not in FINAL_STATUSES]
            if only_new_uncontacted:
                filtered_rows = [r for r in filtered_rows if is_new_uncontacted(r, interaction_counts)]
            if detail_text_filter:
                needle = detail_text_filter.casefold()
                filtered_rows = [
                    r for r in filtered_rows
                    if needle in " ".join([
                        str(r.get("empresa") or ""),
                        str(r.get("cidade") or ""),
                        str(r.get("segmento") or ""),
                        str(r.get("email_publico") or ""),
                        str(r.get("telefone") or ""),
                        str(r.get("whatsapp_numero") or ""),
                    ]).casefold()
                ]

            st.caption(f"Fila atual: {len(filtered_rows)} lead(s). Ordenação prioriza follow-up vencido, novos/não contactados e leads em andamento.")

            if not filtered_rows:
                st.warning("Nenhum lead encontrado com os filtros atuais.")
                return

            lead_lookup = {int(r["id"]): r for r in filtered_rows}
            lead_ids = list(lead_lookup.keys())

            session_key = "detail_selected_lead_id"
            if session_key not in st.session_state or st.session_state[session_key] not in lead_lookup:
                st.session_state[session_key] = lead_ids[0]

            current_index = lead_ids.index(int(st.session_state[session_key]))
            nav1, nav2, nav3 = st.columns([1, 1, 2])
            if nav1.button("◀ Anterior", width="stretch", disabled=current_index == 0, key="detail_prev"):
                st.session_state[session_key] = lead_ids[current_index - 1]
                st.rerun()
            if nav2.button("Próximo ▶", width="stretch", disabled=current_index >= len(lead_ids) - 1, key="detail_next"):
                st.session_state[session_key] = lead_ids[current_index + 1]
                st.rerun()
            nav3.caption(f"Lead {current_index + 1} de {len(lead_ids)} na fila")

            def _format_lead_option(current_id: int) -> str:
                current = lead_lookup.get(int(current_id), {})
                score = int(current.get("score") or 0)
                reason = detail_reason_label(current, interaction_counts)
                return f"#{current.get('id', current_id)} | {current.get('empresa', '')} | {current.get('cidade', '')} | Score {score} | {reason}"

            lead_id = int(
                st.selectbox(
                    "Lead",
                    lead_ids,
                    format_func=_format_lead_option,
                    key=session_key,
                )
            )
            lead = get_lead(db, lead_id) or lead_lookup.get(lead_id)
            if lead:
                action, reason = recommend_next_action(lead)
                score_info = score_lead(lead)
                st.info(f"Próxima ação recomendada: **{action}** — {reason}")

                left, right = st.columns([1.05, 1.15])
                with left:
                    st.markdown(f"### {lead['empresa']}")
                    st.write(f"**Cidade:** {lead.get('cidade','')}")
                    st.write(f"**Segmento:** {lead.get('segmento','')}")
                    st.write(f"**Score:** {lead.get('score', 0)} | **Prioridade:** {lead.get('prioridade','')}")
                    st.write(f"**Status:** {lead.get('status','')}")
                    st.write(f"**Canal:** {lead.get('canal_prioritario','')}")
                    st.write(f"**E-mail:** {lead.get('email_publico','')}")
                    st.write(f"**Telefone:** {lead.get('telefone','')}")
                    st.write(f"**WhatsApp:** {lead.get('whatsapp_status','')} {lead.get('whatsapp_numero','')}")
                    st.write(f"**Fonte:** {lead.get('fonte_contato','')} | **Confiança:** {lead.get('confianca_contato','')}")
                    st.write(f"**Dor provável:** {lead.get('dor_provavel','')}")
                    if score_info.motivos:
                        st.markdown("**Motivos do score:**")
                        st.markdown("\n".join(f"- {m}" for m in score_info.motivos))

                with right:
                    st.markdown("### WhatsApp / Mensagens")
                    first_msg = first_contact_message(lead, settings)
                    copy_widget("Mensagem inicial WhatsApp", first_msg, height=180, context=f"lead_{lead_id}_wa_initial")
                    copy_widget("Follow-up D+2", followup_message(2, settings), height=140, context=f"lead_{lead_id}_wa_d2")
                    copy_widget("Follow-up D+7", followup_message(7, settings), height=140, context=f"lead_{lead_id}_wa_d7")
                    phone = lead.get("whatsapp_numero") or lead.get("telefone")
                    link = whatsapp_link(phone, first_msg)
                    if link:
                        st.link_button("Abrir WhatsApp com mensagem (opcional)", link, width="stretch")
                    else:
                        st.warning("Sem número válido para gerar link WhatsApp.")

                st.divider()
                st.markdown("### Webmail assistido")
                to_email = first_email(lead.get("email_publico"))
                subject = email_subject(lead)
                body = email_body(lead, settings)
                copy_widget("Script de ligação", call_script(lead, settings), height=150, context=f"lead_{lead_id}_call_script")
                copy_widget("Para", to_email, height=90, context=f"lead_{lead_id}_email_to")
                copy_widget("Assunto", subject, height=90, context=f"lead_{lead_id}_email_subject")
                copy_widget("Corpo do e-mail", body, height=300, context=f"lead_{lead_id}_email_body")
                e1, e2, e3 = st.columns(3)
                if to_email:
                    e1.link_button("Abrir Gmail pronto", gmail_compose_link(to_email, subject, body), width="stretch")
                    e2.link_button("Abrir Outlook pronto", outlook_compose_link(to_email, subject, body), width="stretch")
                    e3.link_button("Abrir app e-mail (Android)", mailto_link(to_email, subject, body), width="stretch")
                else:
                    st.warning("Lead sem e-mail público válido.")

                webmail_url = settings.get("webmail_url") or "https://webmail.biotechti.com.br"
                login_base = sanitize_roundcube_base_url(webmail_url)
                roundcube_base = roundcube_session_base_url(webmail_url)
                has_token = has_cpanel_session_token(webmail_url)
                st.markdown("#### Roundcube / cPanel")
                if has_token:
                    st.success("URL atual contém cpsess: compose interno deve abrir sem erro 401 enquanto a sessão estiver válida.")
                else:
                    st.warning("URL sem cpsess. No cPanel, o compose interno pode gerar HTTP 401. Faça login, copie a URL atual do Roundcube/InBox com /cpsess.../ e cole em Config → URL do webmail.")
                st.caption(f"Base usada para compose: `{roundcube_base}`")
                r1, r2, r3, r4 = st.columns(4)
                if to_email:
                    r1.link_button("Roundcube pronto", roundcube_compose_link(webmail_url, to_email, subject, body, "underscore"), width="stretch")
                    r2.link_button("Roundcube alternativo", roundcube_compose_link(webmail_url, to_email, subject, body, "plain"), width="stretch")
                r3.link_button("Roundcube compose simples", roundcube_simple_compose_link(webmail_url), width="stretch")
                r4.link_button("Abrir webmail/login", login_base, width="stretch")
                st.caption("Se aparecer erro 401/token inválido, atualize no app a URL atual do Roundcube após login. Se o provedor ignorar parâmetros, use Copiar Para/Assunto/Corpo.")

                html_sig = signature_html(settings)
                if html_sig:
                    with st.expander("Assinatura HTML do Roundcube"):
                        copy_widget("Assinatura HTML para configurar/colar no Roundcube", html_sig, height=260, context="signature_html_preview")
                        st.markdown("Prévia da assinatura:", unsafe_allow_html=False)
                        st.markdown(html_sig, unsafe_allow_html=True)

                quick_register_buttons(db, lead)

                st.divider()
                st.subheader("Registrar ação manual")
                with st.form(f"interaction_form_{lead_id}"):
                    c1, c2, c3 = st.columns(3)
                    canal = c1.selectbox("Canal", ["WhatsApp", "Telefone", "E-mail", "Presencial", "Sistema", "Outro"])
                    acao = c2.selectbox("Ação", ["Primeiro contato", "Follow-up D+2", "Follow-up D+7", "Ligação", "E-mail enviado", "Reunião", "Proposta", "Não contatar", "Outro"])
                    current_status = lead.get("status") if lead.get("status") in STATUS_DEFAULTS else "Novo"
                    status_resultante = c3.selectbox("Novo status", STATUS_DEFAULTS, index=STATUS_DEFAULTS.index(current_status))
                    resumo = st.text_area("Resumo")
                    prox = st.selectbox("Próximo follow-up", ["", "D+2", "D+3", "D+7", "D+30", "D+60", "Manual"])
                    manual_date = st.date_input("Data manual", value=date.today()) if prox == "Manual" else None
                    ok = st.form_submit_button("Registrar")

                if ok:
                    next_date = ""
                    if prox.startswith("D+"):
                        next_date = add_days_iso(int(prox.replace("D+", "")))
                    elif prox == "Manual" and manual_date:
                        next_date = manual_date.isoformat()
                    add_interaction(db, lead_id, canal, acao, resumo, next_date, status_resultante)
                    st.success("Ação registrada.")
                    refresh()

                h1, h2 = st.tabs(["Histórico", "Auditoria"])
                with h1:
                    hist = list_interactions(db, lead_id)
                    if hist:
                        st.dataframe(pd.DataFrame(hist), width="stretch", hide_index=True)
                    else:
                        st.info("Sem histórico para este lead.")
                with h2:
                    audit = list_audit_events(db, lead_id)
                    if audit:
                        st.dataframe(pd.DataFrame(audit), width="stretch", hide_index=True)
                    else:
                        st.info("Sem eventos de auditoria para este lead.")

    with tabs[5]:
        st.subheader("Exportar")
        if df.empty:
            st.info("Nada para exportar.")
        else:
            active = df[df["status"].fillna("").isin(FINAL_STATUSES) == False] if "status" in df.columns else df
            due_df = normalize_df(due_today(rows))
            hot_df = df[df["prioridade"].fillna("").isin(["Alta", "Média/Alta"])] if "prioridade" in df.columns else df
            pipeline_df = pd.DataFrame([{"status": status, "total": counts.get(status, 0)} for status in PIPELINE_ORDER])

            exports = {
                "leadops_export_todos.csv": df,
                "leadops_export_ativos.csv": active,
                "leadops_export_followups_hoje.csv": due_df,
                "leadops_export_quentes.csv": hot_df,
                "leadops_export_funil.csv": pipeline_df,
            }
            for filename, export_df in exports.items():
                csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    f"Baixar {filename}",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    width="stretch",
                )
            st.caption("Para Excel/Google Sheets: importar como UTF-8 com separador vírgula.")

    with tabs[6]:
        st.subheader("Configuração comercial")
        with st.form("settings_form"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome", settings.get("nome", ""))
            cargo = col2.text_input("Cargo", settings.get("cargo", ""))
            empresa = col1.text_input("Empresa", settings.get("empresa", ""))
            email_remetente = col2.text_input("E-mail comercial/remetente", settings.get("email_remetente", ""))
            telefone_assinatura = col1.text_input("Telefone assinatura", settings.get("telefone_assinatura", ""))
            website = col2.text_input("Website assinatura", settings.get("website", ""))
            webmail_url = col1.text_input("URL do webmail ou URL atual do Roundcube após login", settings.get("webmail_url", "https://webmail.biotechti.com.br"), help="Para cPanel/Roundcube, cole a URL atual que aparece dentro do Roundcube contendo /cpsess.../. Ex.: https://webmail.dominio/cpsess123/3rdparty/roundcube/?_task=mail&_mbox=INBOX")
            webmail_tipo = col2.selectbox("Tipo de webmail", ["roundcube_cpanel", "generico"], index=0 if settings.get("webmail_tipo", "roundcube_cpanel") == "roundcube_cpanel" else 1)
            assinatura_html_cfg = st.text_area("Assinatura HTML Roundcube", settings.get("assinatura_html", ""), height=260)
            salvar = st.form_submit_button("Salvar configurações")
        if salvar:
            update_settings(db, {
                "nome": nome,
                "cargo": cargo,
                "empresa": empresa,
                "email_remetente": email_remetente,
                "telefone_assinatura": telefone_assinatura,
                "website": website,
                "webmail_url": webmail_url,
                "webmail_tipo": webmail_tipo,
                "assinatura_html": assinatura_html_cfg,
            })
            st.success("Configurações salvas.")
            refresh()
        st.markdown("### Diagnóstico Roundcube/cPanel")
        current_settings = get_settings(db)
        configured_url = current_settings.get("webmail_url", "")
        st.write("**cpsess detectado:**", "Sim" if has_cpanel_session_token(configured_url) else "Não")
        st.write("**Base compose:**", roundcube_session_base_url(configured_url))
        st.write("**Base login segura:**", sanitize_roundcube_base_url(configured_url))

        st.markdown("### Assinatura atual")
        st.code(signature(current_settings))
        if signature_html(current_settings):
            with st.expander("Prévia da assinatura HTML"):
                st.markdown(signature_html(current_settings), unsafe_allow_html=True)


def main() -> None:
    db = db_path()
    init_db(db)
    render_sidebar(db)
    render_dashboard(db)


if __name__ == "__main__":
    main()
