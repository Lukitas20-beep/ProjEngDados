# 09 - Backup e Continuidade de Operação

## Requisito avaliado
5 - Backup e continuidade de operação.

## Contexto
O PNCP Data Engine já possui autenticação, anonimização, controles de LGPD e mecanismos básicos de proteção contra ataques digitais. A Entrega 5 adiciona uma camada operacional para reduzir o risco de perda de dados e facilitar a retomada do sistema em caso de falhas nos bancos locais ou indisponibilidade parcial dos componentes.

## Objetivo
Implementar rotinas básicas de backup, verificação de integridade, restauração controlada e diagnóstico de continuidade operacional, preservando os bancos locais usados pelas entregas anteriores e oferecendo exportação opcional de dados do MongoDB.

## Escopo implementado
- Criação do módulo `src/backup.py`.
- Backup local dos bancos SQLite configurados no projeto.
- Geração de manifesto `manifest.json` com hash SHA-256, tamanho dos arquivos e status de integridade.
- Compactação dos backups em arquivos `.zip`.
- Listagem dos backups disponíveis na interface Streamlit.
- Verificação de integridade dos arquivos de backup.
- Restauração controlada de bancos locais com cópia de segurança anterior.
- Exportação opcional de coleção MongoDB em formato JSONL.
- Política simples de retenção por quantidade de backups e idade máxima.
- Diagnóstico de continuidade operacional.
- Atualização de `.env.example` e `.gitignore`.

## Requisitos funcionais
| Código | Requisito | Descrição |
|---|---|---|
| RF01 | Criar backup local | O sistema deve permitir criar backup dos bancos SQLite locais. |
| RF02 | Gerar manifesto | Cada backup deve conter manifesto com data, arquivos, tamanho, hash e status. |
| RF03 | Compactar backup | O backup deve ser empacotado em arquivo ZIP. |
| RF04 | Listar backups | A interface deve listar os backups disponíveis. |
| RF05 | Verificar integridade | O sistema deve recalcular hashes e validar o pacote de backup. |
| RF06 | Restaurar banco local | O sistema deve restaurar bancos SQLite de forma controlada. |
| RF07 | Preservar cópia anterior | Antes de restaurar, o sistema deve criar cópia do banco substituído. |
| RF08 | Exportar MongoDB | O sistema deve permitir exportação opcional de coleção MongoDB em JSONL. |
| RF09 | Aplicar retenção | O sistema deve remover backups antigos conforme política configurável. |
| RF10 | Verificar continuidade | O sistema deve exibir diagnóstico sobre bancos locais, diretório de backup e último backup. |

## Requisitos não funcionais
| Código | Requisito | Descrição |
|---|---|---|
| RNF01 | Confiabilidade | Backups devem conter hashes para permitir validação posterior. |
| RNF02 | Recuperabilidade | Restaurações devem ser reversíveis por meio de cópia anterior. |
| RNF03 | Segurança operacional | Backups e bancos locais não devem ser versionados no Git. |
| RNF04 | Configurabilidade | Diretório, retenção e limite de exportação devem ser configuráveis por `.env`. |
| RNF05 | Manutenibilidade | A lógica de backup deve ficar concentrada em módulo próprio. |
| RNF06 | Baixo impacto | As rotinas de backup não devem impedir o uso normal da aplicação. |

## Arquivos impactados
| Arquivo | Alteração |
|---|---|
| `src/backup.py` | Novo módulo de backup, verificação, restauração, retenção e continuidade. |
| `app.py` | Inclusão da área "Backup e continuidade de operação" na interface. |
| `.env.example` | Inclusão de variáveis de backup, retenção e caminhos de bancos locais. |
| `.gitignore` | Exclusão de backups, bancos locais, logs e arquivos sensíveis. |
| `Documentação do Projeto/09_Backup_Continuidade_Operacao.md` | Documento técnico da entrega. |

## Critérios de aceite
- Ao clicar em criar backup, o sistema deve gerar um ZIP em `BACKUP_DIR`.
- O ZIP deve conter `manifest.json`.
- A verificação de integridade deve informar se os hashes batem com o manifesto.
- A restauração deve exigir confirmação explícita.
- Antes da restauração, o banco substituído deve ser preservado em cópia de segurança.
- A política de retenção deve remover backups excedentes ou antigos.
- O diagnóstico de continuidade deve indicar bancos existentes, integridade e último backup.

## Limitações e melhorias futuras
A solução atende ao escopo acadêmico do projeto. Em produção, seria recomendável usar armazenamento externo e redundante, criptografia dos backups, rotação de chaves, agendamento automático, alertas, testes periódicos de restauração e infraestrutura com múltiplas zonas de disponibilidade.
