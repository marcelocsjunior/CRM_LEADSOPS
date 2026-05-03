# LeadOps TI / Mini CRM Biotech

Mini-CRM operacional para prospecção comercial B2B da Biotech TI.

## 🚀 Status Operacional em Produção

**Baseline operacional vigente:** `LeadOps DEV v1.5.5 — Consolidar WhatsApp Priority`

| Atributo | Detalhe |
| :--- | :--- |
| **Ambiente** | VM Ubuntu Server LTS (10.0.0.107) |
| **Diretório Base** | `/opt/leadops` |
| **Banco de Dados** | `/opt/leadops/data/leadops.db` |
| **Porta Produção** | `8501` |
| **Serviço** | `leadops-ti.service` (Systemd) |
| **Backup** | Diário (02:00 AM) com retenção de 7 dias |

---

## 🛠️ Guia Rápido de Implantação (Ubuntu Server)

Para implantar esta ferramenta em um novo servidor Ubuntu Server LTS, siga os blocos de comando abaixo:

### 1. Preparação e Dependências
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip git rsync
sudo adduser --system --no-create-home --group leadops
sudo mkdir -p /opt/leadops && sudo chown leadops:leadops /opt/leadops
```

### 2. Setup do Código e Ambiente Virtual
```bash
sudo -u leadops git clone https://github.com/marcelocsjunior/CRM_LEADSOPS.git /opt/leadops
cd /opt/leadops
sudo -u leadops python3 -m venv .venv
sudo -u leadops .venv/bin/pip install -r requirements.txt
```

### 3. Configuração do Serviço (Systemd)
Crie o arquivo `/etc/systemd/system/leadops-ti.service`:
```ini
[Unit]
Description=LeadOps TI CRM Service
After=network.target

[Service]
User=leadops
Group=leadops
WorkingDirectory=/opt/leadops
Environment="LEADOPS_DB=/opt/leadops/data/leadops.db"
EnvironmentFile=/etc/leadops/leadops-ti.env
ExecStart=/opt/leadops/.venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
```

### 4. Ativação e Firewall
```bash
sudo systemctl daemon-reload
sudo systemctl enable leadops-ti
sudo systemctl start leadops-ti
sudo ufw allow 8501/tcp
```

---

## 🧠 Integração e Roteamento de IA

O LeadOps utiliza uma camada assistiva de IA configurada via variáveis de ambiente.

**Configurações em `/etc/leadops/leadops-ti.env`:**
- `LEADOPS_AI_ENABLED=true`
- `LEADOPS_AI_PROVIDER=gemini` (Roteamento: Gemini, Cloudflare, Local)
- `LEADOPS_AI_MODEL=gemini-2.5-flash-lite`

**Regra de Ouro:**
> IA sugere. Operador revisa. Operador confirma. Sistema registra.

---

## 📂 Estrutura do Repositório

- `leadops/`: Core da aplicação (DB, Scoring, Aging, Queue).
- `docs/`: Documentação técnica detalhada (Arquitetura, IA, Roadmap).
- `deployment/`: Templates de serviço, scripts de backup e guias.
- `app.py`: Ponto de entrada da interface Streamlit.
- `requirements.txt`: Dependências do projeto.

---

## 🛡️ Segurança e Higiene

**Não versionar:**
- Banco SQLite real (`*.db`);
- Arquivos de ambiente com chaves (`.env` ou `.env.local`);
- Logs e diretórios de cache (`.cache/`).

Para detalhes completos sobre a arquitetura, consulte `docs/ARCHITECTURE.md`.
