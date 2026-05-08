# Entrega 1 - Contexto, Problema e Recorte

**Disciplina:** Negócios da Internet – ADS Regular  
**Professor:** Rinack Izidoro Silva Junior  

## Integrantes do Grupo
- Lucas Ferreira
- Isaac Daniel
- Arthur Orange
- Antônio
- Guilherme
- Gabriel Garcia
- Priscila Maciel
- João Lucas Lira

## Repositório GitHub
🔗 https://github.com/Lukitas20-beep/ProjEngDados

---

# 1. Contextualização do Desafio

O cenário de contratações públicas no Brasil passou por uma transformação significativa com a Lei nº 14.133/2021, que estabeleceu o Portal Nacional de Contratações Públicas (PNCP) como o sítio eletrônico oficial centralizado para a divulgação obrigatória dos atos exigidos pela lei.

Apesar da existência de uma API pública para acesso aos dados, a utilização dessas informações por analistas de mercado, órgãos de controle e cidadãos comuns enfrenta barreiras técnicas severas. O desafio reside em transformar um volume massivo de dados brutos e complexos em informações estruturadas e prontas para análise.

Este projeto surge no contexto da disciplina de Engenharia de Dados, utilizando a metodologia de Aprendizagem Baseada em Projetos (PBL), com o intuito de aplicar conceitos de extração, transformação e carga (ETL) para resolver um problema real de transparência e acesso a dados.

---

# 2. Definição do Problema Central

O problema central identificado é a dificuldade de acesso, limpeza e análise estruturada dos dados de contratações públicas do PNCP.

Embora os dados sejam públicos, eles são disponibilizados em formatos aninhados (JSON complexo) que exigem conhecimento em programação para serem consumidos.

Além disso, a falta de uma interface intuitiva impede que gestores e analistas sem perfil técnico consigam monitorar licitações de forma eficiente e histórica, uma vez que a consulta direta à API não oferece persistência de dados para análises comparativas ao longo do tempo.

---

# 3. Recorte Escolhido pelo Grupo

Para garantir a viabilidade do projeto como um Produto Mínimo Viável (MVP), o grupo estabeleceu o seguinte recorte:

## 3.1 Foco na Modalidade
Extração específica de dados da modalidade **Pregão (código 8)**, por ser uma das mais comuns e relevantes em termos de volume financeiro.

## 3.2 Filtros Essenciais
Delimitação da busca por:
- Unidade da Federação (UF)
- Intervalo de datas
- Paginação controlada

## 3.3 Fluxo Técnico
Implementação de um pipeline ETL modular (POO) que realiza:
- O “achatamento” de objetos aninhados
- Carga em banco NoSQL (**MongoDB Atlas**) para escalabilidade
- Carga em banco relacional (**SQLite**) para auditoria local

## 3.4 Interface
Desenvolvimento de uma interface web via **Streamlit** para permitir que o usuário configure buscas e visualize os resultados sem escrever código.

---

# 4. Principais Dores Percebidas

| Categoria | Descrição da Dor |
|---|---|
| Técnica | Complexidade da API do PNCP e estrutura de dados “aninhada” que dificulta o consumo direto |
| Operacional | Necessidade de repetir consultas manualmente devido à falta de um repositório centralizado de dados tratados |
| Segurança | Riscos associados à gestão de credenciais de acesso a bancos de dados em ambientes de desenvolvimento compartilhado |
| Usabilidade | Ausência de uma ferramenta que permita a visualização rápida e o filtro de licitações para usuários não técnicos |

---

# 5. Possíveis Causas e Consequências do Problema

## 5.1 Causas

1. **Estrutura da API:**  
   O PNCP prioriza a integridade dos dados em formatos complexos, o que eleva a curva de aprendizado para integração.

2. **Volume de Dados:**  
   A enorme quantidade de editais publicados diariamente torna o processamento manual inviável.

3. **Falta de Ferramentas Intermediárias:**  
   Escassez de soluções open-source que façam a ponte entre a API bruta e bancos de dados prontos para análise (Data Warehouses/Data Lakes).

---

## 5.2 Consequências

1. **Baixa Transparência:**  
   Dificuldade para a sociedade civil fiscalizar o uso de recursos públicos de forma ágil.

2. **Perda de Oportunidades:**  
   Empresas (especialmente PMEs) perdem licitações por não conseguirem monitorar o portal de forma eficiente.

3. **Decisões Baseadas em Dados Incompletos:**  
   Gestores públicos podem ter dificuldade em realizar benchmarking de preços e fornecedores devido à fragmentação da informação.

---

# 6. Matriz CSD (Certezas, Suposições e Dúvidas)

| Certezas | Suposições | Dúvidas |
|---|---|---|
| A API do PNCP é a fonte oficial e confiável de dados | A modalidade “Pregão” é a de maior interesse para o público-alvo inicial | Qual o volume máximo de dados que o Streamlit suporta exibir sem perda de performance? |
| O modelo ETL (Extract, Transform, Load) é adequado para o problema | Usuários preferem visualizar os dados em tabelas antes de salvá-los no banco | Como automatizar a extração para que ocorra de forma recorrente (agendada)? |
| A persistência em MongoDB facilita a consulta de dados semiestruturados | A segurança por autenticação de usuário é um requisito crítico para a evolução do produto | Existe um limite de requisições (rate limit) na API do PNCP que possa bloquear o pipeline? |
| O uso de POO torna o código mais fácil de manter e escalar | O “achatamento” dos dados não causa perda de informações vitais para a análise | Como integrar dashboards gráficos (Plotly/Seaborn) de forma intuitiva no MVP? |
