# Operação — LeadOps TI

## Objetivo

Este guia organiza execução, manutenção e recuperação operacional do LeadOps TI em ambiente local ou servidor Ubuntu.

## Execução local

```bash
cd CRM_LEADSOPS
source .venv/bin/activate
streamlit run app.py
```

Acesse:

```text
http://localhost:8501
```

## Execução em servidor

Padrão recomendado:

```bash
sudo systemctl status leadops-ti --no-pager
sudo journalctl -u leadops-ti -n 100 --no-pager
```

Reiniciar:

```bash
sudo systemctl restart leadops-ti
```

Parar:

```bash
sudo systemctl stop leadops-ti
```

Subir no boot:

```bash
sudo systemctl enable leadops-ti
```

## Banco de dados

Caminho recomendado:

```text
/opt/leadops/data/leadops.db
```

Antes de manutenção relevante, gere backup:

```bash
sudo -u leadops mkdir -p /opt/leadops/data/backups
sudo -u leadops cp /opt/leadops/data/leadops.db /opt/leadops/data/backups/leadops_manual_$(date +%Y%m%d_%H%M%S).db
```

## Atualização de código em produção

```bash
cd /opt/leadops
sudo systemctl stop leadops-ti
sudo -u leadops git pull --ff-only
sudo -u leadops .venv/bin/pip install -r requirements.txt
sudo systemctl start leadops-ti
sudo systemctl status leadops-ti --no-pager
```

## Verificações pós-atualização

- app abre na porta `8501`;
- banco foi preservado;
- leads aparecem na aba Leads;
- aba Hoje carrega sem erro;
- aba Detalhe permite navegar na fila;
- registro de interação funciona;
- exportação CSV funciona.

## Troubleshooting

### Serviço não sobe

```bash
sudo journalctl -u leadops-ti -n 200 --no-pager
```

Verifique:

- caminho `/opt/leadops`;
- existência da `.venv`;
- permissões do usuário `leadops`;
- arquivo `/etc/leadops/leadops-ti.env`;
- dependências do `requirements.txt`.

### Porta ocupada

```bash
sudo ss -ltnp | grep 8501
```

### Banco sem permissão

```bash
sudo chown -R leadops:leadops /opt/leadops/data
```

### App sem dados

Verifique se `LEADOPS_DB` aponta para o banco correto.

## Rotina mínima semanal

- revisar backups;
- testar abertura do app;
- exportar base CSV quando necessário;
- revisar logs do serviço;
- confirmar espaço em disco.

## Regra operacional

O LeadOps prepara abordagem e registra histórico. O envio de mensagem, e-mail ou ligação continua sendo ação humana fora do sistema.
