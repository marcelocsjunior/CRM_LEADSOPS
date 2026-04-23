# STATUS DO PROJETO — LeadOps TI / Mini CRM Biotech

## Visão geral

O LeadOps TI / Mini CRM Biotech nasceu para organizar, priorizar e acelerar a prospecção comercial dos serviços da Biotech, com foco em operação prática, controle de leads, histórico de interações, funil comercial, priorização por score e apoio direto à abordagem por WhatsApp, e-mail e webmail.

## Início do projeto

O projeto começou como um MVP local de mini-CRM voltado para prospecção B2B, especialmente para empresas e instituições com maior aderência aos serviços da Biotech, como clínicas, hospitais, laboratórios, escolas, escritórios e empresas com infraestrutura crítica, dependência de rede, backup, servidores, Wi-Fi, VPN ou suporte técnico especializado.

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

Principais pontos já tratados:

1. drift de versionamento;
2. score inicialmente saturado;
3. refinamento do funil comercial;
4. correção do launcher no Ubuntu com adoção de `.venv` local;
5. melhoria de usabilidade da aba **Detalhe**.

## Decisões técnicas consolidadas

- app principal rodando localmente em Streamlit;
- banco principal em SQLite;
- ambiente principal em `.venv` local;
- método confiável de execução: `python -m streamlit run app.py`;
- operação principal na porta `8501`;
- preservação da base real durante as atualizações;
- backup prévio e rollback simples como padrão de atualização.

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

Último estado consolidado conhecido:

- 42 leads;
- 13 interações;
- 32 em Novo;
- 9 em Contatado;
- 1 em Respondeu.

## Atualização mais recente — v2.3.3

A linha `v2.3.3` teve foco principal em tornar a aba **Detalhe** mais prática para ataque comercial diário.

### Melhorias aplicadas

- fila operacional na aba **Detalhe**;
- checkbox **Novos/não contactados**;
- melhor navegação entre leads;
- ordenação mais inteligente;
- recomendação objetiva de próxima ação;
- manutenção do botão de e-mail para Android;
- preservação total da base real;
- instalação segura com backup e rollback simples.

## Status atual validado

O projeto está ativo, atualizado, validado e operacional no notebook, com a versão **LeadOps TI v2.3.3** em funcionamento.

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
- fila operacional na aba **Detalhe**;
- filtro de novos/não contactados;
- navegação mais prática entre leads.

## Operação atual recomendada

A operação principal deve continuar em cima da instalação já promovida como oficial, com foco em:

- registrar contatos;
- trabalhar os leads em Novo;
- evoluir leads no funil;
- registrar interações;
- acompanhar próximos passos;
- usar a fila da aba **Detalhe** para abordagem diária.
