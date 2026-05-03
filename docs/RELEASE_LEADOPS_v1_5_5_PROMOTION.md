# Release LeadOps DEV v1.5.5 — Consolidar WhatsApp Priority

## Resumo executivo

A release `LeadOps DEV v1.5.5 — Consolidar WhatsApp Priority` foi promovida para uso operacional em `2026-05-02 00:12:58`.

Esta release encerra a fase de hotfixes sobrepostos na camada WhatsApp/telefone e passa a ser o baseline operacional vigente da produção `8501`.

## Evidência de promoção

```text
PROMOTION_STATUS=OK
VALIDATION_REPORT=/home/biotech/Documentos/LeadOps_TI_RELEASE_BACKUPS/validation/validate_prod_v1_5_5_20260502_001258.log
```

## Ambientes envolvidos

### Origem — DEV IA

```text
/home/biotech/Documentos/LeadOps_TI_DEV_IA
porta 8502
banco DEV: /home/biotech/Documentos/LeadOps_TI_DEV_IA/data/leadops_dev.db
```

### Destino — Produção

```text
/home/biotech/Documentos/LeadOps_TI
porta 8501
banco real: /home/biotech/Documentos/LeadOps_TI/data/leadops.db
```

## Diretriz de promoção

A promoção foi tratada como release controlada, não como hotfix.

Critérios adotados:

- backup antes da troca;
- preservação do banco real;
- preservação de `.venv`, segredos, logs e backups locais;
- limpeza de código residual dos hotfixes;
- validação pós-subida;
- rollback preparado;
- registro documental no repositório.

## Escopo funcional consolidado

- uma única lógica canônica para seleção de telefone/WhatsApp;
- prioridade para WhatsApp/celular antes de telefone fixo;
- correção de regressão em botões de WhatsApp;
- consistência entre Cockpit Comercial e Detalhes/Ações;
- imports saneados;
- testes permanentes cobrindo Cockpit e ações multicanal;
- status/README/changelog atualizados.

## Regra de ouro pós-v1.5.5

Hotfix improvisado não deve ser aplicado daqui para frente.

Qualquer nova alteração deve entrar como release planejada, por exemplo:

```text
v1.5.6 — correção pequena planejada
v1.6.0 — evolução funcional maior
```

Toda release futura deve conter:

- objetivo claro;
- escopo fechado;
- teste mínimo;
- backup;
- rollback;
- documentação;
- validação pós-deploy.

## Status final

```text
Baseline operacional vigente: v1.5.5
Produção 8501: OK
Banco real: preservado
Validação: OK
Modo operacional: release controlada
```
