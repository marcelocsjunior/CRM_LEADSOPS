# CRM_LEADSOPS

STATUS DO PROJETO — LeadOps TI / Mini CRM Biotech

Visão geral
O projeto LeadOps TI / Mini CRM Biotech nasceu para organizar e acelerar a prospecção comercial de serviços de TI da Biotech, com foco em operação local, controle de leads, histórico de interações, funil comercial, priorização por score e apoio à abordagem por WhatsApp, e-mail e webmail. A ideia central sempre foi ter uma ferramenta leve, prática e utilizável no dia a dia, sem dependência inicial de CRM externo, mantendo velocidade operacional e controle sobre os dados.

Início do projeto
No início, o projeto foi estruturado como um MVP de mini-CRM local voltado para prospecção B2B, especialmente para empresas e instituições com maior aderência aos serviços da Biotech, como clínicas, hospitais, laboratórios, escolas, empresas com infraestrutura crítica, operações dependentes de rede, backup, servidores, Wi‑Fi, VPN e suporte técnico especializado. O foco geográfico inicial concentrou-se em Formiga/MG e região, com expansão para cidades próximas como Arcos, Piumhi, Campo Belo, Lagoa da Prata e outras do Centro-Oeste mineiro.

A base inicial do projeto foi montada com:
- app local em Streamlit;
- persistência em SQLite;
- importação de leads por CSV;
- score de priorização;
- geração assistida de mensagens;
- histórico de interações;
- funil comercial básico;
- apoio a ações por WhatsApp, Gmail, Outlook e webmail.

Evolução do projeto
Durante a evolução do projeto, foram identificados alguns pontos importantes:

1. Drift de versionamento
Havia inconsistência entre versão exibida no app, README e módulo interno. Isso foi corrigido ao longo das revisões e consolidado em releases mais recentes.

2. Score saturado
Nas primeiras versões, o score estava agressivo demais e muitos leads acabavam com nota máxima ou muito próxima disso, reduzindo o valor real da priorização. O modelo foi recalibrado para gerar separação operacional útil entre leads.

3. Funil comercial pouco consolidado
O funil inicial foi refinado e padronizado para refletir melhor a rotina real de prospecção.

4. Problemas de launcher no Ubuntu
O app inicialmente tentou usar instalação via Python do sistema, mas no notebook Ubuntu houve bloqueio por PEP 668 / externally-managed-environment. A operação foi corrigida para usar .venv local + python -m streamlit, que passou a ser o padrão estável.

5. Aba “Detalhe” com erro visual em navegador mobile
Em versões intermediárias, surgiu erro de front-end na aba Detalhe, com mensagem do tipo removeChild, além de inconsistência visual em alguns cenários móveis. Após debug minucioso, ficou claro que:
- backend e banco estavam íntegros;
- parte da inconsistência foi corrigida por hotfix;
- o restante foi isolado como problema de cache/estado do navegador mobile, e não erro estrutural do app, pois no notebook e no celular em aba anônima a aba funcionou corretamente.

Decisões técnicas consolidadas
As decisões técnicas atuais e consolidadas do projeto são:
- o app principal roda localmente em Streamlit;
- o banco principal é SQLite, preservando simplicidade e portabilidade;
- a instalação principal roda em .venv local, sem depender do Python global do sistema;
- o método confiável de execução passou a ser: python -m streamlit run app.py;
- o projeto principal foi promovido para a pasta: /home/biotech/Documentos/LeadOps_TI;
- a instalação anterior foi preservada como fallback em backup de promoção;
- a operação principal está em porta 8501;
- a versão validada operacionalmente como principal é a v2.3.2.

Funil comercial atual
O funil comercial do projeto foi consolidado no formato:
- Novo
- Contatado
- Respondeu
- Reunião
- Proposta
- Ganhou
- Perdido
- Não contatar

Esse funil é a referência atual do projeto.

Status atual validado
O projeto está ativo, validado e operacional em produção local no notebook, com a versão principal em funcionamento. O ambiente foi testado e validado com sucesso.

Situação atual da base
Estado atual conhecido do banco operacional:
- 42 leads
- 13 interações
- 32 em Novo
- 9 em Contatado
- 1 em Respondeu

Além disso, a aplicação exibe os indicadores operacionais principais normalmente e a base real foi preservada ao longo das atualizações.

Versão atual
- Versão operacional validada: LeadOps TI v2.3.2

Instalação principal
- Pasta principal: /home/biotech/Documentos/LeadOps_TI

Execução principal
- execução em .venv local;
- subida via python -m streamlit;
- porta principal: 8501.

Status funcional atual
Atualmente o projeto já entrega:
- cadastro e visualização de leads;
- score de priorização calibrado;
- funil comercial padronizado;
- histórico de interações;
- recomendações de próxima ação;
- mensagens assistidas para abordagem;
- apoio para WhatsApp e e-mail;
- exportação;
- operação local estável.

Situação da aba Detalhe
A aba Detalhe está funcional no ambiente correto. O erro vermelho que apareceu em navegador móvel foi isolado como problema de cache/estado antigo do navegador, porque:
- no notebook funcionou corretamente;
- no celular em aba anônima também funcionou corretamente.

Portanto, o app não está estruturalmente quebrado nessa área. Em caso de repetição no celular, a ação correta é limpar os dados/cache do site no navegador.

Status do backend e do banco
O backend está íntegro e o banco também. Não foi encontrada evidência de corrupção do leadops.db. Os problemas encontrados no projeto até aqui foram predominantemente:
- launcher/ambiente Python;
- drift de versão;
- score saturado;
- comportamento de UI em front-end/caching.

Esses pontos foram tratados e o ambiente atual está utilizável.

Operação atual recomendada
A operação principal deve continuar em cima da instalação atual já promovida. O projeto deve ser tratado como a base oficial do LeadOps TI, com uso diário para:
- registrar contatos;
- evoluir leads no funil;
- registrar interações;
- acompanhar próximos passos;
- medir avanço real da prospecção.

Próximos passos recomendados
Próximos passos estratégicos do projeto:

1. Operação comercial disciplinada
- avançar os leads em Novo;
- trabalhar os Contatado;
- amadurecer o lead em Respondeu;
- registrar toda interação no CRM.

2. Higiene e endurecimento operacional
- revisar exposição do Streamlit em rede;
- preferir acesso local/rede interna controlada;
- avaliar binding apenas em localhost ou endurecimento de acesso, se necessário.

3. Melhorias futuras
- autostart no notebook ao ligar;
- evolução da UI;
- possíveis dashboards adicionais;
- refinamento contínuo de scoring e cadência comercial.

Resumo executivo final
O projeto LeadOps TI / Mini CRM Biotech começou como um MVP local para organizar a prospecção comercial da Biotech e evoluiu para uma ferramenta operacional real, com banco ativo, funil consolidado, histórico de interações, score recalibrado e versão principal validada em produção local. O projeto passou por correções de versão, correção de launcher, saneamento de ambiente Python e hotfixes de interface. Hoje, encontra-se em estado operacional, com a v2.3.2 validada, banco real preservado e uso recomendado como base principal da operação comercial.
