# Changelog — LeadOps TI

Todas as mudanças relevantes do projeto devem ser registradas neste arquivo.

## v2.3.3

Base operacional publicada no repositório.

### Consolidado

- interface principal em Streamlit;
- funil comercial padronizado;
- aba Detalhe como fila operacional;
- filtro de novos/não contactados;
- navegação entre leads com Anterior e Próximo;
- ordenação operacional da fila;
- recomendação de próxima ação por lead;
- score comercial com motivos;
- registro de interações;
- auditoria de alterações;
- templates de WhatsApp, e-mail e ligação;
- exportações CSV;
- documentação de arquitetura, operação, segurança e roadmap;
- templates de deploy para Systemd, ambiente e backup.

## v2.3.2

- versão operacional anterior consolidada;
- ambiente estável em Streamlit + SQLite;
- execução padronizada com `.venv` local e `python -m streamlit run app.py`;
- correções de launcher, score e estabilização de uso local.

## Convenção futura

Usar categorias:

- `Added` para novos recursos;
- `Changed` para mudanças funcionais;
- `Fixed` para correções;
- `Security` para hardening e proteção de dados;
- `Docs` para documentação.
