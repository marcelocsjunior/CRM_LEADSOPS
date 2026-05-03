# Guia de Implantação: LeadOps TI em Ubuntu Server LTS

Este documento detalha os passos para implantar e configurar o sistema LeadOps TI em um servidor Ubuntu Server LTS, garantindo sua operação como um serviço do sistema.

## 1. Preparação do Ambiente

### 1.1. Atualização do Sistema e Instalação de Dependências

É fundamental garantir que o sistema operacional esteja atualizado e que as dependências básicas para o Python e o ambiente virtual estejam instaladas.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip git rsync
```

### 1.2. Criação do Usuário Dedicado

Para maior segurança e organização, o serviço do LeadOps TI deve rodar sob um usuário dedicado, não como `root`.

```bash
sudo adduser --system --no-create-home --group leadops
```

### 1.3. Clonagem do Repositório e Ajuste de Permissões

O código-fonte do LeadOps TI será clonado para um diretório específico. Recomenda-se usar `/opt/leadops`.

```bash
sudo mkdir -p /opt/leadops
sudo chown leadops:leadops /opt/leadops
sudo -u leadops git clone https://github.com/marcelocsjunior/CRM_LEADOPS.git /opt/leadops
```

### 1.4. Configuração do Ambiente Virtual Python

O uso de um ambiente virtual isola as dependências do projeto do sistema global, evitando conflitos.

```bash
sudo -u leadops python3 -m venv /opt/leadops/.venv
sudo -u leadops /opt/leadops/.venv/bin/pip install --upgrade pip
sudo -u leadops /opt/leadops/.venv/bin/pip install -r /opt/leadops/requirements.txt
```

### 1.5. Estrutura de Dados e Configuração Inicial

O LeadOps TI utiliza um banco de dados SQLite e armazena dados em `/opt/leadops/data`. É importante inicializar o banco e, opcionalmente, carregar dados de seed.

```bash
sudo mkdir -p /opt/leadops/data
sudo chown leadops:leadops /opt/leadops/data

# Inicializar o banco de dados (cria o arquivo leadops.db se não existir)
sudo -u leadops PYTHONPATH=/opt/leadops /opt/leadops/.venv/bin/python -c "from leadops.db import init_db; init_db(\"/opt/leadops/data/leadops.db\")"

# Opcional: Carregar dados de seed (se houver um arquivo leads_seed.csv no repositório)
# sudo -u leadops PYTHONPATH=/opt/leadops /opt/leadops/.venv/bin/python -c "from leadops.db import init_db, import_rows; from leadops.utils import read_csv_rows; init_db(\"/opt/leadops/data/leadops.db\"); import_rows(\"/opt/leadops/data/leadops.db\", read_csv_rows(\"/opt/leadops/data/leads_seed.csv\"), source=\'seed\')"
```

**Observação:** Se você possui um banco de dados existente (`leadops.db`) do seu ambiente de desenvolvimento, transfira-o para `/opt/leadops/data/` antes de iniciar o serviço. Exemplo de transferência (executar no host de origem):

```bash
rsync -avz /caminho/do/seu/leadops.db USUARIO_VM@IP_DA_VM:/opt/leadops/data/leadops.db
```

## 2. Configuração do Serviço Systemd

Para que o LeadOps TI inicie automaticamente com o servidor e seja gerenciado como um serviço, criaremos uma unidade Systemd.

### 2.1. Criação do Arquivo de Serviço

Crie o arquivo `/etc/systemd/system/leadops-ti.service` com o conteúdo do template `deployment/leadops-ti.service.template` do repositório.

```bash
sudo cp /opt/leadops/deployment/leadops-ti.service.template /etc/systemd/system/leadops-ti.service
```

### 2.2. Configuração de Variáveis de Ambiente para IA (Opcional)

Se você for utilizar a integração com IA, crie o arquivo `/etc/leadops/leadops-ti.env` com suas chaves e configurações. **Substitua `SUA_CHAVE_GEMINI_AQUI` e `SEU_TOKEN_CLOUDFLARE_AQUI` pelos seus valores reais.**

```bash
sudo mkdir -p /etc/leadops
sudo tee /etc/leadops/leadops-ti.env > /dev/null << 'EOF'
GEMINI_API_KEY=SUA_CHAVE_GEMINI_AQUI
CLOUDFLARE_API_TOKEN=SEU_TOKEN_CLOUDFLARE_AQUI
LEADOPS_ENV=prod
LEADOPS_AI_ENABLED=true
LEADOPS_AI_PROVIDER=gemini
LEADOPS_AI_MODEL=gemini-2.5-flash-lite
LEADOPS_AI_TIMEOUT_SECONDS=20
LEADOPS_AI_CACHE_ENABLED=true
LEADOPS_AI_CACHE_TTL_SECONDS=86400
LEADOPS_AI_COOLDOWN_SECONDS=90
LEADOPS_AI_CACHE_DIR=/opt/leadops/.cache/leadops_ai
CLOUDFLARE_ACCOUNT_ID="8ca6a31e0a7fc95695be4cf180cdfc4d"
LEADOPS_CLOUDFLARE_MODEL="@cf/meta/llama-3.1-8b-instruct"
LEADOPS_AI_ROUTER_CHAIN="gemini,cloudflare,local"
LEADOPS_AI_ROUTER_MIN_SCORE="85"
LEADOPS_AI_ROUTER_MAX_LATENCY_MS="10000"
LEADOPS_AI_ROUTER_ALLOW_MARKETING_WARNING="false"
LEADOPS_AI_ROUTER_ACCEPT_LOCAL_ALWAYS="true"
LEADOPS_AI_ROUTER_CLASSIFICATION_LOCAL_FIRST="true"
LEADOPS_AI_ROUTER_CLASSIFICATION_EXTERNAL_ENRICHMENT="true"
LEADOPS_AI_ROUTER_CHOOSE_EXTERNAL_OVER_LOCAL="true"
LEADOPS_AI_ROUTER_MIN_WHATSAPP_CHARS="85"
LEADOPS_AI_ROUTER_REQUIRE_WHATSAPP_CONTEXT="true"
LEADOPS_AI_ROUTER_PROVIDER_COOLDOWN_SECONDS="120"
LEADOPS_AI_ROUTER_QUOTA_COOLDOWN_SECONDS="600"
LEADOPS_AI_TIMEOUT="10"
EOF

sudo chown root:leadops /etc/leadops/leadops-ti.env
sudo chmod 640 /etc/leadops/leadops-ti.env

# Criar diretório de cache para a IA
sudo mkdir -p /opt/leadops/.cache/leadops_ai
sudo chown -R leadops:leadops /opt/leadops/.cache
```

### 2.3. Habilitar e Iniciar o Serviço

Após criar o arquivo de serviço e configurar as variáveis de ambiente, é necessário recarregar o Systemd, habilitar o serviço para iniciar no boot e iniciá-lo.

```bash
sudo systemctl daemon-reload
sudo systemctl enable leadops-ti
sudo systemctl start leadops-ti
```

### 2.4. Verificação do Status do Serviço

Para confirmar que o serviço está rodando corretamente:

```bash
sudo systemctl status leadops-ti
```

Você deve ver `Active: active (running)`.

## 3. Configuração de Firewall (UFW)

Se o firewall UFW estiver ativo, é necessário permitir o tráfego na porta 8501 para acessar a interface web do LeadOps TI.

```bash
sudo ufw allow 8501/tcp
sudo ufw enable
```

## 4. Acesso à Aplicação

Após a conclusão dos passos acima, o LeadOps TI estará acessível via navegador web no endereço `http://<IP_DO_SEU_SERVIDOR>:8501`.

## 5. Script de Manutenção e Rotação de Backups

Para garantir a saúde do banco de dados e gerenciar o espaço em disco, implementaremos um script para realizar backups diários e rotacionar os arquivos antigos.

### 5.1. Criação do Script de Backup e Rotação

Crie o arquivo `/opt/leadops/scripts/backup_rotate.sh` com o conteúdo do template `deployment/backup_rotate.sh.template` do repositório.

```bash
sudo mkdir -p /opt/leadops/scripts /opt/leadops/logs
sudo chown leadops:leadops /opt/leadops/scripts /opt/leadops/logs
sudo cp /opt/leadops/deployment/backup_rotate.sh.template /opt/leadops/scripts/backup_rotate.sh
```

### 5.2. Tornar o Script Executável

```bash
sudo chmod +x /opt/leadops/scripts/backup_rotate.sh
```

### 5.3. Agendamento com Cron

Para executar o script diariamente, adicione uma entrada no crontab do usuário `leadops`.

```bash
(sudo -u leadops crontab -l 2>/dev/null; echo "0 2 * * * /opt/leadops/scripts/backup_rotate.sh >> /opt/leadops/logs/backup.log 2>&1") | sudo -u leadops crontab -
```

## 6. Rollback

Em caso de problemas após uma atualização ou alteração, você pode reverter para um backup anterior do banco de dados e reiniciar o serviço.

```bash
sudo systemctl stop leadops-ti
sudo cp /opt/leadops/data/backups/leadops_backup_YYYYMMDD_HHMMSS.db /opt/leadops/data/leadops.db
sudo systemctl start leadops-ti
```

Substitua `YYYYMMDD_HHMMSS` pelo timestamp do backup desejado.
