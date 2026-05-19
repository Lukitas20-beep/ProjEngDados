# Entrega 3: Jornada Atual e Jornada Futura - PNCP Data Engine

**Autor:** Manus AI
**Data:** 19 de maio de 2026

## 1. Introdução

Este documento tem como objetivo mapear a experiência do usuário principal do projeto "PNCP Data Engine" antes e depois da implementação da solução. Através da análise da jornada atual (As-Is) e da projeção da jornada futura (To-Be), busca-se evidenciar as dores, fricções e desafios enfrentados pelos usuários no processo de busca e análise de licitações públicas. Concomitantemente, o documento destaca as oportunidades de melhoria e os momentos em que a solução "PNCP Data Engine" gera o maior valor percebido, transformando a rotina e a capacidade estratégica do usuário.

## 2. Persona Principal: Ana, Analista de Licitações

Para contextualizar as jornadas, definimos a persona principal que se beneficiará da solução:

**Nome:** Ana Paula Costa
**Idade:** 35 anos
**Ocupação:** Analista de Licitações em uma empresa de médio porte do setor de serviços (ex: consultoria, TI, engenharia).
**Formação:** Graduação em Administração ou Direito, com especialização em Gestão Pública ou Comércio Exterior.
**Localização:** Grande centro urbano, Brasil.

### Contexto e Objetivos

Ana é responsável por identificar oportunidades de negócios em licitações públicas, analisar editais, preparar propostas e monitorar a concorrência. Seu principal objetivo é garantir que sua empresa participe das licitações mais relevantes e com maior chance de sucesso, otimizando o tempo e os recursos dedicados a esse processo. Ela busca informações precisas e atualizadas para tomar decisões estratégicas.

### Dores e Desafios Atuais

1.  **Fragmentação de Dados:** Os dados de licitações estão espalhados em diversas fontes (PNCP, Diários Oficiais, portais de compras estaduais/municipais), exigindo busca manual e demorada.
2.  **Volume e Complexidade:** O grande volume de editais e a complexidade das informações (termos técnicos, anexos extensos) dificultam a triagem e a análise.
3.  **Falta de Padronização:** Cada órgão ou plataforma pode apresentar os dados em formatos diferentes, exigindo um esforço manual significativo para consolidar e comparar informações.
4.  **Dificuldade de Análise:** A extração de *insights* sobre o mercado, concorrência ou tendências de preços é árdua devido à falta de dados estruturados e ferramentas de análise.
5.  **Perda de Oportunidades:** A demora na identificação de editais relevantes ou a falta de informações estratégicas podem levar à perda de oportunidades de negócio.
6.  **Tempo Consumido:** Grande parte do seu tempo é gasta em tarefas repetitivas de coleta e organização de dados, em vez de análise estratégica.
7.  **Risco de Erro:** A manipulação manual de dados aumenta o risco de erros na interpretação ou na preparação das propostas.

## 3. Jornada Atual (As-Is) da Ana: O Cenário sem o PNCP Data Engine

Esta seção descreve a jornada típica de Ana ao tentar encontrar e analisar editais de licitação relevantes para sua empresa, sem o auxílio do "PNCP Data Engine". É uma jornada caracterizada por ineficiência e alto esforço manual.

**Tabela 1: Jornada Atual (As-Is) da Ana**

| Etapa da Jornada | Ações da Ana | Pensamentos e Sentimentos | Dores e Fricções | Oportunidades de Melhoria |
| :--- | :--- | :--- | :--- | :--- |
| **1. Identificação de Fontes** | Acessa múltiplos portais (PNCP, Diários Oficiais, sites de prefeituras/estados). | _"Onde será que está o edital que preciso?"_ <br> _"Mais um site com interface diferente..."_ | **Fragmentação:** Dados espalhados, necessidade de visitar diversas plataformas. <br> **Inconsistência:** Interfaces e formatos de dados variados. | Centralização das fontes de dados. |
| **2. Busca Manual** | Utiliza filtros básicos em cada portal (palavra-chave, UF, data). Navega por páginas e páginas de resultados. | _"Será que não perdi nada importante?"_ <br> _"Essa busca é muito genérica, preciso de algo mais específico."_ | **Ineficiência:** Busca demorada e repetitiva. <br> **Limitação:** Filtros insuficientes para refinar a pesquisa. <br> **Alto Volume:** Muitos resultados irrelevantes. | Filtros avançados e busca inteligente. |
| **3. Abertura e Leitura de Editais** | Baixa PDFs de editais e anexos. Lê documentos extensos para identificar informações chave (objeto, valor, prazos, requisitos). | _"Preciso encontrar o objeto exato e os requisitos técnicos."_ <br> _"Será que este edital realmente se encaixa no nosso perfil?"_ | **Tempo Consumido:** Leitura exaustiva de documentos longos. <br> **Complexidade:** Linguagem jurídica e técnica densa. <br> **Relevância:** Dificuldade em determinar rapidamente a pertinência do edital. | Sumarização e extração automática de informações chave. |
| **4. Extração Manual de Dados** | Copia e cola informações relevantes para planilhas (Excel) ou sistemas internos. | _"Essa parte é muito chata e repetitiva."_ <br> _"Espero não ter cometido nenhum erro de digitação."_ | **Repetitividade:** Tarefa manual e propensa a erros. <br> **Inconsistência:** Dados em formatos diferentes exigem padronização manual. | Automação da extração e padronização de dados. |
| **5. Análise e Consolidação** | Organiza os dados na planilha. Compara editais, identifica concorrentes, analisa valores. | _"Como posso comparar esses dados de forma eficiente?"_ <br> _"Preciso de uma visão geral do mercado."_ | **Dificuldade de Análise:** Falta de ferramentas para cruzar e visualizar dados de forma eficaz. <br> **Falta de Insights:** Dificuldade em identificar tendências ou padrões. | Ferramentas de visualização e análise de dados. |
| **6. Elaboração de Relatórios** | Prepara relatórios e apresentações para a gerência, com base nos dados coletados e analisados. | _"Meus dados estão atualizados?"_ <br> _"Será que a gerência vai entender a complexidade dessa busca?"_ | **Demora:** Processo de compilação e formatação de relatórios. <br> **Credibilidade:** Dúvida sobre a completude e atualização dos dados. | Geração automática de relatórios e dashboards. |
| **7. Perda de Oportunidades** | Ocorre quando um edital relevante não é encontrado a tempo ou a análise é tardia. | _"Perdemos mais uma licitação por falta de agilidade..."_ <br> _"Se tivéssemos essa informação antes..."_ | **Impacto Financeiro:** Perda de potenciais negócios. <br> **Frustração:** Sentimento de ineficiência e sobrecarga. | Alertas e monitoramento proativo de oportunidades. |

## 4. Jornada Futura (To-Be) da Ana: O Cenário com o PNCP Data Engine

Com a implementação do "PNCP Data Engine", Ana transforma sua rotina de trabalho, passando de um processo manual e reativo para uma abordagem estratégica e proativa. A solução atua como um catalisador, permitindo que ela foque em análise e tomada de decisão, em vez de coleta e organização de dados.

**Tabela 2: Jornada Futura (To-Be) da Ana com PNCP Data Engine**

| Etapa da Jornada | Ações da Ana | Pensamentos e Sentimentos | Ganhos e Valor Gerado | Momentos de "Aha!" (Valor) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Acesso Centralizado** | Acessa o "PNCP Data Engine" via navegador, realiza login na plataforma. | _"Finalmente, tudo em um só lugar!"_ <br> _"Interface intuitiva, fácil de usar."_ | **Centralização:** Um único ponto de acesso para dados de licitações. <br> **Segurança:** Acesso controlado por autenticação. | **Onboarding Eficaz:** Tour guiado inicial que mostra o potencial da ferramenta. |
| **2. Configuração de Busca Inteligente** | Utiliza filtros avançados (UF, datas, modalidade, palavra-chave no objeto) na barra lateral. | _"Posso refinar exatamente o que preciso, sem perder tempo."_ <br> _"Posso até agendar essa busca para rodar automaticamente!"_ | **Eficiência:** Busca rápida e precisa, com filtros granulares. <br> **Flexibilidade:** Seleção dinâmica de modalidades e outros parâmetros. | **Busca Personalizada:** Encontra editais altamente relevantes em segundos. |
| **3. Análise e Visualização de Dados** | Visualiza os resultados em dashboards interativos. Filtra, ordena e explora os dados diretamente na interface. | _"Que visão clara do mercado!"_ <br> _"Posso ver as tendências e os concorrentes de forma muito mais fácil."_ | **Insights Imediatos:** Dados apresentados de forma visual e compreensível. <br> **Análise Aprofundada:** Ferramentas de *drill-down* e comparação. | **Dashboards Interativos:** Transforma dados brutos em inteligência de mercado acionável. |
| **4. Classificação CNAE por IA** | Seleciona um objeto de licitação ou um lote de dados para classificação automática do CNAE. | _"A IA faz o trabalho chato para mim!"_ <br> _"Isso economiza horas de pesquisa manual."_ | **Automação Inteligente:** Classificação rápida e precisa de objetos de licitação. <br> **Redução de Erros:** Diminui a chance de classificação incorreta. | **IA Acelerando o Trabalho:** Obtenção instantânea de códigos CNAE, liberando tempo para análise. |
| **5. Exportação e Integração** | Exporta dados limpos e classificados para planilhas ou integra com sistemas internos via API (futuro). | _"Os dados já vêm prontos para uso, sem retrabalho."_ <br> _"Posso integrar isso facilmente com nossos sistemas."_ | **Padronização:** Dados limpos e estruturados, prontos para uso. <br> **Compatibilidade:** Exportação em formatos comuns. | **Dados Prontos para Decisão:** Eliminação da etapa de tratamento manual de dados. |
| **6. Monitoramento e Alertas** | Configura alertas para novos editais que correspondam aos seus critérios de busca. | _"Serei notificada assim que uma nova oportunidade surgir."_ <br> _"Nunca mais vou perder um edital importante."_ | **Proatividade:** Identificação antecipada de oportunidades. <br> **Redução de Risco:** Minimiza a perda de negócios por falta de informação. | **Alertas Personalizados:** Recebe notificações de novas oportunidades diretamente. |
| **7. Relatórios Automatizados** | Gera relatórios personalizados ou acessa dashboards de monitoramento para a gerência. | _"Meus relatórios são sempre atualizados e baseados em dados sólidos."_ <br> _"A gerência tem uma visão clara do nosso desempenho."_ | **Agilidade:** Geração rápida de relatórios. <br> **Credibilidade:** Relatórios baseados em dados precisos e atualizados. | **Relatórios Estratégicos:** Apresenta análises de alto nível, focando em estratégia. |

## 5. Análise Comparativa e Destaque de Valor

A transição da jornada atual para a jornada futura, mediada pelo "PNCP Data Engine", representa uma mudança paradigmática na forma como Ana interage com os dados de licitações. As principais transformações e os momentos de maior valor gerado pela solução são:

*   **Da Fragmentação à Centralização:** A solução consolida diversas fontes de dados, eliminando a necessidade de Ana navegar por múltiplos portais. Isso economiza tempo e reduz a frustração, tornando a **Busca Inteligente** o primeiro grande momento de valor.
*   **Da Busca Manual à Inteligência de Dados:** A capacidade de usar filtros avançados e a **Visualização Enriquecida** transformam a busca de uma tarefa tediosa em uma atividade estratégica, permitindo que Ana identifique *insights* e tendências de mercado de forma ágil.
*   **Do Trabalho Repetitivo à Automação com IA:** A **Classificação CNAE por IA** automatiza uma tarefa complexa e demorada, liberando Ana para focar em análises de maior nível. Este é um momento de "Aha!" significativo, onde a tecnologia assume o trabalho operacional.
*   **Da Reatividade à Proatividade:** O **Monitoramento e Alertas** garantem que Ana seja informada sobre novas oportunidades em tempo real, permitindo que sua empresa reaja rapidamente e não perca negócios por falta de informação.
*   **Da Dificuldade de Análise à Decisão Estratégica:** A capacidade de gerar **Relatórios Automatizados** e acessar dashboards interativos eleva a qualidade das informações apresentadas à gerência, posicionando Ana como uma consultora estratégica e não apenas uma coletora de dados.

## 6. Conclusão

O "PNCP Data Engine" não é apenas uma ferramenta, mas um catalisador para a transformação digital no processo de análise de licitações. Ao mapear a jornada atual e futura da persona Ana, fica evidente que a solução aborda diretamente as dores e fricções mais críticas, oferecendo ganhos substanciais em eficiência, agilidade e capacidade analítica. Os momentos de maior valor são aqueles em que a plataforma automatiza tarefas repetitivas, centraliza informações e fornece *insights* acionáveis, permitindo que profissionais como Ana dediquem seu tempo a atividades estratégicas que impulsionam o crescimento e a competitividade de suas empresas. A implementação do "PNCP Data Engine" representa um avanço significativo na otimização da experiência do usuário e na entrega de valor no complexo cenário das contratações públicas.

## Referências

[1] `persona_definition.md` - Definição da Persona Principal.
[2] `jornada_atual_ana.md` - Mapeamento da Jornada Atual (As-Is).
[3] `jornada_futura_ana.md` - Mapeamento da Jornada Futura (To-Be).
[4] `app.py` - Interface do usuário Streamlit com sistema de autenticação.
