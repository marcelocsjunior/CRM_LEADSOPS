# Checklist operacional — LeadOps TI

## Antes de prospectar

- [ ] Configurar identidade comercial.
- [ ] Confirmar e-mail remetente.
- [ ] Confirmar URL atual do Roundcube após login, contendo `/cpsess.../`, quando aplicável.
- [ ] Confirmar tipo de webmail configurado no app.
- [ ] Validar prévia da assinatura HTML.
- [ ] Carregar seed inicial ou importar CSV.
- [ ] Verificar leads duplicados pela tela Leads.
- [ ] Confirmar o funil padrão: `Novo → Contatado → Respondeu → Reunião → Proposta → Ganhou/Perdido`.

## Teste de webmail

- [ ] Fazer login no webmail antes de clicar nos botões do LeadOps.
- [ ] Copiar a URL atual da caixa de entrada do Roundcube com `/cpsess.../`, quando houver.
- [ ] Colar essa URL em **Config → URL do webmail**.
- [ ] Confirmar que o diagnóstico reconhece sessão válida, quando aplicável.
- [ ] Testar botão **Roundcube pronto**.
- [ ] Se não preencher, testar **Roundcube alternativo**.
- [ ] Se aparecer HTTP 401/token inválido, atualizar a URL atual da sessão Roundcube em Config.
- [ ] Se ainda falhar, usar **Roundcube compose simples** + copiar Para/Assunto/Corpo.
- [ ] Após envio manual, clicar em **Registrar e-mail enviado + D+3**.
- [ ] Confirmar que o lead mudou para `Contatado` e ganhou follow-up.

## Fluxo diário

- [ ] Abrir aba Hoje.
- [ ] Executar follow-ups vencidos primeiro.
- [ ] Atacar no máximo 5–10 leads novos por dia.
- [ ] Registrar cada ação.
- [ ] Definir follow-up.
- [ ] Avançar estágio com disciplina: `Contatado → Respondeu → Reunião → Proposta`.
- [ ] Marcar `Perdido` ou `Não contatar` quando fizer sentido.

## Depois da resposta

- [ ] Mudar status para `Respondeu`.
- [ ] Registrar resumo objetivo.
- [ ] Qualificar dor principal.
- [ ] Agendar conversa quando houver abertura.
- [ ] Quando houver agenda confirmada, mover para `Reunião`.
- [ ] Quando enviar orçamento/proposta, mover para `Proposta`.

## Higiene da base

- [ ] Exportar base periodicamente.
- [ ] Revisar leads frios/parados.
- [ ] Remover ou segregar contatos inadequados.
- [ ] Não insistir após pedido de remoção.
