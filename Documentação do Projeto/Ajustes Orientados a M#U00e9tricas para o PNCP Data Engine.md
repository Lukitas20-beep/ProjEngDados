# Ajustes Orientados a Métricas para o PNCP Data Engine

## Introdução

Este documento apresenta uma análise estratégica para o projeto "PNCP Data Engine", focando na interpretação de métricas de desempenho e na proposição de ajustes nos fluxos de usuário. O objetivo é maximizar o engajamento e o valor percebido pelos usuários, alinhando o desenvolvimento do produto com objetivos de negócio claros, mesmo em sua fase de protótipo/piloto. A abordagem é orientada por dados, estabelecendo um framework para monitoramento e otimização contínua.

## 1. Definição de Métricas e KPIs Essenciais

Para avaliar o sucesso do "PNCP Data Engine" e guiar futuras iterações, é fundamental estabelecer um conjunto de métricas e Key Performance Indicators (KPIs). Dada a fase atual do projeto, estas métricas servem como um guia para a instrumentação futura e para a interpretação de dados de uso, uma vez que estejam disponíveis. O funil de usuário, delineado a partir da arquitetura do Streamlit (`app.py`) e do sistema de autenticação (`src/auth.py`), orienta a seleção dessas métricas [1] [2].

### 1.1. Funil de Usuário e Ações Chave

O fluxo de interação do usuário com a plataforma pode ser segmentado nas seguintes etapas:

1.  **Acesso à Plataforma:** Visita inicial à aplicação Streamlit.
2.  **Autenticação:** Processo de login ou cadastro de um novo usuário.
3.  **Configuração de Busca:** Interação com os filtros de dados (UF, datas, quantidade por página) na barra lateral.
4.  **Execução de Busca:** Acionamento da funcionalidade principal de extração e processamento de dados.
5.  **Visualização de Dados:** Exibição dos resultados da busca na interface.
6.  **Classificação CNAE (Individual):** Utilização do classificador de IA para um objeto de licitação específico.
7.  **Classificação CNAE (Lote):** Disparo da classificação de IA para múltiplos itens de dados na sessão.
8.  **Salvamento de Dados:** Persistência dos dados processados no MongoDB Atlas.
9.  **Disparo de Pipeline Prefect:** Iniciação de um fluxo ETL automatizado em segundo plano.

### 1.2. Métricas de Adoção e Engajamento

Estas métricas focam no comportamento do usuário e na sua interação com as funcionalidades do sistema. A tabela 1 detalha as métricas propostas, sua justificativa e métodos hipotéticos de coleta.

**Tabela 1: Métricas de Adoção e Engajamento**

| Métrica | Descrição | Justificativa | Como Coletar (Hipótese) |
| :--- | :--- | :--- | :--- |
| **Usuários Registrados** | Número total de contas criadas. | Indica o interesse inicial e a barreira de entrada do processo de cadastro. | Contagem de registros na tabela `usuarios` (`users.db`). |
| **Usuários Ativos Diários/Semanais (DAU/WAU)** | Número de usuários únicos que realizam login em um período. | Mede a recorrência de uso e a aderência do produto. | Logs de login ou registro de `st.session_state.usuario_logado` em um banco de dados de eventos. |
| **Sessões por Usuário** | Média de sessões iniciadas por usuário ativo. | Indica o quão frequentemente os usuários retornam à plataforma. | Logs de sessão associados ao ID do usuário. |
| **Tempo Médio na Sessão** | Duração média de cada sessão de usuário. | Sugere o nível de engajamento e a profundidade da interação. | Marcação de tempo de início e fim da sessão. |
| **Buscas Realizadas** | Número total de vezes que o botão "Buscar e Processar Dados" é clicado. | Métrica central para a funcionalidade principal do produto. | Registro de eventos no backend ou Streamlit callbacks. |
| **Classificações CNAE (Individual/Lote)** | Número de vezes que o classificador de IA é utilizado. | Indica o valor percebido da funcionalidade de IA. | Registro de eventos específicos para cada tipo de classificação. |
| **Salvamentos no MongoDB** | Número de vezes que os dados são persistidos no MongoDB. | Representa a conclusão do ciclo de valor para o usuário. | Registro de eventos no `Load` ou Streamlit callbacks. |
| **Pipelines Prefect Disparados** | Número de execuções do pipeline automatizado iniciadas. | Mede a adoção da funcionalidade de automação. | Logs do Prefect ou registro de eventos no Streamlit. |

### 1.3. Métricas de Performance e Qualidade

Estas métricas avaliam a eficiência e a confiabilidade do sistema, impactando diretamente a experiência do usuário. A Tabela 2 apresenta as métricas de performance.

**Tabela 2: Métricas de Performance e Qualidade**

| Métrica | Descrição | Justificativa | Como Coletar (Hipótese) |
| :--- | :--- | :--- | :--- |
| **Taxa de Sucesso da Extração** | Proporção de buscas que retornam dados válidos. | Indica a robustez da integração com a API do PNCP. | Monitoramento de `error` no retorno de `Extract.extract_contratacoes`. |
| **Tempo Médio de Processamento (ETL)** | Duração média desde o clique em "Buscar" até a visualização dos dados. | Afeta diretamente a experiência do usuário e a usabilidade. | Marcação de tempo no backend do Streamlit. |
| **Latência da Classificação CNAE** | Tempo médio para a resposta do modelo Groq LLaMA. | Crítico para a usabilidade da funcionalidade de IA. | Marcação de tempo na chamada à API Groq. |
| **Erros de Autenticação** | Número de tentativas de login/cadastro falhas. | Pode indicar problemas de usabilidade ou segurança. | Logs de autenticação (`AuthManager`). |

### 1.4. Key Performance Indicators (KPIs)

Os KPIs são indicadores estratégicos que traduzem o sucesso do produto e do negócio, sendo cruciais para a tomada de decisão e para a validação das estratégias de monetização.

*   **Taxa de Ativação:** Percentual de usuários registrados que realizam pelo menos uma busca e visualizam os dados na primeira semana. Este KPI é fundamental para validar a eficácia do *onboarding* e a percepção inicial de valor do produto.
*   **Frequência de Uso:** Número médio de buscas por usuário ativo por semana. Este KPI mede a aderência e a utilidade contínua da plataforma, indicando o quão essencial o produto se tornou para a rotina do usuário.
*   **Retenção de Usuários (Semanal/Mensal):** Percentual de usuários que retornam à plataforma após um período definido. Um alto índice de retenção é vital para a sustentabilidade do produto e para a construção de uma base de usuários leais.
*   **Engajamento com Funcionalidades Premium (Hipótese):** Percentual de usuários que utilizam o classificador CNAE em lote ou disparam pipelines Prefect. Este KPI é um preditor importante do interesse em funcionalidades de maior valor agregado, que são candidatas à monetização.
*   **Taxa de Conversão Freemium (Hipótese):** Percentual de usuários da versão gratuita que assinam um plano premium. Este KPI validará diretamente a estratégia de monetização e a percepção de valor das funcionalidades pagas.
*   **ARPU (Average Revenue Per User) - Hipótese:** Receita média gerada por usuário pagante. Mede a eficácia dos planos de monetização e a capacidade de gerar receita por usuário.
*   **Churn Rate (Hipótese):** Percentual de usuários pagantes que cancelam a assinatura. Um baixo *churn rate* é indicativo de alta satisfação e retenção de clientes pagantes.

## 2. Análise de Fluxos e Propostas de Ajuste para Maximizar Engajamento e Valor Percebido

Com base nas métricas e KPIs definidos, a análise dos fluxos de usuário existentes no "PNCP Data Engine" revela oportunidades significativas para otimização. As propostas de ajuste visam aprimorar a jornada do usuário, aumentar a percepção de valor e preparar a plataforma para estratégias de monetização, especialmente o modelo Freemium [3].

### 2.1. Otimização do Onboarding e Experiência Inicial

O fluxo de autenticação, embora funcional, carece de um *onboarding* explícito. A introdução de um **tour guiado interativo** após o cadastro/login pode reduzir a curva de aprendizado e destacar rapidamente as funcionalidades chave, como a configuração de buscas e o classificador CNAE. Isso impactará positivamente a **Taxa de Ativação**, garantindo que mais usuários experimentem o valor central do produto desde o início.

### 2.2. Melhoria da Busca e Visualização de Dados

O fluxo de busca e visualização é o coração da aplicação. Para maximizar o engajamento, propõe-se:

*   **Filtros Avançados:** Expandir as opções de filtro na barra lateral, incluindo busca por palavra-chave no objeto da licitação, seleção de múltiplas UFs e, crucialmente, a **seleção dinâmica da modalidade de contratação**. A modalidade fixa atual no pipeline automatizado (`pipeline_prefect.py`) limita a flexibilidade [4].
*   **Visualização Enriquecida:** Aprimorar a apresentação dos dados, substituindo o `st.dataframe` básico por **dashboards interativos e personalizáveis**. Isso pode incluir gráficos de distribuição por UF, por valor, ou por modalidade, transformando a plataforma de um mero extrator para uma ferramenta de *insights*. Esta melhoria visa aumentar a **Frequência de Uso** e o **Tempo Médio na Sessão**.
*   **Exportação de Dados:** Adicionar funcionalidades claras para exportar os dados visualizados em formatos úteis (CSV, Excel), agregando valor para usuários que precisam manipular os dados externamente.

### 2.3. Aprimoramento da Classificação CNAE

A funcionalidade de classificação CNAE com IA é um diferencial. Para otimizá-la:

*   **Feedback Visual:** Implementar um **indicador de progresso** (`st.progress`) para a classificação em lote, ou exibir os resultados incrementalmente, melhorando a experiência do usuário e a percepção de performance.
*   **Histórico de Classificações:** Permitir que o usuário visualize um histórico das classificações realizadas, aumentando a utilidade e a rastreabilidade da funcionalidade.
Esses ajustes visam aumentar o **Engajamento com Funcionalidades Premium**, preparando o terreno para a monetização desta capacidade.

### 2.4. Flexibilização e Monitoramento do Pipeline Prefect

A orquestração via Prefect é uma capacidade poderosa, mas sua flexibilidade para o usuário final é limitada. As propostas incluem:

*   **Parâmetros Dinâmicos:** Permitir que o usuário **configure os parâmetros (UF, datas, modalidade) do pipeline Prefect diretamente na interface** antes de dispará-lo, em vez de depender apenas de variáveis de ambiente. Isso empodera o usuário e aumenta o valor percebido da automação.
*   **Notificações e Relatórios:** Integrar um sistema de notificações no Streamlit para informar sobre a conclusão ou falha dos pipelines, e oferecer um link direto para relatórios resumidos ou para a visualização dos dados processados no MongoDB. Isso melhora a experiência de uso e o monitoramento, impactando o **Engajamento com Funcionalidades Premium**.

### 2.5. Implementação de Paywall e Diferenciação de Funcionalidades

Para viabilizar a monetização, a introdução de um **paywall estratégico** é essencial. Este deve diferenciar as funcionalidades entre a versão gratuita e a premium:

*   **Versão Gratuita:** Limitar o número de buscas diárias, a quantidade de registros por busca, e/ou restringir o acesso a filtros avançados e à classificação CNAE em lote.
*   **Versão Premium:** Desbloquear limites, oferecer filtros avançados, classificação em lote ilimitada, acesso a dashboards personalizados e a capacidade de agendar pipelines com parâmetros dinâmicos.

Esta diferenciação é crucial para impulsionar a **Taxa de Conversão Freemium**, transformando usuários engajados em clientes pagantes ao demonstrar o valor adicional das funcionalidades premium.

## 3. Impacto Esperado dos Ajustes nas Métricas e KPIs

Os ajustes propostos são desenhados para gerar um impacto mensurável nos KPIs e métricas, conforme detalhado na Tabela 3.

**Tabela 3: Impacto Esperado dos Ajustes nos KPIs e Métricas**

| Ajuste Proposto | KPIs Impactados | Métricas Impactadas | Justificativa do Impacto |
| :--- | :--- | :--- | :--- |
| **Otimização do Onboarding** | Taxa de Ativação | Usuários Registrados, Sessões por Usuário | Reduz a barreira inicial, demonstra valor rapidamente, incentivando o uso contínuo. |
| **Filtros Avançados e Visualização Enriquecida** | Frequência de Uso, Retenção de Usuários | Tempo Médio na Sessão, Buscas Realizadas | Aumenta a utilidade e a capacidade de análise da ferramenta, mantendo o usuário engajado por mais tempo. |
| **Aprimoramento Classificação CNAE** | Engajamento com Funcionalidades Premium | Classificações CNAE (Individual/Lote) | Melhora a experiência com IA, tornando-a mais confiável e eficiente, incentivando seu uso. |
| **Flexibilização Pipeline Prefect** | Engajamento com Funcionalidades Premium | Pipelines Prefect Disparados | Oferece maior controle e automação, transformando a funcionalidade em um recurso premium valioso. |
| **Implementação de Paywall** | Taxa de Conversão Freemium, ARPU, Churn Rate | Usuários Ativos, Salvamentos no MongoDB | Cria um incentivo claro para a conversão, diferenciando o valor das versões gratuita e premium. |

## Conclusão

O "PNCP Data Engine" possui uma base técnica sólida e funcionalidades de alto valor, como a classificação CNAE por IA e a orquestração de pipelines. Ao implementar os ajustes propostos nos fluxos de usuário, com foco em um *onboarding* mais eficaz, funcionalidades de busca e visualização enriquecidas, e uma clara diferenciação entre ofertas gratuitas e premium, o projeto pode transicionar de um protótipo para um produto com um caminho de monetização bem definido. O monitoramento contínuo das métricas e KPIs será essencial para validar essas hipóteses e guiar a evolução futura do produto, garantindo que os ajustes sejam sempre orientados a maximizar o engajamento e o valor percebido pelo usuário.

## Referências

[1] `app.py` - Interface do usuário Streamlit com sistema de autenticação.
[2] `src/auth.py` - Módulo de autenticação de usuários.
[3] `revised_monetization_strategy.md` - Documento de Estratégia de Negócio, UX e Monetização (Revisado).
[4] `pipeline_prefect.py` - Orquestrador automatizado do ETL usando Prefect 2.
