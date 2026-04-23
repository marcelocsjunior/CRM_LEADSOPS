from __future__ import annotations

from datetime import date
from typing import Mapping, Any

from leadops.identity_defaults import DEFAULT_IDENTITY

FINAL_PIPELINE_STATUSES = {"Ganhou", "Perdido", "Não contatar"}
CADENCE_BY_STATUS = {
    "Novo": 2,
    "Contatado": 3,
    "Respondeu": 2,
    "Reunião": 1,
    "Proposta": 3,
}


def _lower(value: Any) -> str:
    return "" if value is None else str(value).lower()


def _parse_iso_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def cadence_days_for_status(status: str | None) -> int:
    return CADENCE_BY_STATUS.get(str(status or "Novo"), 3)


def followup_urgency(lead: Mapping[str, Any], today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    status = str(lead.get("status") or "Novo")
    cadence_days = cadence_days_for_status(status)
    followup_date = _parse_iso_date(lead.get("proximo_followup"))

    info: dict[str, Any] = {
        "status": status,
        "cadence_days": cadence_days,
        "followup_date": followup_date,
        "followup_date_iso": followup_date.isoformat() if followup_date else "",
        "bucket": "none",
        "label": "Sem follow-up",
        "days_overdue": 0,
        "days_until": None,
        "priority_rank": 5,
    }

    if status in FINAL_PIPELINE_STATUSES:
        info.update({"bucket": "final", "label": status, "priority_rank": 9})
        return info

    if not followup_date:
        return info

    delta = (today - followup_date).days
    info["days_until"] = (followup_date - today).days

    if delta >= 5:
        info.update(
            {
                "bucket": "critical_overdue",
                "label": "Muito vencido",
                "days_overdue": delta,
                "priority_rank": 0,
            }
        )
    elif delta >= 1:
        info.update(
            {
                "bucket": "overdue",
                "label": "Vencido",
                "days_overdue": delta,
                "priority_rank": 1,
            }
        )
    elif delta == 0:
        info.update(
            {
                "bucket": "today",
                "label": "Hoje",
                "priority_rank": 2,
            }
        )
    else:
        info.update(
            {
                "bucket": "upcoming",
                "label": "Agendado",
                "priority_rank": 3,
            }
        )

    return info


def classify_profile(lead: Mapping[str, Any]) -> str:
    """Classifica o lead para escolher o texto mais natural.

    Perfis usados pelos templates v2.3.0:
    - saude_imagem: clínicas de imagem, radiologia, diagnóstico, ultrassom.
    - clinica_laboratorio: clínicas/laboratórios gerais.
    - educacao: escolas/instituições de ensino.
    - geral: escritórios, comércio, empresas gerais.
    """
    blob = " ".join(
        _lower(lead.get(k))
        for k in ("empresa", "segmento", "dor_provavel", "observacoes")
    )
    imagem_terms = [
        "centro de imagens",
        "imagem",
        "diagnóstico",
        "diagnostico",
        "radiologia",
        "tomografia",
        "ultrassom",
        "ultrasonografia",
        "ultrassonografia",
        "raio-x",
        "raios x",
        "rx",
    ]
    if any(t in blob for t in imagem_terms):
        return "saude_imagem"

    saude_terms = [
        "laboratório",
        "laboratorio",
        "análises",
        "analises",
        "clínica",
        "clinica",
        "saúde",
        "saude",
        "hospital",
    ]
    if any(t in blob for t in saude_terms):
        return "clinica_laboratorio"

    if any(t in blob for t in ["escola", "colégio", "colegio", "ensino", "educação", "educacao"]):
        return "educacao"
    return "geral"


def identity(settings: Mapping[str, Any] | None = None) -> dict[str, str]:
    out = dict(DEFAULT_IDENTITY)
    if settings:
        for key in out:
            if settings.get(key):
                out[key] = str(settings[key])
    return out


def _first_name(settings: Mapping[str, Any] | None = None) -> str:
    return identity(settings).get("nome", "Marcelo").split()[0]


def signature(settings: Mapping[str, Any] | None = None) -> str:
    """Assinatura textual mantida para configuração/diagnóstico.

    Importante: os templates de e-mail v2.3.0 NÃO incluem assinatura no corpo,
    porque o Roundcube/webmail corporativo já injeta a assinatura HTML oficial.
    """
    ident = identity(settings)
    linhas = [
        ident["nome"],
        f"{ident['cargo']} | {ident['empresa']}",
        "Infraestrutura • Redes • Servidores • Backup • Suporte Técnico",
    ]
    if ident.get("email_remetente"):
        linhas.append(ident["email_remetente"])
    if ident.get("telefone_assinatura"):
        linhas.append(ident["telefone_assinatura"])
    if ident.get("website"):
        linhas.append(ident["website"])
    return "\n".join(linhas)


def signature_html(settings: Mapping[str, Any] | None = None) -> str:
    ident = identity(settings)
    return ident.get("assinatura_html") or ""


def first_contact_message(lead: Mapping[str, Any], settings: Mapping[str, Any] | None = None) -> str:
    profile = classify_profile(lead)
    nome = _first_name(settings)
    empresa = identity(settings).get("empresa", "Biotech TI")

    if profile == "saude_imagem":
        return (
            "Olá, tudo bem?\n\n"
            f"Sou {nome}, da {empresa}. Trabalho com suporte técnico para clínicas de imagem.\n\n"
            "Atuo com computadores, rede, backup, sistemas e também com manutenção preventiva/corretiva em equipamentos como ultrassom.\n\n"
            "Queria me apresentar e saber quem seria a pessoa certa para conversar sobre essa parte aí na clínica."
        )

    if profile == "clinica_laboratorio":
        return (
            "Olá, tudo bem?\n\n"
            f"Sou {nome}, da {empresa}. Trabalho com suporte técnico para clínicas e laboratórios.\n\n"
            "Atuo com computadores, rede, backup, sistemas, servidores, Wi-Fi e suporte para manter a rotina de atendimento funcionando bem.\n\n"
            "Queria me apresentar e saber quem seria a pessoa certa para conversar sobre essa parte aí com vocês."
        )

    if profile == "educacao":
        return (
            "Olá, tudo bem?\n\n"
            f"Sou {nome}, da {empresa}. Trabalho com suporte técnico para empresas e instituições de ensino.\n\n"
            "Atuo com computadores, rede, Wi-Fi, backup, servidores, impressoras e suporte para manter a rotina da escola funcionando bem.\n\n"
            "Queria me apresentar e saber quem seria a pessoa certa para conversar sobre essa parte aí com vocês."
        )

    return (
        "Olá, tudo bem?\n\n"
        f"Sou {nome}, da {empresa}. Trabalho com suporte técnico para empresas aqui da região.\n\n"
        "Atuo com computadores, rede, Wi-Fi, backup, servidores, impressoras e suporte para manter a rotina da empresa funcionando bem.\n\n"
        "Queria me apresentar e saber quem seria a pessoa certa para conversar sobre essa parte aí com vocês."
    )


def followup_message(days: int = 2, settings: Mapping[str, Any] | None = None) -> str:
    if days <= 3:
        return (
            "Oi, tudo bem?\n\n"
            "Só reforçando meu contato. Trabalho com suporte técnico aqui na região e posso ajudar quando aparecer demanda "
            "com TI, rede, computador, backup, servidor, Wi-Fi ou manutenção em equipamentos como ultrassom.\n\n"
            "Fico à disposição."
        )
    return (
        "Oi, tudo bem?\n\n"
        "Vou deixar meu contato por aqui para não ficar insistindo.\n\n"
        "Quando precisarem de apoio com TI, rede, backup, computadores, servidor, Wi-Fi ou manutenção técnica, podem me chamar.\n\n"
        "Obrigado."
    )


def email_subject(lead: Mapping[str, Any]) -> str:
    profile = classify_profile(lead)
    if profile == "saude_imagem":
        return "Apresentação – suporte técnico para clínica de imagem"
    if profile == "clinica_laboratorio":
        return "Apoio técnico em TI para clínica/laboratório"
    if profile == "educacao":
        return "Apoio técnico em TI para escola"
    return "Apoio técnico em TI para empresas"


def email_body(lead: Mapping[str, Any], settings: Mapping[str, Any] | None = None) -> str:
    profile = classify_profile(lead)
    nome = _first_name(settings)
    empresa = identity(settings).get("empresa", "Biotech TI")

    if profile == "saude_imagem":
        return (
            "Olá, tudo bem?\n\n"
            f"Sou {nome}, da {empresa}.\n\n"
            "Trabalho com suporte técnico para clínicas de imagem, envolvendo TI, sistemas e equipamentos.\n\n"
            "Atuo com computadores, rede, backup, servidores, sistemas usados na rotina de exames e manutenção preventiva/corretiva em equipamentos como ultrassom.\n\n"
            "Queria me apresentar e deixar meu contato caso vocês precisem de apoio nessa parte, seja para uma demanda pontual ou suporte recorrente."
        )

    if profile == "clinica_laboratorio":
        return (
            "Olá, tudo bem?\n\n"
            f"Sou {nome}, da {empresa}.\n\n"
            "Trabalho com suporte técnico para clínicas e laboratórios, apoiando a rotina de TI no dia a dia.\n\n"
            "Atuo com computadores, rede, backup, sistemas, servidores, Wi-Fi e suporte para manter o atendimento funcionando bem.\n\n"
            "Queria me apresentar e deixar meu contato caso vocês precisem de apoio nessa parte, seja para uma demanda pontual ou suporte recorrente."
        )

    if profile == "educacao":
        return (
            "Olá, tudo bem?\n\n"
            f"Sou {nome}, da {empresa}.\n\n"
            "Trabalho com suporte técnico para empresas e instituições de ensino, apoiando a rotina de TI no dia a dia.\n\n"
            "Atuo com computadores, rede, Wi-Fi, backup, servidores, impressoras e suporte para manter a escola funcionando bem.\n\n"
            "Queria me apresentar e deixar meu contato caso vocês precisem de apoio nessa parte, seja para uma demanda pontual ou suporte recorrente."
        )

    return (
        "Olá, tudo bem?\n\n"
        f"Sou {nome}, da {empresa}.\n\n"
        "Trabalho com suporte técnico para empresas aqui da região, apoiando a rotina de TI no dia a dia.\n\n"
        "Atuo com computadores, rede, Wi-Fi, backup, servidores, impressoras e suporte para manter a empresa funcionando bem.\n\n"
        "Queria me apresentar e deixar meu contato caso vocês precisem de apoio nessa parte, seja para uma demanda pontual ou suporte recorrente."
    )


def objection_response(kind: str = "ja_tem_ti") -> str:
    responses = {
        "ja_tem_ti": (
            "Perfeito, sem problema.\n\n"
            "Mesmo quando a empresa já tem suporte, às vezes aparece demanda pontual, segunda opinião, backup, rede, Wi-Fi, servidor, VPN, manutenção preventiva/corretiva ou algum projeto específico.\n\n"
            "Posso deixar meu contato para uma necessidade futura?"
        ),
        "mandar_email": (
            "Claro. Me passa o melhor e-mail que eu te envio uma apresentação objetiva.\n\n"
            "Se tiver alguém específico que cuida da parte administrativa ou de TI, posso mandar direto para essa pessoa também."
        ),
        "quanto_custa": (
            "Depende bastante do tamanho do ambiente e do tipo de suporte que vocês precisam.\n\n"
            "Normalmente eu entendo primeiro a estrutura, quantidade de máquinas, sistemas, rede, backup, equipamentos e principais dores. "
            "Depois disso consigo sugerir algo mais adequado, sem pacote genérico."
        ),
        "nao_interesse": (
            "Tudo bem, agradeço o retorno.\n\n"
            "Vou retirar este contato da minha lista comercial. Caso precisem futuramente de apoio com TI, rede, backup, servidores, suporte técnico ou manutenção, fico à disposição."
        ),
        "qual_servico": (
            "Atuo em duas frentes: TI da empresa/clínica e suporte técnico para operação.\n\n"
            "Na parte de TI: rede, computadores, backup, servidor, Wi-Fi, VPN e sistemas.\n\n"
            "Na parte técnica: apoio em sistemas biomédicos e manutenção preventiva/corretiva em equipamentos como ultrassom."
        ),
    }
    return responses.get(kind, responses["ja_tem_ti"])


def call_script(lead: Mapping[str, Any], settings: Mapping[str, Any] | None = None) -> str:
    ident = identity(settings)
    return (
        f"Olá, tudo bem? Meu nome é {_first_name(settings)}, da {ident['empresa']}. "
        "Trabalho com suporte técnico para empresas e clínicas da região. "
        "Gostaria só de me apresentar e saber quem cuida da parte de TI ou manutenção técnica aí com vocês. "
        "Qual seria o melhor e-mail ou WhatsApp para eu mandar uma apresentação rápida?"
    )


def recommend_next_action(lead: Mapping[str, Any]) -> tuple[str, str]:
    status = str(lead.get("status") or "Novo")
    cadence_days = cadence_days_for_status(status)
    ctx = followup_urgency(lead)
    whatsapp_ok = str(lead.get("whatsapp_status") or "").lower() in {"sim", "confirmado"} or bool(lead.get("whatsapp_numero"))
    email_ok = "@" in str(lead.get("email_publico") or "")

    if status == "Não contatar":
        return "Não agir", "Lead marcado como não contatar."
    if status == "Perdido":
        return "Encerrar", "Oportunidade perdida; revisar apenas se houver novo gatilho."
    if status == "Ganhou":
        return "Pós-venda", "Oportunidade convertida; retirar da cadência comercial."

    if ctx["bucket"] == "critical_overdue":
        return (
            "Follow-up crítico",
            f"Follow-up atrasado há {ctx['days_overdue']} dia(s); tratar antes de novos contatos e recuperar a cadência do estágio {status}.",
        )
    if ctx["bucket"] == "overdue":
        return (
            "Executar follow-up vencido",
            f"Follow-up atrasado há {ctx['days_overdue']} dia(s); retomar a cadência antes de abrir novos toques.",
        )
    if ctx["bucket"] == "today":
        return (
            "Executar follow-up hoje",
            f"Follow-up programado para hoje ({ctx['followup_date_iso']}); manter a cadência do estágio {status}.",
        )
    if ctx["bucket"] == "upcoming" and status in {"Contatado", "Respondeu", "Reunião", "Proposta"}:
        return (
            "Aguardar follow-up agendado",
            f"Próximo toque já agendado para {ctx['followup_date_iso']}; cadência mínima sugerida para {status}: D+{cadence_days}.",
        )

    if status == "Novo":
        if whatsapp_ok:
            return "Primeiro contato via WhatsApp", "WhatsApp confirmado/informado e lead ainda está novo."
        if email_ok:
            return "Enviar e-mail de apresentação", "Sem WhatsApp confirmado; e-mail público disponível."
        return "Ligar para validar contato", "Sem canal digital confiável; telefone é o melhor primeiro passo."
    if status == "Contatado":
        return "Programar follow-up D+3", f"Primeiro toque já ocorreu; cadência mínima sugerida para o estágio atual: D+{cadence_days}."
    if status == "Respondeu":
        return "Qualificar demanda", f"Lead respondeu; avançar descoberta e manter retorno em até D+{cadence_days}."
    if status == "Reunião":
        return "Preparar diagnóstico", f"Oportunidade em reunião; vale entrar com roteiro e próximo passo em até D+{cadence_days}."
    if status == "Proposta":
        return "Follow-up de proposta", f"Verificar objeções, janela de decisão e manter cadência mínima em D+{cadence_days}."
    return "Revisar manualmente", "Status fora do funil padrão; revisar o cadastro."
