# Roadmap — LeadOps TI / Mini CRM Biotech

## Estado atual

A versão operacional atual do código é `v2.3.3`.

A linha atual consolidou:

- aba Detalhe como fila operacional;
- filtro de novos/não contactados;
- recomendação de próxima ação;
- funil comercial padronizado;
- auditoria de alterações;
- templates de abordagem;
- documentação e templates iniciais de deploy.

---

## Prioridade imediata

### 1. Operação comercial disciplinada

- reduzir estoque de leads em **Novo**;
- trabalhar leads **Contatados** com cadência definida;
- avançar leads em **Respondeu** para qualificação;
- registrar toda interação no CRM;
- respeitar status **Não contatar**.

### 2. Endurecimento operacional

- usar serviço Systemd em servidor;
- manter banco real fora do Git;
- executar backup diário;
- testar restauração;
- restringir exposição de rede;
- revisar permissões de `/opt/leadops` e `/etc/leadops`.

### 3. Governança do repositório

- manter README, versão do código e documentação sem drift;
- criar changelog por versão;
- manter templates de deploy atualizados;
- evitar commit de artefatos sensíveis;
- estruturar releases quando houver marco estável.

---

## Próxima camada técnica

### 4. Testes mínimos

Criar testes para:

- scoring;
- normalização de telefone/e-mail/domínio;
- geração de `lead_key`;
- migração inicial do banco;
- preservação de estado comercial em importações.

### 5. Diagnóstico operacional

Adicionar tela ou comando de diagnóstico com:

- caminho do banco atual;
- total de leads;
- total de interações;
- último contato registrado;
- status da configuração de IA;
- versão do app;
- alertas de permissões ou banco ausente.

### 6. Segurança de acesso

Avaliar, conforme cenário:

- VPN;
- túnel autenticado;
- reverse proxy com autenticação;
- binding local quando o uso for apenas no servidor;
- segmentação de rede.

---

## Evoluções futuras do produto

- dashboards adicionais por cidade, segmento e fonte;
- revisão contínua dos pesos de score;
- suporte a importadores mais robustos;
- cadência configurável por perfil de lead;
- exportação segmentada;
- integração assistiva de IA com fallback;
- histórico de objeções;
- indicadores de conversão por canal.

---

## Regra prática

Toda evolução deve preservar:

- simplicidade operacional;
- rollback fácil;
- segurança dos dados;
- baixa fricção de uso;
- aderência ao fluxo comercial real;
- decisão humana antes de ação externa.
