# Mapeamento de Stakeholders e Técnicas de Negociação (PBL)

No contexto de projetos de Aprendizagem Baseada em Projetos (PBL), como o "PNCP Data Engine", a identificação e o engajamento eficaz dos *stakeholders* são cruciais para o sucesso e a relevância da solução desenvolvida. Além disso, a capacidade de negociar com diferentes partes interessadas garante que as necessidades e expectativas sejam alinhadas.

## 1. Mapeamento de Stakeholders

*Stakeholders* são indivíduos ou grupos que podem afetar ou ser afetados pelo projeto. No "PNCP Data Engine", podemos identificar os seguintes:

### Tabela de Stakeholders

| Stakeholder | Interesse no Projeto | Impacto no Projeto | Estratégia de Engajamento |
| :--- | :--- | :--- | :--- |
| **Equipe de Desenvolvimento** | Sucesso do projeto, aprendizado, aplicação de conhecimentos técnicos. | Alta (desenvolvimento, manutenção, decisões técnicas). | Comunicação diária, reuniões de *sprint*, *code reviews*, feedback contínuo. |
| **Professores/Orientadores** | Qualidade acadêmica, aderência à metodologia PBL, resultados de aprendizado dos alunos. | Alta (avaliação, direcionamento, aprovação de escopo). | Reuniões de acompanhamento, apresentações de progresso, relatórios. |
| **Usuários Finais (Analistas de Dados, Gestores Públicos)** | Acesso fácil e rápido a dados de contratações, insights para tomada de decisão. | Média (feedback sobre usabilidade, requisitos funcionais). | Testes de usabilidade, entrevistas, coleta de feedback sobre a interface Streamlit. |
| **PNCP (Portal Nacional de Contratações Públicas)** | Uso correto da API, conformidade com termos de serviço. | Baixa (fonte de dados, mas sem interação direta com o projeto). | Acompanhamento da documentação da API, respeito aos limites de requisição. |
| **Comunidade Acadêmica/Tecnológica** | Compartilhamento de conhecimento, reuso do projeto, contribuições. | Baixa (potencial para feedback e melhorias futuras). | Publicação do projeto no GitHub, participação em eventos acadêmicos. |

### Análise de Poder e Interesse

Para cada *stakeholder*, é importante analisar seu nível de poder (capacidade de influenciar o projeto) e interesse (grau de preocupação com o projeto). Isso ajuda a definir a estratégia de engajamento:

*   **Alto Poder / Alto Interesse:** Equipe de Desenvolvimento, Professores/Orientadores. Manter totalmente engajados e satisfeitos.
*   **Alto Poder / Baixo Interesse:** (Não se aplica diretamente neste projeto, mas em outros poderia ser a alta gerência que aprova recursos, mas não se envolve no dia a dia).
*   **Baixo Poder / Alto Interesse:** Usuários Finais. Manter informados e consultar regularmente.
*   **Baixo Poder / Baixo Interesse:** PNCP, Comunidade Acadêmica/Tecnológica. Monitorar e manter informados de forma geral.

## 2. Técnicas de Negociação dentro da Metodologia PBL

Negociação é um processo de discussão entre duas ou mais partes para chegar a um acordo. No contexto PBL, a negociação pode ocorrer em diversas situações:

*   **Negociação de Escopo com Professores/Orientadores:**
    *   **Situação:** A equipe identifica que o escopo inicial é muito ambicioso para o tempo disponível ou que novas funcionalidades seriam mais relevantes.
    *   **Técnica:** Apresentar dados e argumentos sólidos (análise de esforço, valor agregado das novas funcionalidades) para justificar a alteração. Focar em uma abordagem ganha-ganha, onde o resultado final ainda atende aos objetivos de aprendizado e qualidade acadêmica.
    *   **Exemplo:** Negociar a priorização de funcionalidades do MVP, explicando que a implementação completa de todos os filtros da API pode comprometer a entrega da funcionalidade principal de ETL.

*   **Negociação Interna na Equipe (Conflito de Ideias):**
    *   **Situação:** Divergências sobre a melhor abordagem técnica (ex: qual banco de dados usar para determinada parte, como estruturar uma classe).
    *   **Técnica:** **Escuta Ativa:** Garantir que todos os pontos de vista sejam ouvidos e compreendidos. **Busca por Consenso:** Tentar encontrar uma solução que satisfaça a maioria, ou uma solução híbrida. **Votação/Decisão do Líder:** Em último caso, se o consenso não for possível e o tempo for crítico, pode ser necessário uma votação ou a decisão final de um líder de equipe, com a justificativa clara.
    *   **Exemplo:** Discutir se a persistência relacional deveria ser PostgreSQL em vez de SQLite, ponderando prós e contras de cada um para o final do projeto.

*   **Negociação com Usuários Finais (Coleta de Requisitos):**
    *   **Situação:** Usuários solicitam funcionalidades que estão fora do escopo do MVP ou são tecnicamente complexas para a fase atual do projeto.
    *   **Técnica:** **Gerenciamento de Expectativas:** Explicar o escopo atual do projeto e o que é viável. **Priorização:** Ajudar o usuário a priorizar as funcionalidades mais importantes. **Roadmap:** Registrar as solicitações para futuras iterações, mostrando que o feedback foi valorizado.
    *   **Exemplo:** Um usuário pode pedir um dashboard complexo, e a equipe negocia que, no MVP, será entregue uma tabela simples com os dados, e o dashboard será considerado para uma próxima fase.

### Princípios de Negociação Eficaz

*   **Preparação:** Entender os próprios objetivos e os da outra parte.
*   **Comunicação Clara:** Expressar ideias de forma concisa e sem ambiguidades.
*   **Flexibilidade:** Estar aberto a diferentes soluções e concessões.
*   **Foco nos Interesses, não nas Posições:** Entender o porquê por trás de uma solicitação, não apenas a solicitação em si.
*   **Busca por Soluções Ganha-Ganha:** Tentar encontrar um resultado que beneficie todas as partes envolvidas, fortalecendo o relacionamento e a colaboração no projeto PBL.
