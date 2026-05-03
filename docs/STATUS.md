# STATUS DO PROJETO — LeadOps TI / Mini CRM Biotech

## Visão geral

O LeadOps TI / Mini CRM Biotech nasceu para organizar, priorizar e acelerar a prospecção comercial dos serviços da Biotech TI, com foco em operação prática, controle de leads, histórico de interações, funil comercial, priorização por score e apoio direto à abordagem por WhatsApp, e-mail e webmail.

## Início do projeto

O projeto começou como um MVP local de mini-CRM voltado para prospecção B2B, especialmente para empresas e instituições com maior aderência aos serviços da Biotech TI, como clínicas, hospitais, laboratórios, escolas, escritórios, indústrias locais e empresas com infraestrutura crítica, dependência de rede, backup, servidores, Wi-Fi, VPN ou suporte técnico especializado.

A base inicial foi montada com:

- app local em Streamlit;
- persistência em SQLite;
- importação de leads por CSV;
- score de priorização;
- geração assistida de mensagens;
- histórico de interações;
- funil comercial básico;
- apoio a ações por WhatsApp, Gmail, Outlook e webmail.

## Evolução consolidada

Principais frentes já tratadas:

1. correção de drift de versionamento;
2. ajuste de score inicialmente saturado;
3. refinamento do funil comercial;
4. correção do launcher no Ubuntu com adoção de `.venv` local;
5. melhoria de usabilidade da aba **Detalhe**;
6. criação do ambiente DEV IA na porta `8502`;
7. integração IA com Gemini API em ambiente DEV;
8. criação de Classificação IA, Review IA e relatórios de revisão;
9. consolidação do Cockpit Comercial;
10. saneamento da camada multicanal WhatsApp/e-mail/webmail;
11. consolidação definitiva da prioridade WhatsApp/telefone na release `v1.5.5`.

## Decisões técnicas consolidadas

- app principal rodando localmente em Streamlit;
- banco principal em SQLite;
- ambiente principal em `.venv` local;
- método confiável de execução: `python -m streamlit run app.py`;
- produção na porta `8501`;
- DEV IA na porta `8502`;
- preservação da base real durante atualizações;
- backup prévio e rollback simples como padrão de atualização;
- IA não grava, não envia e não altera status sozinha;
- gravações sensíveis passam por revisão/manualidade;
- hotfix improvisado não é mais aceito após a promoção da `v1.5.5`.

## Ambientes

### Produção

- Caminho: `/home/biotech/Documentos/LeadOps_TI`
- Banco real: `/home/biotech/Documentos/LeadOps_TI/data/leadops.db`
- Porta: `8501`
- Serviço: `leadops-ti.service`

### DEV IA

- Caminho: `/home/biotech/Documentos/LeadOps_TI_DEV_IA`
- Banco DEV: `/home/biotech/Documentos/LeadOps_TI_DEV_IA/data/leadops_dev.db`
- Porta: `8502`
- ENV IA: `/home/biotech/.config/leadops-ti/leadops-dev-ai.env`

## Funil comercial atual

- Novo
- Contatado
- Respondeu
- Reunião
- Proposta
- Ganhou
- Perdido
- Não contatar

## Situação conhecida da base

Último estado consolidado conhecido em DEV IA antes da promoção:

- 42 leads;
- operação comercial assistida validada;
- Classificação IA operacional;
- Review IA operacional;
- Relatório Review IA operacional;
- Cockpit Comercial Unificado operacional;
- ações multicanal validadas.

## Atualização mais recente — v1.5.5

A release `LeadOps DEV v1.5.5 — Consolidar WhatsApp Priority` foi promovida para uso operacional em `2026-05-02 00:12:58`.

### Evidência de promoção

```text
PROMOTION_STATUS=OK
VALIDATION_REPORT=/home/biotech/Documentos/LeadOps_TI_RELEASE_BACKUPS/validation/validate_prod_v1_5_5_20260502_001258.log
```

### Escopo da v1.5.5

- remoção de sobras dos hotfixes anteriores;
- manutenção de uma única lógica canônica de seleção de telefone;
- prioridade correta para WhatsApp/celular antes de telefone fixo;
- garantia de imports limpos nas páginas;
- teste permanente cobrindo Cockpit e ações multicanal;
- atualização de README/status da release;
- promoção controlada DEV IA `8502` -> Produção `8501`;
- banco real preservado durante a promoção;
- rollback preparado.

## Status atual validado

O projeto está ativo, promovido, validado e operacional na produção `8501`, com a versão **LeadOps DEV v1.5.5 — Consolidar WhatsApp Priority** como baseline operacional vigente.

## Estado funcional atual

Atualmente o projeto já entrega:

- cadastro e visualização de leads;
- score de priorização calibrado;
- funil comercial padronizado;
- histórico de interações;
- recomendações de próxima ação;
- mensagens assistidas para abordagem;
- apoio para WhatsApp e e-mail;
- exportação;
- operação local estável;
- fila operacional;
- filtro de novos/não contactados;
- Cockpit Comercial Unificado;
- ações multicanal;
- seleção prioritária de WhatsApp/celular;
- Review IA;
- Classificação IA;
- relatório de revisão IA.

## Operação atual recomendada

A operação principal deve continuar em cima da instalação promovida como oficial, com foco em:

- registrar contatos;
- trabalhar os leads em Novo;
- evoluir leads no funil;
- registrar interações;
- acompanhar próximos passos;
- usar Cockpit/Detalhes para abordagem diária;
- observar gargalos reais antes de planejar nova release.

## Política daqui para frente

A `v1.5.5` encerra a fase de hotfixes sobrepostos. Qualquer alteração nova deve ser tratada como release planejada, com:

- objetivo claro;
- escopo fechado;
- testes;
- backup;
- rollback;
- documentação;
- promoção controlada.
