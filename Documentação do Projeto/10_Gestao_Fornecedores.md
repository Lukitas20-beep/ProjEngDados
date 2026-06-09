# Documento de Requisito 6 - Gestão de Fornecedores

## 1. Contexto

O PNCP Data Engine utiliza fornecedores e componentes externos para obter dados, persistir informações, classificar objetos de contratação, executar pipelines e compor a interface da aplicação. Depois das entregas de autenticação, anonimização, LGPD, proteção contra ataques e backup, a sexta entrega organiza a governança desses fornecedores.

## 2. Objetivo

Implementar e documentar um controle básico de gestão de fornecedores, mantendo inventário dos serviços, APIs, bibliotecas e componentes externos utilizados pelo projeto, com classificação de criticidade, finalidade, dados tratados, riscos, mitigações e registro de avaliações.

## 3. Escopo

- Criação do módulo `src/vendor_management.py`.
- Cadastro inicial de fornecedores e componentes críticos.
- Classificação por categoria, tipo, criticidade e status.
- Registro dos dados tratados por fornecedor.
- Mapeamento de riscos e medidas de mitigação.
- Checagem de variáveis de ambiente associadas a fornecedores.
- Registro de avaliações por critério.
- Exportação do inventário em JSON.
- Inclusão da área "Gestão de fornecedores" no Streamlit.

## 4. Fornecedores/componentes mapeados

- PNCP API.
- MongoDB Atlas.
- Groq API.
- Streamlit.
- Prefect.
- Kafka/kafka-python.
- Spark/PySpark.
- Docker/Docker Compose.
- Bibliotecas Python do projeto.

## 5. Critérios de aceite

- O sistema deve exibir inventário de fornecedores na aplicação.
- O sistema deve permitir exportar o inventário em JSON.
- O sistema deve indicar finalidade, dados tratados, criticidade, risco e mitigação.
- O sistema deve permitir registrar avaliação de fornecedor.
- O sistema deve listar avaliações recentes.
- O sistema deve verificar variáveis de ambiente associadas aos fornecedores.
- A lógica deve ficar separada em módulo próprio.

## 6. Arquivos impactados

- `src/vendor_management.py`.
- `app.py`.
- `.env.example`.
- `.gitignore`.
- `Documentação do Projeto/10_Gestao_Fornecedores.md`.

## 7. Limitações

A solução atende ao escopo acadêmico do projeto, mas não substitui um processo corporativo completo de gestão de terceiros. Em produção, seria recomendável incluir due diligence formal, contratos, SLAs, DPAs, revisões periódicas de segurança, análise de vulnerabilidades e responsáveis institucionais.
