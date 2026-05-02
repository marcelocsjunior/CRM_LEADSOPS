# Integração IA — LeadOps TI / Mini CRM Biotech

## Objetivo

A camada de IA do LeadOps TI existe para acelerar a operação comercial B2B da Biotech TI, apoiando priorização, classificação, revisão e geração assistida de abordagem.

A IA é assistiva. Ela não substitui decisão humana, não envia mensagens automaticamente e não altera status comercial sem ação manual.

## Status operacional

```text
Baseline operacional vigente: LeadOps DEV v1.5.5 — Consolidar WhatsApp Priority
Produção: 8501
DEV IA: 8502
Banco real: preservado
IA: assistiva e controlada
```

## Ambientes

### Produção

```text
Caminho: /home/biotech/Documentos/LeadOps_TI
Porta: 8501
Banco: /home/biotech/Documentos/LeadOps_TI/data/leadops.db
Serviço: leadops-ti.service
```

### DEV IA

```text
Caminho: /home/biotech/Documentos/LeadOps_TI_DEV_IA
Porta: 8502
Banco DEV: /home/biotech/Documentos/LeadOps_TI_DEV_IA/data/leadops_dev.db
ENV IA: /home/biotech/.config/leadops-ti/leadops-dev-ai.env
```

## Provider IA

A integração IA foi validada no ambiente DEV IA usando provider cloud configurado por arquivo externo de ambiente.

Provider consolidado no DEV IA:

```text
LEADOPS_AI_ENABLED=true
LEADOPS_AI_PROVIDER=gemini
Modelo validado: gemini-2.5-flash-lite
```

A configuração sensível deve permanecer fora do repositório.

Não versionar:

- API keys;
- tokens;
- arquivos `.env` reais;
- dumps do banco;
- CSVs reais com leads;
- logs com dados sensíveis.

## Capacidades IA integradas

### 1. Classificação IA de Leads

Apoia a análise dos leads e sugere classificação/prioridade com base em dados disponíveis.

Objetivo:

- reduzir triagem manual;
- destacar leads com maior aderência comercial;
- apoiar decisão de abordagem.

### 2. Classificação Review

A IA gera sugestão, mas a gravação passa por revisão manual.

Regra operacional:

```text
IA sugere.
Operador revisa.
Operador confirma.
Sistema registra.
```

### 3. Relatório Review IA

Gera visão consolidada das revisões feitas, apoiando melhoria do processo comercial e análise de qualidade.

### 4. Modo Ataque IA

Apoia operação comercial diária priorizando leads mais promissores e sugerindo próximos passos.

### 5. Mensagens assistidas

A IA pode apoiar geração ou ajuste de mensagens para WhatsApp/e-mail, respeitando o histórico disponível.

## Regras de segurança e governança

### O que a IA pode fazer

- sugerir classificação;
- sugerir prioridade;
- sugerir texto de abordagem;
- resumir contexto do lead;
- apoiar revisão operacional;
- ajudar a organizar fila comercial.

### O que a IA não pode fazer sozinha

- enviar mensagem;
- alterar status comercial;
- gravar decisão definitiva sem revisão;
- inventar contato anterior;
- assumir que houve conversa prévia sem histórico textual;
- dizer "conforme falamos" sem evidência;
- sobrescrever banco real sem ação explícita do operador;
- decidir descarte definitivo de lead sem validação humana.

## Fallback e estabilidade

A ferramenta deve continuar operável mesmo se a IA falhar.

Diretrizes:

- erro bruto de API não deve aparecer para o usuário final;
- deve existir fallback local/determinístico quando aplicável;
- falha de IA não pode bloquear operação básica do CRM;
- quota, timeout e indisponibilidade devem ser tratados de forma limpa;
- logs não devem expor segredos.

## Relação com a v1.5.5

A release `v1.5.5 — Consolidar WhatsApp Priority` não é uma release de novo modelo IA. Ela consolida a camada operacional multicanal para que as ações assistidas por IA usem contatos corretos e consistentes.

Ponto crítico corrigido/consolidado:

```text
Quando existir WhatsApp/celular válido, o sistema não deve preferir telefone fixo para ação WhatsApp.
```

Isso impacta diretamente a operação com IA porque sugestões e ações comerciais precisam acionar o canal correto.

## Critério operacional

A IA deve ser tratada como copiloto comercial controlado:

```text
Acelera triagem.
Apoia abordagem.
Sugere prioridade.
Não decide sozinha.
Não envia sozinha.
Não grava sozinha.
```

## Política futura

Novas evoluções de IA devem entrar somente por release planejada, com:

- escopo fechado;
- teste;
- fallback;
- proteção de dados;
- documentação;
- backup;
- rollback;
- validação em DEV antes de promoção.
