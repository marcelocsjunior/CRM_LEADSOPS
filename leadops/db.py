from __future__ import annotations

import shutil
import sqlite3
import unicodedata
from pathlib import Path
from typing import Any, Mapping

from . import __version__
from .messages import DEFAULT_IDENTITY
from .scoring import score_lead
from .utils import lead_key_from_payload, now_iso, today_iso

LEAD_FIELDS = [
    "lead_key",
    "empresa",
    "cidade",
    "segmento",
    "site",
    "email_publico",
    "telefone",
    "whatsapp_status",
    "whatsapp_numero",
    "prioridade",
    "decisor",
    "canal_prioritario",
    "dor_provavel",
    "status",
    "proximo_followup",
    "ultimo_contato",
    "score",
    "observacoes",
    "fonte_contato",
    "confianca_contato",
    "nao_contatar_motivo",
]

STATUS_DEFAULTS = [
    "Novo",
    "Contatado",
    "Respondeu",
    "Reunião",
    "Proposta",
    "Ganhou",
    "Perdido",
    "Não contatar",
]

FINAL_STATUSES = {"Ganhou", "Perdido", "Não contatar"}
PRESERVE_ON_IMPORT = {"status", "ultimo_contato", "proximo_followup", "nao_contatar_motivo"}
LEGACY_STATUS_MAP = {
    "Conversa em andamento": "Respondeu",
    "Reunião agendada": "Reunião",
    "Proposta enviada": "Proposta",
    "Frio": "Perdido",
    "Reuniao": "Reunião",
}


def _norm_status_key(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    text = "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))
    return text.lower()


STATUS_KEY_MAP = {_norm_status_key(status): status for status in STATUS_DEFAULTS}
STATUS_KEY_MAP.update({_norm_status_key(old): new for old, new in LEGACY_STATUS_MAP.items()})


def normalize_status(value: Any) -> str:
    if value is None or str(value).strip() == "":
        return "Novo"
    return STATUS_KEY_MAP.get(_norm_status_key(value), str(value).strip())


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    return {str(r[1]) for r in rows}


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    lead_cols = _column_names(conn, "leads")
    additions = {
        "lead_key": "TEXT DEFAULT ''",
        "fonte_contato": "TEXT DEFAULT ''",
        "confianca_contato": "TEXT DEFAULT ''",
        "nao_contatar_motivo": "TEXT DEFAULT ''",
    }
    for col, ddl in additions.items():
        if col not in lead_cols:
            conn.execute(f"ALTER TABLE leads ADD COLUMN {col} {ddl};")


def add_audit_event(
    conn: sqlite3.Connection,
    lead_id: int | None,
    event_type: str,
    field: str = "",
    old_value: Any = "",
    new_value: Any = "",
    source: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO audit_events (lead_id, ts, event_type, field, old_value, new_value, source)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            lead_id,
            now_iso(),
            event_type,
            field,
            "" if old_value is None else str(old_value),
            "" if new_value is None else str(new_value),
            source,
        ),
    )


def _backfill_lead_keys(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT * FROM leads WHERE lead_key IS NULL OR lead_key='';").fetchall()
    for row in rows:
        payload = dict(row)
        key = lead_key_from_payload(payload)
        if key:
            conn.execute("UPDATE leads SET lead_key=?, updated_at=? WHERE id=?;", (key, now_iso(), row["id"]))


def _migrate_live_data(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT * FROM leads ORDER BY id;").fetchall()
    for row in rows:
        lead = dict(row)
        updates: dict[str, Any] = {}

        normalized_status = normalize_status(lead.get("status"))
        if normalized_status != str(lead.get("status") or ""):
            updates["status"] = normalized_status

        if not lead.get("lead_key"):
            updates["lead_key"] = lead_key_from_payload(lead)

        merged = {**lead, **updates}
        scored = score_lead(merged)
        if int(lead.get("score") or 0) != scored.score:
            updates["score"] = scored.score
        current_priority = str(lead.get("prioridade") or "")
        if current_priority != scored.prioridade:
            updates["prioridade"] = scored.prioridade

        if updates:
            assignments = ", ".join([f"{field}=?" for field in updates])
            values = [updates[field] for field in updates] + [now_iso(), int(lead["id"])]
            conn.execute(f"UPDATE leads SET {assignments}, updated_at=? WHERE id=?;", values)
            if "status" in updates:
                add_audit_event(conn, int(lead["id"]), "pipeline_status_migrated", "status", lead.get("status", ""), updates["status"], f"v{__version__}")
            if "score" in updates or "prioridade" in updates:
                add_audit_event(
                    conn,
                    int(lead["id"]),
                    "score_recalibrated",
                    "score",
                    f"{lead.get('score', '')}|{lead.get('prioridade', '')}",
                    f"{updates.get('score', lead.get('score', ''))}|{updates.get('prioridade', lead.get('prioridade', ''))}",
                    f"v{__version__}",
                )


def init_db(db_path: str | Path) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        conn.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_key TEXT DEFAULT '',
                empresa TEXT NOT NULL,
                cidade TEXT DEFAULT '',
                segmento TEXT DEFAULT '',
                site TEXT DEFAULT '',
                email_publico TEXT DEFAULT '',
                telefone TEXT DEFAULT '',
                whatsapp_status TEXT DEFAULT '',
                whatsapp_numero TEXT DEFAULT '',
                prioridade TEXT DEFAULT '',
                decisor TEXT DEFAULT '',
                canal_prioritario TEXT DEFAULT '',
                dor_provavel TEXT DEFAULT '',
                status TEXT DEFAULT 'Novo',
                proximo_followup TEXT DEFAULT '',
                ultimo_contato TEXT DEFAULT '',
                score INTEGER DEFAULT 0,
                observacoes TEXT DEFAULT '',
                fonte_contato TEXT DEFAULT '',
                confianca_contato TEXT DEFAULT '',
                nao_contatar_motivo TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(empresa, cidade)
            );

            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                ts TEXT NOT NULL,
                canal TEXT DEFAULT '',
                acao TEXT DEFAULT '',
                resumo TEXT DEFAULT '',
                prox_followup TEXT DEFAULT '',
                status_resultante TEXT DEFAULT '',
                FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                ts TEXT NOT NULL,
                event_type TEXT NOT NULL,
                field TEXT DEFAULT '',
                old_value TEXT DEFAULT '',
                new_value TEXT DEFAULT '',
                source TEXT DEFAULT '',
                FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
            CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);
            CREATE INDEX IF NOT EXISTS idx_leads_followup ON leads(proximo_followup);
            CREATE INDEX IF NOT EXISTS idx_interactions_lead_ts ON interactions(lead_id, ts DESC);
            CREATE INDEX IF NOT EXISTS idx_audit_lead_ts ON audit_events(lead_id, ts DESC);
            """
        )
        _add_missing_columns(conn)
        _backfill_lead_keys(conn)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_leads_lead_key ON leads(lead_key) WHERE lead_key <> '';" )
        for key, value in DEFAULT_IDENTITY.items():
            conn.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?);", (key, value))
        _migrate_live_data(conn)


def backup_db(db_path: str | Path, reason: str = "manual") -> Path | None:
    db = Path(db_path)
    if not db.exists():
        return None
    backup_dir = db.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    safe_reason = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in reason).strip("_") or "backup"
    target = backup_dir / f"leadops_{now_iso().replace(':','').replace(' ','_')}_{safe_reason}.db"
    shutil.copy2(db, target)
    return target


def _prepared_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = {field: payload.get(field, "") for field in LEAD_FIELDS}
    if not data.get("empresa"):
        data["empresa"] = str(payload.get("Nome") or payload.get("name") or "").strip()
    data["status"] = normalize_status(data.get("status") or payload.get("status"))
    data["lead_key"] = data.get("lead_key") or lead_key_from_payload(data)
    result = score_lead(data)
    if not data.get("prioridade") or str(data.get("prioridade")).lower() in {"auto", "automática", "automatica"}:
        data["prioridade"] = result.prioridade
    data["score"] = result.score
    return data


def _find_existing(conn: sqlite3.Connection, data: Mapping[str, Any]) -> sqlite3.Row | None:
    key = str(data.get("lead_key") or "")
    if key:
        row = conn.execute("SELECT * FROM leads WHERE lead_key=?;", (key,)).fetchone()
        if row:
            return row
    empresa = str(data.get("empresa") or "").strip()
    cidade = str(data.get("cidade") or "").strip()
    if empresa and cidade:
        return conn.execute("SELECT * FROM leads WHERE empresa=? AND cidade=?;", (empresa, cidade)).fetchone()
    return None


def _merge_existing(existing: Mapping[str, Any], data: Mapping[str, Any], preserve_commercial_state: bool) -> dict[str, Any]:
    merged = dict(existing)
    for field in LEAD_FIELDS:
        incoming = data.get(field, "")
        current = existing.get(field, "")
        if preserve_commercial_state and field in PRESERVE_ON_IMPORT and current:
            continue
        if incoming not in (None, ""):
            merged[field] = incoming
        elif field not in merged:
            merged[field] = ""
    merged["status"] = normalize_status(merged.get("status"))
    result = score_lead(merged)
    merged["score"] = result.score
    if not merged.get("prioridade") or str(merged.get("prioridade")).lower() in {"auto", "automática", "automatica"}:
        merged["prioridade"] = result.prioridade
    return merged


def upsert_lead(db_path: str | Path, payload: Mapping[str, Any], source: str = "manual", preserve_commercial_state: bool = True) -> int:
    data = _prepared_payload(payload)
    timestamp = now_iso()
    fields = LEAD_FIELDS
    init_db(db_path)
    with connect(db_path) as conn:
        existing = _find_existing(conn, data)
        if existing:
            old = dict(existing)
            merged = _merge_existing(old, data, preserve_commercial_state=preserve_commercial_state)
            assignments = ", ".join([f"{f}=?" for f in fields])
            values = [merged.get(f, "") for f in fields] + [timestamp, int(old["id"])]
            conn.execute(f"UPDATE leads SET {assignments}, updated_at=? WHERE id=?;", values)
            for field in fields:
                old_v = old.get(field, "")
                new_v = merged.get(field, "")
                if str(old_v) != str(new_v):
                    add_audit_event(conn, int(old["id"]), "lead_updated", field, old_v, new_v, source)
            return int(old["id"])

        values = [data.get(f, "") for f in fields] + [timestamp, timestamp]
        cur = conn.execute(
            f"INSERT INTO leads ({', '.join(fields)}, created_at, updated_at) VALUES ({', '.join(['?'] * len(fields))}, ?, ?);",
            values,
        )
        lead_id = int(cur.lastrowid)
        add_audit_event(conn, lead_id, "lead_created", source=source)
        return lead_id


def list_leads(db_path: str | Path) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY CASE status "
            "WHEN 'Proposta' THEN 1 WHEN 'Reunião' THEN 2 WHEN 'Respondeu' THEN 3 WHEN 'Contatado' THEN 4 WHEN 'Novo' THEN 5 "
            "WHEN 'Ganhou' THEN 6 WHEN 'Perdido' THEN 7 WHEN 'Não contatar' THEN 8 ELSE 9 END, "
            "score DESC, empresa COLLATE NOCASE ASC;"
        ).fetchall()
        return [dict(r) for r in rows]


def list_interaction_counts(db_path: str | Path) -> dict[int, int]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT lead_id, COUNT(*) AS total FROM interactions GROUP BY lead_id;"
        ).fetchall()
        return {int(r["lead_id"]): int(r["total"]) for r in rows}


def get_lead(db_path: str | Path, lead_id: int) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM leads WHERE id=?;", (lead_id,)).fetchone()
        return dict(row) if row else None


def update_lead(db_path: str | Path, lead_id: int, payload: Mapping[str, Any], source: str = "manual") -> None:
    current = get_lead(db_path, lead_id)
    if not current:
        raise ValueError(f"Lead id={lead_id} não encontrado")
    merged = {**current, **payload}
    merged["status"] = normalize_status(merged.get("status"))
    merged["lead_key"] = merged.get("lead_key") or lead_key_from_payload(merged)
    scored = score_lead(merged)
    merged["score"] = scored.score
    if not merged.get("prioridade") or str(merged.get("prioridade")).lower() in {"auto", "automática", "automatica"}:
        merged["prioridade"] = scored.prioridade
    allowed = [f for f in LEAD_FIELDS if f in merged]
    assignments = ", ".join([f"{f}=?" for f in allowed])
    values = [merged[f] for f in allowed] + [now_iso(), lead_id]
    with connect(db_path) as conn:
        conn.execute(f"UPDATE leads SET {assignments}, updated_at=? WHERE id=?;", values)
        for field in allowed:
            if str(current.get(field, "")) != str(merged.get(field, "")):
                add_audit_event(conn, lead_id, "lead_updated", field, current.get(field, ""), merged.get(field, ""), source)


def add_interaction(
    db_path: str | Path,
    lead_id: int,
    canal: str,
    acao: str,
    resumo: str = "",
    prox_followup: str = "",
    status_resultante: str = "",
) -> None:
    init_db(db_path)
    status_resultante = normalize_status(status_resultante) if status_resultante else ""
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO interactions (lead_id, ts, canal, acao, resumo, prox_followup, status_resultante)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (lead_id, now_iso(), canal, acao, resumo, prox_followup, status_resultante),
        )
        add_audit_event(conn, lead_id, "interaction_added", "acao", "", acao, canal)
    update_payload: dict[str, Any] = {"ultimo_contato": now_iso()}
    if prox_followup:
        update_payload["proximo_followup"] = prox_followup
    if status_resultante:
        update_payload["status"] = status_resultante
    update_lead(db_path, lead_id, update_payload, source="interaction")


def list_interactions(db_path: str | Path, lead_id: int) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM interactions WHERE lead_id=? ORDER BY ts DESC;", (lead_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def list_audit_events(db_path: str | Path, lead_id: int) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM audit_events WHERE lead_id=? ORDER BY ts DESC;", (lead_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def import_rows(db_path: str | Path, rows: list[Mapping[str, Any]], source: str = "csv") -> int:
    init_db(db_path)
    count = 0
    for row in rows:
        if not str(row.get("empresa", "") or row.get("Empresa", "")).strip():
            continue
        upsert_lead(db_path, row, source=source, preserve_commercial_state=True)
        count += 1
    return count


def get_settings(db_path: str | Path) -> dict[str, str]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute("SELECT key, value FROM settings;").fetchall()
        data = {r["key"]: r["value"] for r in rows}
    merged = dict(DEFAULT_IDENTITY)
    merged.update({k: v for k, v in data.items() if v is not None})
    return merged


def update_settings(db_path: str | Path, settings: Mapping[str, Any]) -> None:
    init_db(db_path)
    with connect(db_path) as conn:
        for key, value in settings.items():
            conn.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
                (str(key), "" if value is None else str(value)),
            )


def get_operational_snapshot(db_path: str | Path) -> dict[str, Any]:
    init_db(db_path)
    today = today_iso()
    with connect(db_path) as conn:
        leads_total = int(conn.execute("SELECT COUNT(*) FROM leads;").fetchone()[0])
        interactions_total = int(conn.execute("SELECT COUNT(*) FROM interactions;").fetchone()[0])
        audit_total = int(conn.execute("SELECT COUNT(*) FROM audit_events;").fetchone()[0])
        active_total = int(conn.execute("SELECT COUNT(*) FROM leads WHERE status NOT IN ('Ganhou','Perdido','Não contatar');").fetchone()[0])
        due_total = int(conn.execute("SELECT COUNT(*) FROM leads WHERE status NOT IN ('Ganhou','Perdido','Não contatar') AND proximo_followup <> '' AND proximo_followup <= ?;", (today,)).fetchone()[0])
        new_total = int(conn.execute("SELECT COUNT(*) FROM leads WHERE status='Novo';").fetchone()[0])
        pipeline_rows = conn.execute("SELECT status, COUNT(*) AS total FROM leads GROUP BY status;").fetchall()
        pipeline = {status: 0 for status in STATUS_DEFAULTS}
        for row in pipeline_rows:
            pipeline[str(row['status'])] = int(row['total'])
        last_interaction_ts = conn.execute("SELECT MAX(ts) FROM interactions;").fetchone()[0] or ""
        last_lead_update_ts = conn.execute("SELECT MAX(updated_at) FROM leads;").fetchone()[0] or ""
    return {
        "leads_total": leads_total,
        "interactions_total": interactions_total,
        "audit_total": audit_total,
        "active_total": active_total,
        "due_total": due_total,
        "new_total": new_total,
        "pipeline": pipeline,
        "last_interaction_ts": last_interaction_ts,
        "last_lead_update_ts": last_lead_update_ts,
    }


get_dashboard_snapshot = get_operational_snapshot
