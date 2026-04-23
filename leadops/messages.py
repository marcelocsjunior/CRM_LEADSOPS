from __future__ import annotations

from typing import Mapping, Any

DEFAULT_IDENTITY = {
    "nome": "Marcelo Corrêa Jr",
    "cargo": "Gerente de Tecnologia",
    "empresa": "Biotech TI",
    "email_remetente": "comercial@biotechti.com.br",
    "telefone_assinatura": "(31) 99841-8157",
    "website": "www.biotechti.com.br",
    "webmail_url": "https://webmail.biotechti.com.br",
    "webmail_tipo": "roundcube_cpanel",
    "assinatura_html": """<div><hr style="margin: 0 0 12px 0; border: 0; border-bottom: 1px solid #000000;" />
<table style="border-collapse: collapse;" border="0" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td style="vertical-align: top; padding: 0 14px 0 0;"><img style="display: block; border: 0; outline: none; text-decoration: none;" src="https://biotechti.com.br/Assets/Email/LOGOsolov2.png" alt="Biotech TI" width="90" /></td>
<td style="font-family: Arial,sans-serif; color: #000000; vertical-align: top;">
<div style="font-size: 16px; font-weight: bold; line-height: 22px; margin: 0;">Marcelo Corr&ecirc;a Jr</div>
<div style="font-size: 12px; font-weight: bold; line-height: 18px; margin: 4px 0 10px 0;">Biotech Tecnologia | Eng. Cl&iacute;nica</div>
<div style="font-size: 12px; line-height: 18px; margin: 0px 0px 4px; text-align: justify;"><a style="color: #000000; text-decoration: underline;" href="mailto:comercial@biotechti.com.br">comercial@biotechti.com.br</a></div>
<div style="font-size: 12px; line-height: 18px; margin: 0 0 4px 0;"><a style="color: #000000; text-decoration: underline;" href="https://wa.me/5531998418157">(31) 99841-8157</a></div>
<div style="font-size: 12px; line-height: 18px; margin: 0;"><a style="color: #000000; text-decoration: underline;" href="https://www.biotechti.com.br/">www.biotechti.com.br</a></div>
</td>
</tr>
</tbody>
</table>
<hr style="margin: 12px 0 0 0; border: 0; border-bottom: 1px solid #000000;" /></div>""",
}


def _lower(value: Any) -> str:
    return "" if value is None else str(value).lower()


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
    whatsapp_ok = str(lead.get("whatsapp_status") or "").lower() in {"sim", "confirmado"} or bool(lead.get("whatsapp_numero"))
    email_ok = "@" in str(lead.get("email_publico") or "")

    if status == "Não contatar":
        return "Não agir", "Lead marcado como não contatar."
    if status == "Perdido":
        return "Encerrar", "Oportunidade perdida; revisar apenas se houver novo gatilho."
    if status == "Ganhou":
        return "Pós-venda", "Oportunidade convertida; retirar da cadência comercial."
    if status == "Novo":
        if whatsapp_ok:
            return "Primeiro contato via WhatsApp", "WhatsApp confirmado/informado e lead ainda está novo."
        if email_ok:
            return "Enviar e-mail de apresentação", "Sem WhatsApp confirmado; e-mail público disponível."
        return "Ligar para validar contato", "Sem canal digital confiável; telefone é o melhor primeiro passo."
    if status == "Contatado":
        return "Follow-up curto", "Primeiro toque já ocorreu; agora é cadência leve e objetiva."
    if status == "Respondeu":
        return "Qualificar demanda", "Lead respondeu; identificar dor real, ambiente e decisor."
    if status == "Reunião":
        return "Preparar diagnóstico", "Oportunidade em reunião; vale entrar com roteiro e descoberta."
    if status == "Proposta":
        return "Follow-up de proposta", "Verificar objeções, janela de decisão e próximo passo."
    return "Revisar manualmente", "Status fora do funil padrão; revisar o cadastro."
