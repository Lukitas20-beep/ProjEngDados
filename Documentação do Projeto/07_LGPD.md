# DOCUMENTO DE REQUISITO

## Atendimento a Requisitos de LGPD

**Projeto Integrado - PNCP Data Engine**  
**Requisito avaliado:** 3 - Atendimento a requisitos de LGPD  
**Período de documentação:** 20-21/05  
**Data de avaliação da implementação:** 10-11/06  
**Sistema:** Aplicação Streamlit para extração, transformação, visualização e carga de dados do PNCP  
**Versão:** 1.0

## 1. Contexto do requisito

O PNCP Data Engine realiza extração, transformação, visualização e carga de dados obtidos a partir da API do Portal Nacional de Contratações Públicas. Nas entregas anteriores, o sistema passou a contar com autenticação de usuários, cadastro, login, logout, alteração de senha, senha armazenada com hash, externalização de credenciais, anonimização preventiva e cuidados com dados em repouso.

A terceira entrega acrescenta uma camada de conformidade com a Lei Geral de Proteção de Dados Pessoais (LGPD), organizando o tratamento de dados pessoais realizado pelo sistema, especialmente os dados de cadastro dos usuários. A entrega não substitui uma adequação jurídica completa, mas cria mecanismos técnicos e documentais compatíveis com um projeto acadêmico: aviso de privacidade, aceite do usuário, registro simplificado das operações de tratamento, canal para solicitações do titular e evidências de minimização, segurança e transparência.

## 2. Objetivo do requisito

Implementar e documentar mecanismos básicos de atendimento à LGPD no PNCP Data Engine, garantindo que o usuário seja informado sobre o tratamento de seus dados pessoais, registre aceite do aviso de privacidade, tenha acesso aos seus dados de cadastro e possa formalizar solicitações relacionadas aos direitos do titular.

## 3. Escopo da entrega

- Criação de módulo específico para controles de LGPD e privacidade.
- Inclusão de aviso de privacidade na aplicação Streamlit.
- Registro do aceite da política de privacidade por usuário e versão do documento.
- Bloqueio do acesso à aplicação principal até o aceite do aviso de privacidade.
- Criação de registro simplificado das operações de tratamento de dados pessoais.
- Criação de área na interface para consulta de dados pessoais do usuário autenticado.
- Exportação dos dados do usuário em formato JSON.
- Criação de canal interno para solicitações do titular.
- Registro de eventos básicos de privacidade.

## 4. Requisitos funcionais

| Código | Requisito funcional | Descrição |
|---|---|---|
| RF01 | Aviso de privacidade | O sistema deve apresentar ao usuário um aviso de privacidade informando dados tratados, finalidades e direitos. |
| RF02 | Aceite da política | O sistema deve registrar a data, hora e versão da política de privacidade aceita pelo usuário. |
| RF03 | Bloqueio sem aceite | O sistema deve impedir o acesso à tela principal enquanto a política vigente não for aceita. |
| RF04 | Registro de tratamento | O sistema deve exibir um registro simplificado das operações de tratamento de dados pessoais. |
| RF05 | Consulta dos dados do usuário | O usuário autenticado deve conseguir visualizar seus dados de cadastro mantidos pelo sistema. |
| RF06 | Exportação dos dados | O usuário deve conseguir baixar seus dados de cadastro em formato JSON. |
| RF07 | Solicitações do titular | O sistema deve permitir registrar solicitações relacionadas aos direitos do titular. |
| RF08 | Histórico de solicitações | O sistema deve listar as solicitações já registradas pelo usuário autenticado. |
| RF09 | Eventos de privacidade | O sistema deve registrar eventos básicos relacionados a privacidade e segurança. |

## 5. Requisitos não funcionais

| Código | Requisito não funcional | Descrição |
|---|---|---|
| RNF01 | Transparência | O sistema deve informar, em linguagem simples, quais dados são tratados e para quais finalidades. |
| RNF02 | Minimização | O sistema deve manter apenas dados necessários para autenticação, segurança, funcionamento e governança do projeto. |
| RNF03 | Segurança | O sistema deve preservar as medidas das entregas anteriores, como hash de senhas, variáveis de ambiente e anonimização preventiva. |
| RNF04 | Rastreabilidade | Aceites, solicitações e eventos relevantes devem ser registrados para fins de acompanhamento. |
| RNF05 | Manutenibilidade | A lógica de LGPD deve ficar concentrada em módulo próprio. |
| RNF06 | Portabilidade operacional | Os dados do usuário e o registro de tratamento devem poder ser exportados em formato JSON. |

## 6. Regra de negócio

O usuário só poderá utilizar a tela principal do PNCP Data Engine após autenticação e aceite do aviso de privacidade vigente. Caso a versão da política de privacidade seja alterada, o sistema poderá exigir novo aceite. O aceite fica registrado no banco local de usuários, juntamente com a versão do aviso aceita.

Os dados pessoais tratados diretamente pelo sistema são mínimos e se concentram no cadastro dos usuários: nome, e-mail, hash de senha, status do usuário, datas de criação/atualização e aceite da política de privacidade. A senha original não é armazenada. Os dados extraídos do PNCP são, no escopo atual, predominantemente públicos e administrativos, mas continuam submetidos à camada de anonimização preventiva quando houver campos identificáveis.

## 7. Fluxo LGPD na aplicação

1. O usuário acessa a aplicação Streamlit e realiza login com e-mail e senha.
2. O sistema verifica se o usuário já aceitou a versão vigente do aviso de privacidade.
3. Se não houver aceite, a aplicação exibe o aviso de privacidade e bloqueia a tela principal.
4. Após o aceite, o sistema registra data, hora e versão da política aceita.
5. O usuário passa a acessar as funcionalidades principais do pipeline ETL.
6. Na área “Privacidade e LGPD”, o usuário pode consultar o aviso, visualizar o registro de tratamento e baixar seus dados de cadastro.
7. O usuário pode registrar solicitações relacionadas aos direitos do titular.
8. O sistema salva as solicitações em banco local para acompanhamento pela equipe responsável.

## 8. Evidências de implementação

- Criação do módulo `src/lgpd.py`.
- Atualização do `src/auth.py` para incluir campos de aceite da política de privacidade.
- Atualização do `app.py` para bloquear acesso sem aceite da política vigente.
- Criação da área “Privacidade e LGPD” na interface Streamlit.
- Inclusão de visualização e download dos dados do usuário em JSON.
- Inclusão de visualização e download do registro simplificado de tratamento em JSON.
- Inclusão de formulário para registro de solicitações do titular.
- Registro de eventos básicos de privacidade.
- Manutenção da anonimização preventiva da Entrega 2 por meio do módulo `src/data_security.py`.

## 9. Arquivos impactados

| Arquivo | Descrição da alteração |
|---|---|
| `app.py` | Recebeu fluxo de aceite da política de privacidade, área LGPD, exportação de dados e registro de solicitações. |
| `src/lgpd.py` | Novo módulo de governança LGPD, aviso de privacidade, registro de tratamento, solicitações e eventos. |
| `src/auth.py` | Inclui campos e métodos para aceite da política de privacidade, exportação de dados e desativação lógica. |
| `src/data_security.py` | Mantém anonimização, mascaramento, hash de campos sensíveis e restrição de permissões locais. |
| `src/load.py` | Mantém carga no MongoDB com anonimização opcional por padrão. |
| `src/transform.py` | Inclui metadados sobre fonte pública e base legal/justificativa do tratamento. |
| `pipeline_prefect.py` | Mantém carga automatizada com anonimização ativada. |
| `.env.example` | Inclui variáveis de caminho dos bancos locais, salt de anonimização e credenciais administrativas de exemplo. |
| `.gitignore` | Evita versionamento de `.env`, bancos locais, caches e arquivos sensíveis. |

## 10. Conclusão

A terceira entrega adiciona ao PNCP Data Engine uma camada inicial de conformidade com a LGPD. A aplicação passa a informar o usuário sobre o tratamento de dados pessoais, registrar aceite do aviso de privacidade, documentar suas operações de tratamento e oferecer mecanismos básicos para exercício dos direitos do titular. Com isso, o projeto avança da segurança técnica das Entregas 1 e 2 para uma camada de governança, transparência e responsabilização sobre o tratamento de dados pessoais.
