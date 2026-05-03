# Arquitetura — LeadOps TI / Mini CRM Biotech

## Visão técnica

O projeto foi desenhado para ser um mini-CRM local, leve e rápido, sem dependência inicial de plataforma externa. A arquitetura prioriza simplicidade operacional, portabilidade e domínio total sobre os dados. Com a evolução para ambiente de servidor, a robustez e a automação foram incorporadas.

## Componentes principais

### Aplicação

- Interface principal em **Streamlit**;
- Foco em operação prática, velocidade de uso e baixa fricção.

### Persistência

- Banco principal em **SQLite**;
- Escolha orientada por simplicidade, portabilidade e manutenção leve.
- Em ambiente de servidor, o banco reside em `/opt/leadops/data/leadops.db`.

### Execução

- Ambiente principal em **`.venv` local**;
- Método confiável de subida: `python -m streamlit run app.py`;
- Porta operacional principal: `8501`.
- Em ambiente de servidor, gerenciado por **Systemd** (`leadops-ti.service`), garantindo auto-restart e inicialização no boot.

### Integração IA

- IA assistiva, configurada via **variáveis de ambiente externas** (ex: `LEADOPS_AI_PROVIDER=gemini`).
- Utiliza um **Roteador de IA** para escolher entre diferentes provedores (Gemini, Cloudflare) com base em critérios como latência e score.
- As configurações de IA são carregadas via `EnvironmentFile` no Systemd, garantindo segurança e flexibilidade.

## Decisões arquiteturais consolidadas

- Evitar dependência do Python global do sistema;
- Preservar a base real durante atualizações;
- Manter backup anterior para rollback rápido;
- Priorizar uso local ou rede interna controlada;
- Manter a solução simples antes de expandir para integrações mais pesadas.
- **Automação:** Gerenciamento do serviço via Systemd para alta disponibilidade.
- **Segurança:** Variáveis de ambiente sensíveis isoladas em arquivo de configuração externo (`/etc/leadops/leadops-ti.env`).
- **Manutenção:** Rotinas de backup automático com retenção.

## Fluxo funcional de alto nível

1. Cadastro/importação de leads;
2. Classificação/priorização por score;
3. Navegação da fila comercial;
4. Registro de interações;
5. Evolução do lead no funil;
6. Geração de apoio à abordagem.

## Evolução recente da UX operacional

A principal evolução recente foi a transformação da aba **Detalhe** em uma fila de ação mais útil para o dia a dia comercial, reduzindo atrito de navegação e melhorando a cadência de abordagem.

## Diretriz de versionamento

O repositório deve refletir o estado operacional real do projeto, evitando drift entre README, versão exibida no app e documentação.

## Diretriz de segurança

Não versionar dados reais, banco operacional, logs, backups locais ou qualquer segredo de operação. Variáveis de ambiente sensíveis (API Keys) devem ser gerenciadas via `EnvironmentFile` no Systemd em ambiente de servidor.
