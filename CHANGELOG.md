# Changelog

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

O projeto nasceu como MVP local de mini-CRM para prospecção B2B da Biotech e evoluiu para ferramenta operacional real, com foco em simplicidade, rapidez de uso e controle total dos dados.
