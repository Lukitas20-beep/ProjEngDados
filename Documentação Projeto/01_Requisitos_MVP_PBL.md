# Documentação de Requisitos, MVP e Metodologia PBL

## 1. Levantamento de Requisitos Integrados

O projeto "PNCP Data Engine" consiste em um pipeline de dados (ETL) que extrai informações de contratações públicas do Portal Nacional de Contratações Públicas (PNCP), transforma os dados para um formato adequado e os carrega em bancos de dados (MongoDB Atlas e SQLite). A interface do usuário é construída com Streamlit.

### Requisitos Funcionais (RF)
* **RF01 - Extração de Dados:** O sistema deve consumir a API REST do PNCP para buscar dados de contratações públicas com base em filtros (UF, Data Inicial, Data Final, Tamanho da Página).
* **RF02 - Transformação de Dados:** O sistema deve limpar e normalizar os dados brutos, "achatando" objetos aninhados e descartando campos irrelevantes.
* **RF03 - Carga de Dados (NoSQL):** O sistema deve permitir a persistência dos dados transformados em um cluster do MongoDB Atlas.
* **RF04 - Carga de Dados (Relacional):** O sistema deve permitir a persistência dos dados em um banco de dados local SQLite para backup e auditoria.
* **RF05 - Interface de Usuário:** O sistema deve fornecer uma interface web interativa (via Streamlit) para configuração de buscas, visualização dos dados processados e acionamento da carga no banco de dados.

### Requisitos Não Funcionais (RNF)
* **RNF01 - Desempenho:** O processo de extração e transformação deve ser otimizado para lidar com paginação e grandes volumes de dados de forma eficiente.
* **RNF02 - Usabilidade:** A interface web deve ser intuitiva, permitindo que usuários sem conhecimento técnico profundo possam realizar buscas e visualizar os resultados.
* **RNF03 - Manutenibilidade:** O código deve seguir o paradigma de Orientação a Objetos (POO), garantindo modularidade e facilidade de manutenção nas camadas de Extração, Transformação e Carga.
* **RNF04 - Segurança:** As credenciais de acesso ao banco de dados (URI do MongoDB) devem ser tratadas de forma segura, evitando exposição no código-fonte público.

## 2. Definição do MVP (Minimum Viable Product)

O MVP do "PNCP Data Engine" foca em entregar o valor principal: a capacidade de buscar, visualizar e armazenar dados de contratações públicas de forma simplificada.

**Escopo do MVP:**
* Interface web básica em Streamlit com filtros essenciais (UF, Data Inicial, Data Final, Quantidade por página).
* Conexão com a API do PNCP para extração de dados da modalidade de contratação (código 8 - Pregão, conforme código atual).
* Transformação básica dos dados (limpeza e estruturação em DataFrame).
* Visualização dos dados em formato de tabela na interface.
* Funcionalidade de salvar os dados processados no MongoDB Atlas.

**Fora do Escopo do MVP (Próximas Iterações):**
* Filtros avançados (por órgão, valor, modalidade dinâmica).
* Dashboards analíticos complexos e gráficos interativos.
* Automação de extração (agendamento de rotinas ETL).
* Sistema de login e autenticação de usuários.

## 3. Revisão de Escopo e Riscos

### Revisão de Escopo
O escopo atual atende perfeitamente à proposta de um pipeline ETL educacional/funcional. A separação em camadas (Extract, Transform, Load) e a interface Streamlit fornecem uma base sólida. No entanto, para escalar o projeto, será necessário expandir as opções de filtro na interface e implementar tratamento de erros mais robusto na comunicação com a API do PNCP.

### Matriz de Riscos

| Risco | Probabilidade | Impacto | Mitigação |
| :--- | :--- | :--- | :--- |
| **Indisponibilidade da API do PNCP** | Média | Alto | Implementar *retries* (tentativas) automáticas e mensagens de erro claras para o usuário na interface. |
| **Mudança na estrutura de dados da API** | Baixa | Alto | Criar testes unitários para a camada de transformação, garantindo que mudanças na API sejam detectadas rapidamente. |
| **Exposição de credenciais do Banco de Dados** | Média | Alto | Utilizar variáveis de ambiente (`.env`) para armazenar a URI do MongoDB, removendo-a do código-fonte (`app.py` e `main.py`). |
| **Estouro de memória no processamento** | Baixa | Médio | Implementar processamento em lotes (batches) para grandes volumes de dados, evitando carregar tudo na memória RAM de uma vez. |

## 4. Metodologia PBL (Project-Based Learning)

A execução deste projeto segue a metodologia de Aprendizagem Baseada em Projetos (PBL), focando na resolução de um problema real (acesso e análise de dados públicos) através da construção de uma solução tecnológica.

**Fases da Execução PBL:**
1. **Apresentação do Problema:** Dificuldade em acessar, limpar e analisar dados de contratações públicas do PNCP de forma estruturada.
2. **Investigação e Pesquisa:** Estudo da documentação da API do PNCP, modelagem de dados NoSQL (MongoDB) e frameworks de interface (Streamlit).
3. **Desenvolvimento da Solução:** Implementação do pipeline ETL em Python, utilizando POO para estruturar o código.
4. **Apresentação e Feedback:** Demonstração da interface Streamlit funcionando, com carga de dados no MongoDB, seguida de avaliação pelos pares e professores.
5. **Reflexão e Iteração:** Análise dos resultados, identificação de melhorias (ex: segurança de credenciais, novos filtros) e planejamento para futuras versões.
