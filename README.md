# LeadOps TI / Mini CRM Biotech

Mini-CRM operacional para prospecção comercial B2B da Biotech TI.

## Status atual

**Baseline operacional vigente:** `LeadOps DEV v1.5.5 — Consolidar WhatsApp Priority`

**Data da promoção:** `2026-05-02 00:12:58`

**Ambiente promovido:** DEV IA `8502` -> Produção `8501`

**Evidência de promoção:** `PROMOTION_STATUS=OK`

**Relatório de validação:** `/home/biotech/Documentos/LeadOps_TI_RELEASE_BACKUPS/validation/validate_prod_v1_5_5_20260502_001258.log`

A release `v1.5.5` consolidou a camada multicanal de WhatsApp/telefone depois de múltiplos hotfixes, eliminando sobras de patches e padronizando a seleção de contato para evitar regressão operacional.

## Estado operacional

- Produção: `/home/biotech/Documentos/LeadOps_TI`
- Porta produção: `8501`
- Banco real: `/home/biotech/Documentos/LeadOps_TI/data/leadops.db`
- DEV IA: `/home/biotech/Documentos/LeadOps_TI_DEV_IA`
- Porta DEV IA: `8502`
- IA assistiva configurada por ENV externo, sem segredos no repositório
- Promoção validada com backup e rollback preparado
- Banco real preservado durante a promoção

## Escopo consolidado na v1.5.5

- remoção de sobras dos hotfixes anteriores;
- função canônica para seleção de telefone/WhatsApp;
- prioridade correta para WhatsApp/celular antes de telefone fixo;
- imports limpos nas páginas;
- cobertura permanente de teste para Cockpit/ações multicanal;
- documentação/status de release atualizados;
- política operacional: sem hotfix improvisado daqui para frente.

## Integração IA

A IA no LeadOps TI é assistiva e controlada.

Ela pode apoiar:

- Classificação IA de Leads;
- Classificação Review;
- Relatório Review IA;
- Modo Ataque IA;
- sugestões de mensagens e abordagem;
- priorização comercial.

Regra operacional:

```text
IA sugere.
Operador revisa.
Operador confirma.
Sistema registra.
```

A IA não envia mensagens, não altera status e não grava decisões definitivas sozinha.

Detalhamento técnico e regras de governança: `docs/AI_INTEGRATION.md`.

## Stack

- Python
- Streamlit
- SQLite
- Pandas
- Pytest
- Integração IA via provider cloud configurado por ENV externo
- `.venv` local
- execução via `python -m streamlit run app.py`
- porta produção `8501`
- porta DEV IA `8502`

## Funil comercial atual

- Novo
- Contatado
- Respondeu
- Reunião
- Proposta
- Ganhou
- Perdido
- Não contatar

## Documentação

- `docs/STATUS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/CHECKLIST_OPERACAO.md`
- `docs/STATUS_TEMPLATE.md`
- `docs/AI_INTEGRATION.md`
- `docs/RELEASE_LEADOPS_v1_5_5_PROMOTION.md`
- `CHANGELOG.md`

## Regras de higiene

Não versionar:

- banco SQLite real;
- CSVs reais de leads;
- `.venv`;
- logs, `*.pid`, `*.out`;
- segredos e credenciais;
- arquivos reais de backup operacional.

## Política pós-promoção

A `v1.5.5` passa a ser o baseline operacional vigente. Novas alterações devem entrar somente como release planejada (`v1.5.6` ou `v1.6.0`), com checklist, teste, backup e rollback. Hotfix solto fica fora do processo.
