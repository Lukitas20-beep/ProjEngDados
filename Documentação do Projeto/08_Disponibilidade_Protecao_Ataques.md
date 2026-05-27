# Documento de Requisito 4 — Disponibilidade e proteção contra ataques digitais

## 1. Contexto

A quarta entrega complementa as camadas já implementadas no PNCP Data Engine: autenticação e gestão de senhas, anonimização de dados em repouso e atendimento básico à LGPD. O foco agora é reduzir riscos de indisponibilidade e ataques simples contra a aplicação, especialmente em pontos de entrada como login, filtros de busca, chamadas à API externa do PNCP e carga no MongoDB.

## 2. Objetivo

Implementar controles básicos de disponibilidade e proteção contra ataques digitais, garantindo que a aplicação valide entradas, limite tentativas de autenticação, registre eventos de segurança, trate falhas de serviços externos e forneça uma visão mínima da saúde operacional do sistema.

## 3. Escopo da implementação

- Criação do módulo `src/security.py`.
- Limitação de tentativas de login por e-mail.
- Bloqueio temporário após repetidas falhas de autenticação.
- Registro local de eventos de segurança em `security_events.db`.
- Validação de UF, datas, intervalo de consulta e tamanho da página.
- Sanitização do nome da coleção antes de salvar dados no MongoDB.
- Timeout e retentativas nas chamadas à API do PNCP.
- Tratamento de erros HTTP e falhas de conexão.
- Validação do texto enviado para classificação CNAE.
- Painel de segurança e disponibilidade na interface Streamlit.
- Health check de ambiente, API PNCP e MongoDB.
- Atualização das variáveis de ambiente de segurança no `.env.example`.
- Reforço do `.gitignore` para evitar versionamento de bancos locais, logs, caches e arquivos sensíveis.

## 4. Requisitos funcionais

| Código | Requisito | Descrição |
|---|---|---|
| RF01 | Controle de tentativas de login | O sistema deve registrar falhas de login por e-mail. |
| RF02 | Bloqueio temporário | O sistema deve bloquear temporariamente login após excesso de tentativas inválidas. |
| RF03 | Validação de filtros | O sistema deve validar UF, datas e quantidade por página antes de consultar a API. |
| RF04 | Tratamento de falhas externas | O sistema deve aplicar timeout, retentativas e mensagens de erro em chamadas ao PNCP. |
| RF05 | Sanitização de coleção | O sistema deve sanitizar nomes de coleção antes da persistência no MongoDB. |
| RF06 | Registro de eventos | O sistema deve registrar eventos de login, falhas, entradas inválidas, health checks e cargas. |
| RF07 | Painel de disponibilidade | O sistema deve exibir checagens básicas de saúde dos serviços. |

## 5. Requisitos não funcionais

| Código | Requisito | Descrição |
|---|---|---|
| RNF01 | Disponibilidade | Falhas externas devem ser tratadas sem quebrar a aplicação. |
| RNF02 | Segurança | Entradas do usuário devem ser validadas antes de uso em chamadas externas ou persistência. |
| RNF03 | Rastreabilidade | Eventos relevantes de segurança devem ser registrados localmente. |
| RNF04 | Configurabilidade | Limites de login, timeout e retentativas devem ser configuráveis por variáveis de ambiente. |
| RNF05 | Manutenibilidade | Os controles de segurança devem ficar concentrados em módulo próprio. |

## 6. Arquivos impactados

| Arquivo | Alteração |
|---|---|
| `src/security.py` | Novo módulo com validações, limitação de login, logs e health checks. |
| `app.py` | Integração dos controles de login, validação de filtros, painel de segurança e eventos. |
| `src/extract.py` | Inclusão de timeout, retentativas e tratamento de falhas da API PNCP. |
| `src/load.py` | Sanitização de nome de coleção e timeout de conexão MongoDB. |
| `src/classify.py` | Validação e sanitização do texto enviado ao classificador CNAE. |
| `.env.example` | Inclusão das variáveis de segurança e disponibilidade. |
| `.gitignore` | Reforço para não versionar bancos locais, logs, caches e arquivos sensíveis. |

## 7. Critérios de aceite

- Após o número máximo de falhas configurado, o login deve ser temporariamente bloqueado.
- UF inválida deve impedir a consulta ao PNCP.
- Datas em formato incorreto devem impedir a consulta ao PNCP.
- Intervalo de datas acima do limite configurado deve ser recusado.
- Falhas da API PNCP devem retornar mensagem amigável ao usuário.
- Nome de coleção deve ser sanitizado antes da carga no MongoDB.
- A aplicação deve exibir painel de segurança e disponibilidade.
- Eventos de segurança devem ser registrados em banco local.

## 8. Limitações e melhorias futuras

A solução atende ao requisito acadêmico, mas ainda pode evoluir com firewall de aplicação, autenticação multifator, rate limit por IP, logs centralizados, monitoramento externo, alertas automáticos, varredura de dependências vulneráveis e testes automatizados de segurança.
