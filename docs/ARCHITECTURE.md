# Arquitetura — LeadOps TI / Mini CRM Biotech

## Visão técnica

O projeto foi desenhado para ser um mini-CRM local, leve e rápido, sem dependência inicial de plataforma externa. A arquitetura prioriza simplicidade operacional, portabilidade e domínio total sobre os dados.

## Componentes principais

### Aplicação

- interface principal em **Streamlit**;
- foco em operação prática, velocidade de uso e baixa fricção.

### Persistência

- banco principal em **SQLite**;
- escolha orientada por simplicidade, portabilidade e manutenção leve.

### Execução

- ambiente principal em **`.venv` local**;
- método confiável de subida: `python -m streamlit run app.py`;
- porta operacional principal: `8501`.

## Decisões arquiteturais consolidadas

- evitar dependência do Python global do sistema;
- preservar a base real durante atualizações;
- manter backup anterior para rollback rápido;
- priorizar uso local ou rede interna controlada;
- manter a solução simples antes de expandir para integrações mais pesadas.

## Fluxo funcional de alto nível

1. cadastro/importação de leads;
2. classificação/priorização por score;
3. navegação da fila comercial;
4. registro de interações;
5. evolução do lead no funil;
6. geração de apoio à abordagem.

## Evolução recente da UX operacional

A principal evolução recente foi a transformação da aba **Detalhe** em uma fila de ação mais útil para o dia a dia comercial, reduzindo atrito de navegação e melhorando a cadência de abordagem.

## Diretriz de versionamento

O repositório deve refletir o estado operacional real do projeto, evitando drift entre README, versão exibida no app e documentação.

## Diretriz de segurança

Não versionar dados reais, banco operacional, logs, backups locais ou qualquer segredo de operação.
