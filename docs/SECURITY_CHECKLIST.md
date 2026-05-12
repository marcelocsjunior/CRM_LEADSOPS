# Checklist de Segurança — LeadOps TI

## Escopo

Checklist para reduzir risco operacional no uso do LeadOps TI em notebook, VM ou servidor Ubuntu.

## Dados e versionamento

Antes de qualquer commit, confirmar:

- nenhum banco real foi adicionado;
- nenhum CSV real de leads/clientes foi adicionado;
- nenhum arquivo `.env` foi adicionado;
- nenhum token, senha ou chave de API aparece no diff;
- nenhum log operacional foi adicionado;
- nenhum backup foi adicionado.

Comandos úteis:

```bash
git status --short
git diff --cached
```

## Arquivos sensíveis bloqueados

O `.gitignore` deve bloquear, no mínimo:

```text
.env
*.db
*.sqlite
*.sqlite3
*.log
backups/
exports/
secrets/
private/
data/private/
data/raw/
```

## Permissões recomendadas no servidor

```bash
sudo chown -R leadops:leadops /opt/leadops
sudo chmod 750 /opt/leadops
sudo chmod 750 /etc/leadops
sudo chmod 640 /etc/leadops/leadops-ti.env
sudo chown root:leadops /etc/leadops/leadops-ti.env
```

## Exposição de rede

Preferência operacional:

1. uso local;
2. LAN controlada;
3. VPN;
4. túnel autenticado;
5. reverse proxy com autenticação.

Evitar exposição pública direta do Streamlit sem camada adicional de proteção.

## Variáveis de ambiente

Arquivo recomendado:

```text
/etc/leadops/leadops-ti.env
```

Conteúdo mínimo:

```env
LEADOPS_DB=/opt/leadops/data/leadops.db
LEADOPS_AI_ENABLED=false
LEADOPS_AI_PROVIDER=gemini
LEADOPS_AI_MODEL=gemini-2.5-flash-lite
```

Chaves reais devem ser adicionadas apenas no servidor e nunca no Git.

## Backup

- gerar backup antes de atualização;
- manter retenção mínima de 7 dias;
- validar restauração periodicamente;
- proteger diretório de backup contra leitura indevida.

## Operação comercial

- respeitar marcação `Não contatar`;
- registrar motivo quando remover lead da cadência;
- não automatizar envio sem validação humana;
- manter histórico de interação atualizado.

## Revisão antes de produção

- serviço Systemd ativo;
- banco em caminho esperado;
- firewall coerente com o cenário;
- logs sem erro crítico;
- backup testado;
- documentação alinhada com a versão do código.
