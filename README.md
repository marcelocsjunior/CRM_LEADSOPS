# LeadOps TI / Mini CRM Biotech

Mini-CRM operacional para prospecção comercial B2B da Biotech TI.

## Status operacional

**Versão do código:** `LeadOps TI v2.3.3`

| Atributo | Valor recomendado |
| :--- | :--- |
| **Ambiente alvo** | Ubuntu Server LTS |
| **Diretório base** | `/opt/leadops` |
| **Banco de dados** | `/opt/leadops/data/leadops.db` |
| **Porta padrão** | `8501` |
| **Serviço Systemd** | `leadops-ti.service` |
| **Backup** | Diário, com retenção mínima de 7 dias |

> O repositório deve conter código, documentação e templates operacionais. Dados reais, bancos SQLite, chaves, logs e backups não devem ser versionados.

---

## Visão geral

O LeadOps TI é um CRM local leve para organizar prospecção comercial, priorizar leads, preparar abordagens e registrar histórico de contato.

Principais recursos:

- cadastro/importação de leads;
- deduplicação por chave operacional;
- score e prioridade comercial;
- funil de vendas;
- fila diária de ação;
- geração assistida de mensagens, e-mails e scripts de ligação;
- registro de interações;
- auditoria de alterações;
- exportação CSV;
- operação local ou em rede controlada via Streamlit.

---

## Stack

- Python 3;
- Streamlit;
- Pandas;
- SQLite;
- Systemd para produção em servidor Linux.

Dependências diretas estão em `requirements.txt`.

---

## Instalação rápida em Ubuntu Server

### 1. Dependências do sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip git rsync
```

### 2. Usuário e diretório operacional

```bash
sudo adduser --system --no-create-home --group leadops
sudo mkdir -p /opt/leadops /etc/leadops
sudo chown -R leadops:leadops /opt/leadops
sudo chmod 750 /etc/leadops
```

### 3. Código e ambiente virtual

```bash
sudo -u leadops git clone https://github.com/marcelocsjunior/CRM_LEADSOPS.git /opt/leadops
cd /opt/leadops
sudo -u leadops python3 -m venv .venv
sudo -u leadops .venv/bin/pip install --upgrade pip
sudo -u leadops .venv/bin/pip install -r requirements.txt
```

### 4. Variáveis de ambiente

```bash
sudo cp /opt/leadops/deployment/leadops-ti.env.example /etc/leadops/leadops-ti.env
sudo chmod 640 /etc/leadops/leadops-ti.env
sudo chown root:leadops /etc/leadops/leadops-ti.env
```

Ajuste `/etc/leadops/leadops-ti.env` conforme o ambiente.

### 5. Serviço Systemd

```bash
sudo cp /opt/leadops/deployment/leadops-ti.service /etc/systemd/system/leadops-ti.service
sudo systemctl daemon-reload
sudo systemctl enable leadops-ti
sudo systemctl start leadops-ti
sudo systemctl status leadops-ti --no-pager
```

### 6. Firewall, quando necessário

```bash
sudo ufw allow 8501/tcp
```

Acesso padrão:

```text
http://IP_DO_SERVIDOR:8501
```

---

## Execução local para desenvolvimento

```bash
git clone https://github.com/marcelocsjunior/CRM_LEADSOPS.git
cd CRM_LEADSOPS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Operação diária

Fluxo recomendado:

1. importar ou cadastrar leads;
2. revisar a aba **Hoje**;
3. priorizar follow-ups vencidos;
4. trabalhar a aba **Detalhe**;
5. copiar mensagem/e-mail/script gerado;
6. executar contato manualmente no canal adequado;
7. registrar a interação no CRM;
8. revisar funil e exportações.

O app não dispara WhatsApp ou e-mail automaticamente. Ele prepara o conteúdo e registra a ação depois da confirmação operacional.

---

## IA assistiva

A camada de IA deve ser tratada como apoio operacional, não como decisor automático.

Regra prática:

> IA sugere. Operador revisa. Operador confirma. Sistema registra.

Quando habilitada, a configuração deve ficar fora do Git, em `/etc/leadops/leadops-ti.env`.

Variáveis previstas:

```env
LEADOPS_AI_ENABLED=false
LEADOPS_AI_PROVIDER=gemini
LEADOPS_AI_MODEL=gemini-2.5-flash-lite
```

Chaves e tokens nunca devem ser commitados.

---

## Estrutura do repositório

```text
.
├── app.py
├── leadops/
│   ├── db.py
│   ├── messages.py
│   ├── scoring.py
│   ├── utils.py
│   └── ui/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── OPERATIONS.md
│   ├── ROADMAP.md
│   └── SECURITY_CHECKLIST.md
├── deployment/
│   ├── leadops-ti.env.example
│   ├── leadops-ti.service
│   └── backup-leadops.sh
├── requirements.txt
└── README.md
```

---

## Segurança e higiene

Não versionar:

- `*.db`, `*.sqlite`, `*.sqlite3`;
- `.env`, `.env.local`, arquivos com chaves ou tokens;
- logs;
- backups;
- CSVs de clientes/leads reais;
- dumps ou exports operacionais.

O `.gitignore` já possui bloqueios para esses artefatos, mas a responsabilidade operacional continua sendo revisar antes de cada commit.

---

## Documentação complementar

- `docs/ARCHITECTURE.md`: arquitetura e decisões técnicas;
- `docs/OPERATIONS.md`: operação, manutenção e troubleshooting;
- `docs/SECURITY_CHECKLIST.md`: checklist de segurança;
- `docs/ROADMAP.md`: evolução recomendada;
- `deployment/`: templates prontos para produção.
