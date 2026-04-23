# LeadOps TI / Mini CRM Biotech

Mini-CRM operacional para prospecção comercial B2B da Biotech.

## Status atual

**Versão operacional validada:** `v2.3.3`

A linha v2.3.3 consolidou a aba **Detalhe** como fila operacional, com filtro de **Novos/não contactados**, navegação entre leads e recomendação de próxima ação.

## Stack

- Streamlit
- SQLite
- `.venv` local
- execução via `python -m streamlit run app.py`
- porta `8501`

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
- `CHANGELOG.md`

## Regras de higiene

Não versionar:

- banco SQLite real;
- CSVs reais de leads;
- `.venv`;
- logs, `*.pid`, `*.out`;
- segredos e credenciais.
