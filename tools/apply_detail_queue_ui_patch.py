from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"

IMPORT_ANCHOR = "from leadops.scoring import score_lead\n"
IMPORT_BLOCK = """from leadops.ui.detail_queue import (\n    bucket_options,\n    detail_option_label,\n    filter_active_rows,\n    format_bucket_summary,\n)\n"""

OLD_FILTER_BLOCK = '''            interaction_counts = list_interaction_counts(db)
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
'''

NEW_FILTER_BLOCK = '''            interaction_counts = list_interaction_counts(db)
            queue_rows = sorted(rows, key=lambda r: detail_sort_key(r, interaction_counts))

            bucket_summary = " | ".join(format_bucket_summary(queue_rows, interaction_counts))
            st.caption(bucket_summary)

            bucket_choices = bucket_options()
            bucket_labels = [label for _, label in bucket_choices]
            bucket_by_label = {label: key for key, label in bucket_choices}

            filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
            detail_text_filter = filter_col1.text_input("Buscar lead na fila", key="detail_search", placeholder="Empresa, cidade, segmento, e-mail ou telefone")
            selected_bucket_label = filter_col2.selectbox("Bucket", bucket_labels, key="detail_bucket_filter")
            selected_bucket = bucket_by_label.get(selected_bucket_label, "Todos")
            only_new_uncontacted = filter_col3.checkbox(
                "Novos/não contactados",
                value=False,
                key="detail_only_new_uncontacted",
                help="Mostra somente leads em status Novo e sem qualquer contato/interação registrado.",
            )

            filtered_rows = filter_active_rows(
                queue_rows,
                interaction_counts,
                text_filter=detail_text_filter,
                bucket_filter=selected_bucket,
                only_new_uncontacted=only_new_uncontacted,
            )

            st.caption(f"Fila atual: {len(filtered_rows)} lead(s). Use Bucket para navegar por prioridade operacional e aging por etapa.")
'''

OLD_FORMAT_FUNC = '''            def _format_lead_option(current_id: int) -> str:
                current = lead_lookup.get(int(current_id), {})
                score = int(current.get("score") or 0)
                reason = detail_reason_label(current, interaction_counts)
                return f"#{current.get('id', current_id)} | {current.get('empresa', '')} | {current.get('cidade', '')} | Score {score} | {reason}"
'''

NEW_FORMAT_FUNC = '''            def _format_lead_option(current_id: int) -> str:
                current = lead_lookup.get(int(current_id), {})
                return detail_option_label(current)
'''

OLD_ACTION_BLOCK = '''            if lead:
                action, reason = recommend_next_action(lead)
                score_info = score_lead(lead)
                st.info(f"Próxima ação recomendada: **{action}** — {reason}")
'''

NEW_ACTION_BLOCK = '''            if lead:
                action, reason = recommend_next_action(lead)
                score_info = score_lead(lead)
                lead_ui = lead_lookup.get(lead_id, {})
                if lead_ui.get("operational_bucket_label"):
                    st.caption(
                        f"Bucket: {lead_ui.get('operational_bucket_label')} | "
                        f"Aging: {lead_ui.get('aging_days', 0)} dia(s) — {lead_ui.get('aging_label', '')}"
                    )
                st.info(f"Próxima ação recomendada: **{action}** — {reason}")
'''

MARKERS = [
    "detail_bucket_filter",
    "format_bucket_summary",
    "filter_active_rows(",
    "detail_option_label(current)",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"ERRO: bloco esperado não encontrado: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    text = APP.read_text(encoding="utf-8")
    original = text

    if IMPORT_BLOCK not in text:
        if IMPORT_ANCHOR not in text:
            raise SystemExit("ERRO: âncora de import não encontrada")
        text = text.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + IMPORT_BLOCK, 1)

    text = replace_once(text, OLD_FILTER_BLOCK, NEW_FILTER_BLOCK, "filtros da aba Detalhe")
    text = replace_once(text, OLD_FORMAT_FUNC, NEW_FORMAT_FUNC, "formatador do selectbox Detalhe")
    text = replace_once(text, OLD_ACTION_BLOCK, NEW_ACTION_BLOCK, "caption de bucket/aging")

    missing = [marker for marker in MARKERS if marker not in text]
    if missing:
        raise SystemExit(f"ERRO: marcadores esperados ausentes após patch: {missing}")

    backup = APP.with_suffix(".py.bak_detail_queue_ui")
    backup.write_text(original, encoding="utf-8")
    APP.write_text(text, encoding="utf-8")
    print(f"Patch aplicado com sucesso: {APP}")
    print(f"Backup criado: {backup}")


if __name__ == "__main__":
    main()
