from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Mapping, Any

CITY_PRIORITY = {
    "formiga": 10,
    "arcos": 8,
    "piumhi": 6,
    "lagoa da prata": 6,
    "pains": 5,
    "bambui": 5,
    "bambuí": 5,
    "divinopolis": 4,
    "divinópolis": 4,
    "campo belo": 4,
    "oliveira": 4,
    "itapecerica": 4,
    "corrego fundo": 4,
    "córrego fundo": 4,
    "santo antonio do monte": 4,
    "santo antônio do monte": 4,
    "capitolio": 3,
    "capitólio": 3,
}

SEGMENT_WEIGHTS = {
    "hospital": 26,
    "centro de imagens": 26,
    "diagnóstico por imagem": 25,
    "diagnostico por imagem": 25,
    "radiologia": 22,
    "tomografia": 22,
    "laboratório": 21,
    "laboratorio": 21,
    "clínica": 16,
    "clinica": 16,
    "escola": 11,
    "colégio": 11,
    "colegio": 11,
    "contabilidade": 10,
    "advocacia": 9,
    "indústria": 10,
    "industria": 10,
    "supermercado": 8,
}

FINAL_STATUSES = {"Perdido", "Ganhou", "Não contatar"}


SIGNAL_GROUPS = {
    "escala": {
        "weight": 9,
        "patterns": ["múltiplas unidades", "multiplas unidades", "multiunidade", "duas unidades", "filial", "filiais", "expansão", "expansao"],
    },
    "criticidade": {
        "weight": 8,
        "patterns": ["ambiente crítico", "ambiente critico", "continuidade operacional", "contingência", "contingencia", "suporte rápido", "suporte rapido", "prevenção de parada", "prevencao de parada", "parada"],
    },
    "operação digital": {
        "weight": 6,
        "patterns": ["resultado", "resultados", "exames", "agendamento", "portal", "atendimento digital", "consultório virtual", "consultorio virtual"],
    },
}

INFRA_SIGNALS = {
    "backup": 2,
    "vpn": 2,
    "servidor": 2,
    "wi-fi": 2,
    "wifi": 2,
    "rede": 2,
    "suporte": 2,
    "padronização": 2,
    "padronizacao": 2,
    "contingência": 2,
    "contingencia": 2,
}
INFRA_CAP = 8

STATUS_WEIGHTS = {
    "Novo": 0,
    "Contatado": 6,
    "Respondeu": 12,
    "Reunião": 18,
    "Proposta": 16,
    "Ganhou": -25,
    "Perdido": -60,
    "Não contatar": -80,
}


@dataclass(frozen=True)
class ScoreResult:
    score: int
    prioridade: str
    motivos: list[str] = field(default_factory=list)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _blob(lead: Mapping[str, Any]) -> str:
    return " ".join(
        _text(lead.get(k)).lower()
        for k in (
            "empresa",
            "cidade",
            "segmento",
            "site",
            "dor_provavel",
            "observacoes",
            "canal_prioritario",
            "decisor",
            "fonte_contato",
        )
    )


def _ascii(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch)).lower()


def _contains(blob: str, pattern: str) -> bool:
    return _ascii(pattern) in _ascii(blob)


def priority_from_score(score: int) -> str:
    if score >= 70:
        return "Alta"
    if score >= 55:
        return "Média/Alta"
    if score >= 40:
        return "Média"
    return "Baixa"


def calculate_score_with_reasons(lead: Mapping[str, Any]) -> tuple[int, list[str]]:
    blob = _blob(lead)
    score = 0
    reasons: list[str] = []

    for segment, weight in SEGMENT_WEIGHTS.items():
        if _contains(blob, segment):
            score += weight
            reasons.append(f"+{weight} aderência de segmento: {segment}")
            break

    for city, weight in CITY_PRIORITY.items():
        if _contains(_text(lead.get("cidade")), city):
            score += weight
            reasons.append(f"+{weight} praça prioritária: {city}")
            break

    for label, cfg in SIGNAL_GROUPS.items():
        if any(_contains(blob, pattern) for pattern in cfg["patterns"]):
            score += int(cfg["weight"])
            reasons.append(f"+{cfg['weight']} sinal comercial: {label}")

    infra_points = 0
    matched_infra: list[str] = []
    for signal, weight in INFRA_SIGNALS.items():
        if _contains(blob, signal):
            infra_points += weight
            matched_infra.append(signal)
    if infra_points:
        awarded = min(INFRA_CAP, infra_points)
        score += awarded
        reasons.append(f"+{awarded} dor técnica identificada: {', '.join(sorted(set(matched_infra))[:4])}")

    whatsapp_status = _text(lead.get("whatsapp_status")).lower()
    whatsapp_number = _text(lead.get("whatsapp_numero"))
    if whatsapp_status in {"sim", "confirmado", "confirmado publicamente"} or whatsapp_number:
        score += 10
        reasons.append("+10 WhatsApp confirmado/informado")
    elif whatsapp_status in {"provável", "provavel"}:
        score += 4
        reasons.append("+4 WhatsApp provável")

    email = _text(lead.get("email_publico"))
    if "@" in email:
        score += 5
        reasons.append("+5 e-mail público disponível")

    telefone = _text(lead.get("telefone"))
    if re.search(r"\d", telefone):
        score += 3
        reasons.append("+3 telefone público disponível")

    decisor = _text(lead.get("decisor"))
    if decisor:
        score += 3
        reasons.append("+3 decisor provável mapeado")

    confianca = _text(lead.get("confianca_contato")).lower()
    if confianca == "alta":
        score += 6
        reasons.append("+6 contato com alta confiança")
    elif confianca == "média" or confianca == "media":
        score += 3
        reasons.append("+3 contato com confiança média")
    elif confianca == "inferida":
        score += 1
        reasons.append("+1 contato inferido")

    fonte = _text(lead.get("fonte_contato"))
    if fonte:
        score += 2
        reasons.append("+2 fonte de contato registrada")

    status = _text(lead.get("status")) or "Novo"
    status_weight = STATUS_WEIGHTS.get(status, 0)
    if status_weight:
        sign = "+" if status_weight > 0 else ""
        score += status_weight
        reasons.append(f"{sign}{status_weight} estágio do funil: {status}")

    if not whatsapp_number and "@" not in email and not re.search(r"\d", telefone):
        score -= 15
        reasons.append("-15 sem canal claro de contato")

    score = max(0, min(100, score))
    return score, reasons


def calculate_score(lead: Mapping[str, Any]) -> int:
    score, _ = calculate_score_with_reasons(lead)
    return score


def score_lead(lead: Mapping[str, Any]) -> ScoreResult:
    score, reasons = calculate_score_with_reasons(lead)
    return ScoreResult(score=score, prioridade=priority_from_score(score), motivos=reasons)
