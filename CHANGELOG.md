# Changelog

## v1.5.5 — Consolidar WhatsApp Priority

**Data da promoção:** `2026-05-02 00:12:58`

**Status:** promovida para uso operacional

**Evidência:**

```text
PROMOTION_STATUS=OK
VALIDATION_REPORT=/home/biotech/Documentos/LeadOps_TI_RELEASE_BACKUPS/validation/validate_prod_v1_5_5_20260502_001258.log
```

### Objetivo

Consolidar a camada WhatsApp/telefone após três camadas de hotfix, eliminando código residual e transformando a lógica multicanal em base operacional limpa, previsível e testável.

### Melhorias consolidadas

- remoção de sobras dos patches/hotfixes anteriores;
- padronização de uma função canônica de seleção de telefone/WhatsApp;
- prioridade correta para WhatsApp/celular antes de telefone fixo;
- correção de comportamento em que lead com WhatsApp disponível podia cair em telefone fixo;
- saneamento de imports nas páginas;
- cobertura permanente de teste para Cockpit e ações multicanal;
- atualização de documentação/status;
- promoção controlada do DEV IA `8502` para produção `8501`;
- preservação do banco real durante a promoção;
- backup e rollback preparados.

### Política operacional definida

A partir desta release, hotfix improvisado deixa de ser prática aceita. Novas alterações devem entrar como release planejada, com escopo, testes, backup, rollback e documentação.

## v1.5.1 — Ações Multicanal no Cockpit

- Cockpit Comercial Unificado com ações multicanal;
- e-mail sem webmail com assunto/corpo para copiar;
- Gmail/Outlook Web;
- `mailto:`/app local;
- WhatsApp Web/App;
- WhatsApp Android via `whatsapp://send`;
- ligação via `tel:`;
- produção `8501` preservada;
- banco real intocado.

## v1.5.0 — Cockpit Comercial Unificado

- consolidação do fluxo comercial em uma tela orientada a ação;
- redução de cliques e alternância entre páginas;
- foco em abordagem prática diária;
- base para evolução multicanal posterior.

## v1.3 — Operação Comercial IA

- DEV IA `8502` operacional;
- Operação Comercial IA validada;
- Classificação Review OK;
- Relatório Review IA OK;
- pytest geral OK;
- produção `8501` preservada;
- banco real intocado.

## v2.3.3

### Melhorias da aba Detalhe

- aba **Detalhe** evoluída para fila operacional;
- filtro **Novos/não contactados**;
- a fila oculta status finais por padrão;
- ordenação prioriza follow-up vencido, novos sem contato e leads em andamento;
- navegação entre leads com **Anterior** e **Próximo**;
- seletor do lead mostra score e motivo operacional;
- recomendação de próxima ação por lead;
- manutenção do fluxo de e-mail no Android com `mailto:`;
- atualização aplicada sem sobrescrever a base real.

### Critério do filtro `Novos/não contactados`

Um lead entra nesse filtro quando:

- status = `Novo`;
- `ultimo_contato` está vazio;
- não existe interação registrada.

### Objetivo

Transformar a aba Detalhe em fila prática de ataque comercial, reduzindo caça manual de lead e acelerando abordagem no Android.

## v2.3.2

- versão operacional anterior consolidada;
- ambiente estável em Streamlit + SQLite;
- execução padronizada com `.venv` local e `python -m streamlit run app.py`;
- correções de launcher, score e estabilização de uso local.

## Histórico resumido

O projeto nasceu como MVP local de mini-CRM para prospecção B2B da Biotech TI e evoluiu para ferramenta operacional real, com foco em simplicidade, rapidez de uso, IA assistiva, ações multicanal e controle total dos dados.
