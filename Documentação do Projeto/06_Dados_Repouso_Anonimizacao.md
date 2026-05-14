# DOCUMENTO DE REQUISITO
## Gerenciamento de Dados em Repouso / Anonimização de Informações

**Desenvolvido por:** Lucas Ferreira, Isaac Daniel, Arthur Orange, Antônio, Guilherme, Gabriel Garcia, Priscila Maciel e João Lucas Santos Lira  
**GitHub:** https://github.com/Lukitas20-beep/ProjEngDados  
**Projeto Integrado - PNCP Data Engine**

| Campo | Descrição |
|---|---|
| Requisito avaliado | 2 - Gerenciamento de dados em repouso / anonimização de informações |
| Período de documentação | 13-14/05 |
| Data de avaliação da implementação | 10-11/06 |
| Sistema | Aplicação Streamlit para extração, transformação, visualização e carga de dados do PNCP |
| Versão do documento | 1.0 |

## 1. Contexto do requisito

O PNCP Data Engine realiza extração, transformação, visualização e carga de dados obtidos a partir da API do Portal Nacional de Contratações Públicas. Na entrega anterior, o sistema passou a contar com autenticação de usuários, cadastro, login, logout, alteração de senha e armazenamento seguro das senhas por meio de hash.

A segunda entrega complementa essa camada de segurança com foco nos dados armazenados em repouso, isto é, dados já persistidos em bases locais ou externas. No projeto, esses dados podem estar presentes no banco local de usuários (`users.db`), no banco local de contratações (`contratacoes.db`), em variáveis de ambiente e nas coleções salvas no MongoDB Atlas. Mesmo que os dados do PNCP sejam majoritariamente públicos, o sistema também manipula informações de usuários cadastrados e pode receber, em versões futuras, campos que contenham informações pessoais ou sensíveis.

## 2. Objetivo do requisito

Implementar e documentar mecanismos básicos de gerenciamento de dados em repouso e anonimização de informações. O objetivo é reduzir a exposição de dados pessoais, impedir armazenamento desnecessário de campos sensíveis e aplicar anonimização ou mascaramento antes da persistência no MongoDB quando houver campos identificáveis.

## 3. Escopo da entrega

- Criação de um módulo próprio de segurança de dados e anonimização.
- Identificação de campos potencialmente sensíveis, como e-mail, CPF, telefone, senha e responsáveis.
- Aplicação de mascaramento para e-mails e documentos.
- Aplicação de hash determinístico para campos sensíveis que precisem ser comparáveis sem expor o valor original.
- Remoção lógica de valores de senha quando algum campo desse tipo aparecer em registros a serem persistidos.
- Inclusão de opção na interface para aplicar anonimização antes de salvar dados no MongoDB.
- Restrição de permissões locais do banco de usuários quando o sistema operacional permitir.
- Inclusão de variável `ANONYMIZATION_SALT` no arquivo de exemplo de ambiente.
- Atualização da carga no MongoDB para salvar dados anonimizados por padrão.

## 4. Requisitos funcionais

| Código | Requisito funcional | Descrição |
|---|---|---|
| RF01 | Anonimização antes da carga | O sistema deve permitir aplicar anonimização aos registros antes de salvá-los no MongoDB Atlas. |
| RF02 | Mascaramento de e-mail | O sistema deve mascarar campos de e-mail, preservando apenas parte mínima do endereço. |
| RF03 | Mascaramento de documentos | O sistema deve mascarar documentos identificáveis, exibindo apenas os últimos dígitos. |
| RF04 | Hash de campos sensíveis | O sistema deve substituir campos sensíveis por hash quando for necessário manter possibilidade de comparação sem revelar o valor original. |
| RF05 | Proteção de campos de senha | O sistema não deve persistir valores de senha em registros de dados operacionais. |
| RF06 | Configuração por ambiente | O salt de anonimização deve poder ser configurado por variável de ambiente. |
| RF07 | Controle na interface | A interface deve indicar a possibilidade de aplicar anonimização antes da persistência. |

## 5. Requisitos não funcionais

| Código | Requisito não funcional | Descrição |
|---|---|---|
| RNF01 | Minimização de dados | O sistema deve persistir apenas os campos necessários para a finalidade da aplicação. |
| RNF02 | Segurança em repouso | Arquivos locais com dados de usuários devem ter permissões mais restritas quando possível. |
| RNF03 | Manutenibilidade | A lógica de anonimização deve estar concentrada em módulo próprio, sem ficar espalhada pela interface. |
| RNF04 | Baixo impacto no fluxo principal | A anonimização não deve impedir a execução normal da extração, transformação e carga dos dados. |
| RNF05 | Reprodutibilidade | O hash deve ser determinístico quando utilizado o mesmo salt, permitindo auditoria e comparação controlada. |
| RNF06 | Configurabilidade | Parâmetros sensíveis, como URI do MongoDB e salt de anonimização, devem ser definidos fora do código-fonte. |

## 6. Regra de negócio

Por padrão, os dados enviados ao MongoDB devem passar pela camada de anonimização. Caso o registro contenha campos identificados como sensíveis, o sistema deve mascarar ou substituir esses valores antes da persistência. Campos de senha não devem ser armazenados em registros operacionais. E-mails e documentos devem ser substituídos por estrutura contendo valor mascarado e hash, reduzindo a exposição do dado original.

No caso dos dados do PNCP utilizados atualmente, os registros tratados possuem campos como número de controle, objeto da contratação, órgão, valor, UF, município, modalidade e data de abertura. Esses campos são predominantemente públicos e administrativos. Ainda assim, a camada de anonimização foi implementada para proteger o sistema caso a API ou futuras expansões passem a incluir campos identificáveis, como responsável, e-mail, telefone ou documentos.

## 7. Fluxo de gerenciamento e anonimização

1. O usuário autenticado executa uma busca na API do PNCP.
2. O sistema transforma os dados brutos em registros estruturados.
3. A interface mantém a opção de anonimização ativada antes da carga.
4. Ao salvar no MongoDB, o módulo de carga chama a camada de anonimização.
5. O módulo percorre os registros e identifica chaves potencialmente sensíveis.
6. Campos de e-mail são mascarados e recebem hash.
7. Campos de documento são mascarados e recebem hash.
8. Campos de senha são removidos logicamente.
9. Campos sensíveis genéricos são substituídos por hash.
10. Apenas os registros tratados são persistidos na coleção do MongoDB.

## 8. Estratégia de dados em repouso

| Local de armazenamento | Risco identificado | Tratamento aplicado |
|---|---|---|
| `users.db` | Contém nome, e-mail e hash de senha dos usuários | Senhas já ficam em hash; o arquivo recebe permissão local restrita quando possível. |
| `contratacoes.db` | Pode conter dados operacionais locais | Deve ser evitado no versionamento e mantido fora do Git. |
| MongoDB Atlas | Recebe registros processados do PNCP | Dados passam por anonimização antes da persistência quando houver campos sensíveis. |
| `.env` | Pode conter URI do MongoDB e salt de anonimização | Arquivo não deve ser versionado; apenas `.env.example` deve ficar no repositório. |
| Código-fonte | Poderia expor credenciais ou regras sensíveis | Variáveis sensíveis ficam fora do código. |

## 9. Campos tratados pela anonimização

| Tipo de campo | Exemplos | Tratamento |
|---|---|---|
| E-mail | `email`, `e_mail` | Mascaramento parcial e hash SHA-256 com salt. |
| Documento | `cpf`, `cnpj`, `documento`, `identificacao` | Exibição apenas dos últimos dígitos e hash SHA-256 com salt. |
| Senha | `senha`, `password` | Remoção lógica do valor. |
| Contato | `telefone`, `celular` | Substituição por hash. |
| Responsável | `responsavel`, `nome_responsavel` | Substituição por hash. |

## 10. Critérios de aceite

| Critério | Resultado esperado |
|---|---|
| Registro com e-mail | O e-mail não deve ser salvo em texto puro após anonimização. |
| Registro com CPF ou documento | O documento deve ser mascarado e acompanhado de hash. |
| Registro com campo de senha | O valor original da senha não deve ser persistido. |
| Carga no MongoDB com anonimização ativada | Os registros devem ser salvos já tratados. |
| Ausência de campos sensíveis | O sistema deve salvar os dados normalmente, sem alterar campos públicos. |
| Arquivo `.env` | Não deve ser versionado no Git. |
| Banco local de usuários | Deve receber restrição de permissão quando o sistema operacional permitir. |

## 11. Evidências de implementação

Foram adicionados ou alterados os seguintes elementos no projeto:

- Criação do módulo `src/data_security.py`, responsável por mascaramento, hash e anonimização de registros.
- Atualização do `src/load.py` para aplicar anonimização antes de salvar dados no MongoDB.
- Atualização do `app.py` para incluir opção de anonimização antes da persistência.
- Atualização do `pipeline_prefect.py` para aplicar anonimização por padrão na carga automatizada.
- Atualização do `src/auth.py` para restringir permissões locais do banco de usuários quando possível.
- Atualização do `.env.example` com a variável `ANONYMIZATION_SALT`.
- Atualização do `.gitignore` para manter fora do versionamento arquivos como `.env`, bancos locais e caches.
- Inclusão dos campos `fonte_dado` e `contém_dado_pessoal` na transformação, indicando a origem pública dos registros tratados atualmente.

## 12. Arquivos impactados

| Arquivo | Descrição da alteração |
|---|---|
| `src/data_security.py` | Novo módulo de anonimização, mascaramento, hash e proteção de arquivos locais. |
| `src/load.py` | Carga no MongoDB passa a aceitar e aplicar anonimização por padrão. |
| `app.py` | Interface recebe controle para anonimização antes de salvar os dados. |
| `pipeline_prefect.py` | Fluxo automatizado passa a salvar dados com anonimização ativada. |
| `src/auth.py` | Banco local de usuários recebe tentativa de restrição de permissão. |
| `src/transform.py` | Dados tratados recebem metadados sobre fonte e presença de dado pessoal. |
| `.env.example` | Inclui `ANONYMIZATION_SALT`. |
| `.gitignore` | Evita versionamento de arquivos sensíveis e bancos locais. |

## 13. Limitações e melhorias futuras

A solução implementada atende ao requisito acadêmico de gerenciamento de dados em repouso e anonimização, mas ainda pode evoluir. Em uma versão de produção, seria recomendável utilizar criptografia completa do banco local, gerenciamento de chaves em serviço externo, rotação periódica do salt, classificação automática mais robusta de dados pessoais, trilhas de auditoria e políticas formais de retenção e descarte.

Além disso, como a base atual do PNCP contém majoritariamente dados públicos de contratações, a anonimização funciona principalmente como uma camada preventiva para campos sensíveis que possam aparecer em futuras expansões do projeto.

## 14. Conclusão

A segunda entrega adiciona ao PNCP Data Engine uma camada inicial de governança sobre dados em repouso. O sistema passa a reduzir a exposição de informações pessoais, aplicar anonimização antes da persistência no MongoDB e reforçar o cuidado com arquivos locais e variáveis sensíveis. Com isso, a aplicação fica mais alinhada a boas práticas de segurança, privacidade e preparação para os próximos requisitos do projeto integrado, especialmente LGPD, disponibilidade e continuidade de operação.
