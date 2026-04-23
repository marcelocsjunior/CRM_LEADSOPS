from __future__ import annotations

import csv
import re
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping, Any
from urllib.parse import quote, urlencode, urlparse, urlunparse


def normalize_text(value: Any) -> str:
    """Normaliza texto para comparação/deduplicação."""
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def site_domain(site: str | None) -> str:
    if not site:
        return ""
    raw = str(site).strip()
    if not raw:
        return ""
    if not re.match(r"^https?://", raw, re.I):
        raw = "https://" + raw
    parsed = urlparse(raw)
    host = (parsed.netloc or parsed.path).lower().strip()
    host = host.split("/")[0].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def email_domain(email: str | None) -> str:
    first = first_email(email)
    if "@" not in first:
        return ""
    return first.split("@", 1)[1].lower().strip()


def first_email(email: str | None) -> str:
    if not email:
        return ""
    match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", str(email), flags=re.I)
    return match.group(0).strip() if match else ""


def normalize_phone(phone: str | None) -> str:
    """Retorna apenas dígitos com DDI 55. Aceita múltiplos números e usa o primeiro."""
    if not phone:
        return ""
    candidates = re.findall(r"(?:\+?55\s*)?\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}", str(phone))
    raw = candidates[0] if candidates else str(phone)
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("55") and len(digits) in {12, 13}:
        return digits
    if len(digits) in {10, 11}:
        return "55" + digits
    return digits


def pretty_phone(phone: str | None) -> str:
    digits = normalize_phone(phone)
    if digits.startswith("55"):
        digits = digits[2:]
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return str(phone or "")


def whatsapp_link(phone: str | None, message: str = "") -> str:
    digits = normalize_phone(phone)
    if not digits:
        return ""
    base = f"https://wa.me/{digits}"
    if message:
        return f"{base}?text={quote(message)}"
    return base


def gmail_compose_link(to: str, subject: str, body: str) -> str:
    return (
        "https://mail.google.com/mail/?view=cm&fs=1"
        f"&to={quote(to or '')}"
        f"&su={quote(subject or '')}"
        f"&body={quote(body or '')}"
    )


def outlook_compose_link(to: str, subject: str, body: str) -> str:
    return (
        "https://outlook.office.com/mail/deeplink/compose"
        f"?to={quote(to or '')}"
        f"&subject={quote(subject or '')}"
        f"&body={quote(body or '')}"
    )


def mailto_link(to: str, subject: str, body: str) -> str:
    return f"mailto:{quote(to or '')}?subject={quote(subject or '')}&body={quote(body or '')}"



def _normalize_url(raw: str | None, default: str = "https://webmail.biotechti.com.br") -> str:
    value = (raw or default).strip() or default
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    return value


def has_cpanel_session_token(webmail_url: str | None) -> bool:
    """Detecta se a URL atual contém /cpsessNNN/.

    cPanel exige esse token para abrir páginas internas como o Roundcube.
    Sem ele, a tela típica é HTTP 401 / token de segurança inválido.
    """
    raw = _normalize_url(webmail_url)
    return bool(re.search(r"/cpsess\d+(/|$)", urlparse(raw).path or ""))


def sanitize_roundcube_base_url(webmail_url: str | None) -> str:
    """Retorna uma URL base sem cpsess apenas para login/exibição segura.

    Importante: essa URL sem cpsess NÃO deve ser usada para abrir compose interno
    no cPanel, porque o cPanel bloqueia com 401. Para compose, use
    roundcube_session_base_url(), que preserva o cpsess quando informado.
    """
    raw = _normalize_url(webmail_url)
    parsed = urlparse(raw)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path.split("/", 1)[0]
    path = parsed.path or "/"

    path = re.sub(r"/cpsess\d+/?", "/", path)

    if "3rdparty/roundcube" in path:
        base_path = re.sub(r"(.*?/3rdparty/roundcube/).*", r"\1", path)
    elif "webmaillogout.cgi" in path or "login" in path.lower():
        base_path = "/"
    else:
        base_path = "/"

    if not base_path.startswith("/"):
        base_path = "/" + base_path
    return urlunparse((scheme, netloc, base_path, "", "", ""))


def roundcube_session_base_url(webmail_url: str | None) -> str:
    """Retorna base do Roundcube preservando /cpsessNNN/ quando existir.

    Esse é o modo correto para cPanel/Roundcube: o token de sessão fica no path,
    por exemplo /cpsess123/3rdparty/roundcube/. O token expira; quando expirar,
    cole novamente no app a URL atual do Roundcube após login.
    """
    raw = _normalize_url(webmail_url)
    parsed = urlparse(raw)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path.split("/", 1)[0]
    path = parsed.path or "/"

    m = re.search(r"(/cpsess\d+/)", path)
    if m:
        cpsess = m.group(1)
        if "3rdparty/roundcube" in path:
            base_path = re.sub(r"(.*?/3rdparty/roundcube/).*", r"\1", path)
        else:
            base_path = cpsess + "3rdparty/roundcube/"
    else:
        # Sem cpsess, não há token válido para compose interno. Mantém base limpa
        # apenas como fallback; o app também deve oferecer copiar/colar.
        if "3rdparty/roundcube" in path:
            base_path = re.sub(r"(.*?/3rdparty/roundcube/).*", r"\1", path)
        else:
            base_path = "/3rdparty/roundcube/"

    if not base_path.startswith("/"):
        base_path = "/" + base_path
    return urlunparse((scheme, netloc, base_path, "", "", ""))


def roundcube_compose_link(webmail_url: str | None, to: str, subject: str, body: str, variant: str = "underscore") -> str:
    """Gera link assistido para compose do Roundcube/cPanel. Não envia e-mail.

    Para cPanel, preserva /cpsessNNN/ se a URL atual da sessão for informada.
    Sem cpsess, o cPanel tende a responder HTTP 401.
    """
    base = roundcube_session_base_url(webmail_url)
    if variant == "plain":
        params = {"_task": "mail", "_action": "compose", "to": to or "", "subject": subject or "", "body": body or ""}
    else:
        params = {"_task": "mail", "_action": "compose", "_to": to or "", "_subject": subject or "", "_body": body or ""}
    return base + "?" + urlencode(params)


def roundcube_simple_compose_link(webmail_url: str | None) -> str:
    base = roundcube_session_base_url(webmail_url)
    return base + "?_task=mail&_action=compose"

def lead_key_from_payload(payload: Mapping[str, Any]) -> str:
    empresa = normalize_text(payload.get("empresa"))
    cidade = normalize_text(payload.get("cidade"))
    domain = site_domain(payload.get("site")) or email_domain(payload.get("email_publico"))
    domain_key = normalize_text(domain)
    phone_key = normalize_phone(str(payload.get("whatsapp_numero") or payload.get("telefone") or ""))[-8:]

    parts = [empresa, cidade]
    if domain_key:
        parts.append(domain_key)
    elif phone_key:
        parts.append(phone_key)
    return "|".join(p for p in parts if p)


def today_iso() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def add_days_iso(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: str | Path, rows: Iterable[Mapping[str, Any]], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
