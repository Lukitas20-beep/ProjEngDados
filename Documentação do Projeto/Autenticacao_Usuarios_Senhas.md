# Gestão de Autenticação de Usuários e Gestão de Senhas

## 1. Contexto do requisito

O projeto **PNCP Data Engine** tem como objetivo permitir a extração, transformação, visualização e carga de dados de contratações públicas obtidos por meio da API do Portal Nacional de Contratações Públicas (PNCP). Como a aplicação permite acesso a funcionalidades de busca, processamento e persistência de dados, torna-se necessário controlar quais usuários podem acessar a interface e executar ações dentro do sistema.

Na documentação inicial do MVP, a autenticação de usuários aparecia como uma funcionalidade fora do escopo inicial. Para a nova etapa do projeto integrado, esse item passa a ser tratado como requisito obrigatório, com foco em controle de acesso, cadastro de usuários, login, logout e gestão segura de senhas.

## 2. Objetivo do requisito

Implementar um mecanismo básico de autenticação na aplicação Streamlit, garantindo que apenas usuários cadastrados possam acessar o pipeline ETL, buscar dados do PNCP e salvar registros no MongoDB Atlas. O requisito também busca melhorar a segurança do projeto, removendo credenciais sensíveis do código-fonte e utilizando armazenamento seguro de senhas.

## 3. Requisitos funcionais

| Código | Requisito funcional | Descrição |
| :--- | :--- | :--- |
| RF06 | Cadastro de usuários | O sistema deve permitir o cadastro de usuários com nome, e-mail e senha. |
| RF07 | Login de usuários | O sistema deve autenticar usuários cadastrados por meio de e-mail e senha. |
| RF08 | Controle de sessão | O sistema deve manter o usuário autenticado durante a sessão de uso da aplicação. |
| RF09 | Logout | O sistema deve permitir que o usuário encerre sua sessão. |
| RF10 | Alteração de senha | O sistema deve permitir que o usuário autenticado altere sua senha mediante confirmação da senha atual. |
| RF11 | Bloqueio de acesso não autenticado | O sistema deve impedir que usuários não autenticados acessem as funcionalidades de busca, processamento e carga de dados. |

## 4. Requisitos não funcionais

| Código | Requisito não funcional | Descrição |
| :--- | :--- | :--- |
| RNF05 | Segurança de senhas | As senhas não devem ser armazenadas em texto puro. O sistema deve armazenar apenas hashes seguros das senhas. |
| RNF06 | Validação mínima de senha | O sistema deve exigir senha com pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula e um número. |
| RNF07 | Proteção de credenciais | Credenciais sensíveis, como a URI do MongoDB, devem ser armazenadas em variáveis de ambiente, e não diretamente no código. |
| RNF08 | Usabilidade | As telas de login, cadastro e alteração de senha devem ser simples e compatíveis com a interface Streamlit já existente. |
| RNF09 | Manutenibilidade | A lógica de autenticação deve ficar separada em um módulo próprio, evitando misturar regras de segurança com o código principal da interface. |

## 5. Regra de negócio

O usuário só poderá acessar a tela principal do sistema após autenticação bem-sucedida. Antes do login, a aplicação exibirá apenas as opções de entrada e cadastro. Após o login, o usuário poderá executar buscas na API do PNCP, visualizar os dados tratados e salvar os resultados no MongoDB Atlas.

A senha será armazenada no banco local de usuários apenas em formato de hash, utilizando a biblioteca `bcrypt`. Isso significa que o sistema não guarda a senha original digitada pelo usuário, mas uma representação criptográfica usada apenas para verificação no momento do login.

## 6. Fluxo de autenticação

1. O usuário acessa a aplicação Streamlit.
2. O sistema verifica se há uma sessão ativa.
3. Se não houver sessão ativa, o sistema apresenta a tela de login e cadastro.
4. O usuário pode criar uma conta informando nome, e-mail e senha.
5. O sistema valida a força mínima da senha e salva o usuário no banco local `users.db`.
6. O usuário realiza login com e-mail e senha.
7. O sistema compara a senha informada com o hash salvo no banco.
8. Em caso de sucesso, a sessão é iniciada e o usuário acessa a tela principal.
9. O usuário pode alterar sua senha ou encerrar a sessão.

## 7. Modelagem da tabela de usuários

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| id | INTEGER | Identificador único do usuário. |
| nome | TEXT | Nome do usuário. |
| email | TEXT | E-mail utilizado para login. Deve ser único. |
| senha_hash | TEXT | Hash da senha gerado com bcrypt. |
| ativo | INTEGER | Indica se o usuário está ativo. |
| criado_em | TEXT | Data e hora de criação do usuário. |
| atualizado_em | TEXT | Data e hora da última atualização do usuário. |

## 8. Critérios de aceite

| Critério | Resultado esperado |
| :--- | :--- |
| Cadastro com senha fraca | O sistema deve recusar o cadastro e exibir mensagem de erro. |
| Cadastro com e-mail já existente | O sistema deve impedir duplicidade de usuários. |
| Login com senha incorreta | O sistema deve negar acesso. |
| Login com credenciais corretas | O sistema deve liberar a tela principal da aplicação. |
| Usuário não autenticado | O sistema não deve exibir busca, processamento ou carga de dados. |
| Alteração de senha com senha atual incorreta | O sistema deve recusar a alteração. |
| Alteração de senha válida | O sistema deve atualizar o hash da senha no banco local. |
| URI do MongoDB | A URI deve ser lida de variável de ambiente, não escrita diretamente no código. |

## 9. Ajustes realizados no projeto

Foram adicionados os seguintes elementos ao projeto:

- Criação do módulo `src/auth.py`, responsável por cadastro, login, validação de senha, alteração de senha e persistência dos usuários.
- Atualização do `app.py` para incluir tela de login, tela de cadastro, controle de sessão, logout e alteração de senha.
- Criação do arquivo `.env.example`, indicando as variáveis de ambiente necessárias.
- Atualização do `requirements.txt`, incluindo `streamlit`, `pandas`, `bcrypt` e `python-dotenv`.
- Criação do `.gitignore`, impedindo versionamento de `.env`, banco local de usuários e arquivos temporários.
- Remoção da URI do MongoDB do código-fonte, substituindo-a por `MONGO_URI`.

## 10. Limitações e melhorias futuras

A solução implementada atende ao requisito acadêmico de autenticação e gestão de senhas, mas ainda pode evoluir em versões futuras. Entre as melhorias possíveis estão: recuperação de senha por e-mail, perfis de usuário com permissões diferentes, painel administrativo para ativar ou desativar usuários, registro de logs de acesso e autenticação com provedores externos.
