# Pipeline de Engenharia de Dados - Portal Nacional de Contratacoes Publicas (PNCP)

## Descricao do Projeto
Este projeto foi desenvolvido para a disciplina de Engenharia de Dados e Fundamentos de Data Ops. O objetivo principal e implementar uma arquitetura completa de Streaming e Processamento de Dados de ponta a ponta, coletando, enriquecendo e transformando dados de licitacoes do Governo Federal (PNCP).

## Arquitetura da Solucao
O pipeline segue uma arquitetura moderna de microsservicos e streaming, dividida nas seguintes etapas:

1. Ingestao e Orquestracao (Prefect): Coleta de dados da API REST do PNCP e envio para o mensageiro. O Prefect gerencia e agenda essas rotinas. Contem fallback automatico para dados mockados em caso de falha da API.
2. Mensageria e Streaming (Kafka + Zookeeper): Os dados extraidos sao recebidos em tempo real no topico 'pncp_raw_editais', garantindo desacoplamento e escalabilidade.
3. Consumo e Enriquecimento com IA (Python + Groq LLM): Um servico "Consumer" assina o topico do Kafka, processa cada mensagem enviando o texto da licitacao para uma LLM (Llama 3.1 via Groq) afim de classificar o CNAE corretamente, e persiste o resultado.
4. Armazenamento (MongoDB Atlas): Banco de dados NoSQL na nuvem utilizado para armazenar permanentemente os dados brutos ja enriquecidos pela IA.
5. Transformacao Analitica Distribuida (PySpark): Servico responsavel por extrair os dados salvos no MongoDB, normalizar tipos, aplicar regras de negocio (como criar agrupamentos por porte financeiro) e gerar um relatorio tabular relacional formatado. Possui mecanismo de contingencia para demonstracoes caso ocorra timeout no MongoDB.

## Tecnologias e Dependencias
* Linguagem: Python 3.10+
* Infraestrutura e Containerizacao: Docker e Docker Compose (OBRIGATORIO)
* Orquestracao: Prefect Server
* Mensageria: Apache Kafka e Zookeeper
* Processamento Distribuido: Apache Spark (PySpark 3.5.1)
* Banco de Dados: MongoDB Atlas (Driver PyMongo)
* Inteligencia Artificial: Groq API (Llama 3.1)

## Estrutura do Repositorio
```text
.
├── src/                    # Modulos Base e Seguranca
│   ├── auth.py             # Sistema de Autenticacao de usuarios
│   ├── lgpd.py             # Gestao de Privacidade e anonimizacao (LGPD)
│   ├── data_security.py    # Criptografia e seguranca de dados sensiveis
│   ├── classify.py         # Integracao com a LLM para classificacao de CNAE
│   ├── schema.py           # Validacao de qualidade de dados via Pydantic
│   ├── extract.py          # Modulo core de integracao com a API PNCP
│   ├── transform.py        # Modulo core de limpeza em lote (Batch)
│   ├── load.py             # Conectores padronizados para Mongo/SQLite
│   ├── consumer.py         # Consumidor do Kafka (Streaming) e Load no Mongo
│   └── producer.py         # Produtor do Kafka e Validacao de Qualidade
├── app.py                  # Dashboard Interativo Web (Streamlit)
├── pipeline_prefect.py     # Script orquestrador principal de Ingestao (Streaming)
├── transform_pyspark.py    # Script de processamento analitico (PySpark)
├── clean_mock_data.py      # Script administrativo para limpeza do Banco
├── docker-compose.yml      # Manifesto de infraestrutura (Kafka, Zookeeper, etc)
├── Dockerfile              # Build do Consumer Python
├── Dockerfile.spark        # Build do motor PySpark (Java 11 + Python)
├── requirements.txt        # Dependencias unificadas do Python
└── README.md               # Documentacao tecnica do projeto
```

## Modulos Adicionais da Plataforma
Alem do fluxo de Streaming e Processamento Analitico via Docker, este projeto tambem entrega uma **Aplicacao Interativa Batch**:
* **Interface Web (`app.py`):** Um painel interativo feito em Streamlit para operacoes manuais.
* **Conformidade LGPD:** Modulos dedicados a governanca de dados (`lgpd.py` e `data_security.py`).
* **Seguranca:** Controle de acesso nativo mapeado no banco de dados local SQLite (`auth.py`).

## Requisitos Previos
Para executar este projeto, e OBRIGATORIO possuir no ambiente:
* Docker Engine (Em execucao)
* Docker Compose
* Python 3.10+ instalado nativamente (Para rodar os scripts de orquestracao, interface e limpeza)

---

## Como Executar

O projeto foi planejado para ter multiplas frentes funcionais. Qualquer usuario ou desenvolvedor pode testar a arquitetura completa de Streaming e tambem o aplicativo Interativo de Governanca e LGPD. Abaixo esta detalhado como executar cada parte do sistema.

### Fluxo 1: Modo Automatizado de Streaming (Arquitetura Principal)
Este e o fluxo de dados em tempo real, orquestrado e em containers.

**1. Inicializar a Infraestrutura Base (Docker)**
Abra um terminal na raiz do projeto e inicie os servicos (Kafka, Zookeeper, Prefect Server e o Consumer):
```bash
docker-compose up -d
```
A interface web de monitoramento do Prefect estara disponivel em: http://localhost:4200

**2. Disparar a Ingestao de Dados**
Para coletar os dados do Governo (via API ou fallback) e enviar para o Kafka, execute o script no seu terminal local:
```bash
python pipeline_prefect.py
```
> **Dica de Execucao:** Para ver os dados passando pela IA, abra outro terminal e execute `docker-compose logs -f consumer`.

**3. Processamento Analitico Final (PySpark)**
Apos o consumo, os dados estarao no MongoDB. Realize a transformacao final disparando um container isolado para o PySpark:
```bash
docker-compose run --rm spark-job python transform_pyspark.py
```
> **O que isso faz:** O PySpark se conecta ao MongoDB, captura os dados brutos, aplica limpeza e normalizacao em esquema distribuido (incluindo agrupamentos financeiros) e exibe os DataFrames relacionais finais na tela.

### Fluxo 2: Aplicativo Interativo Web (Streamlit & LGPD)
O projeto inclui um front-end interativo com foco em privacidade e operacoes manuais.

**1. Iniciar o Painel Web**
No seu terminal local (pode ser com o Docker desligado), execute:
```bash
streamlit run app.py
```
> **O que isso faz:** Levanta um servidor web em `http://localhost:8501`. Na interface, e possivel simular o fluxo LGPD: criar um usuario padrao, aceitar os termos de uso obrigatorios (gravados via `lgpd.py`), realizar logins de seguranca (`auth.py`) e utilizar filtros para buscar dados da API em Lote.

### Scripts Auxiliares e Administrativos

**Limpeza do Banco de Dados**
Para deletar registros antigos do MongoDB Atlas e preparar o ambiente para uma apresentacao limpa, utilize a ferramenta administrativa:
```bash
python clean_mock_data.py
```
> **O que isso faz:** Conecta via PyMongo no servidor remoto e exclui os registros mockados ou testes gerados em rodadas passadas.

### Encerrar Todo o Ambiente
Quando finalizar a correcao/demonstracao, encerre a arquitetura em nuvem limpando a memoria e rede:
```bash
docker-compose down
```

---

## Documentacao do Projeto
Para uma compreensao mais aprofundada sobre a gestao, metodologia e estrategia do projeto, consulte os documentos detalhados na pasta docs/:

* 01 - Requisitos, MVP e Metodologia PBL
    * Levantamento de Requisitos Integrados (Funcionais e Nao Funcionais).
    * Definicao do Produto Minimo Viavel (MVP).
    * Revisao de Escopo e Matriz de Riscos.
    * Aplicacao da Metodologia de Aprendizagem Baseada em Projetos (PBL).

* 02 - Comunicacao, Feedback e Gestao de Conflitos no Time
    * Melhores praticas para comunicacao eficaz na equipe.
    * Estrategias para feedback construtivo.
    * Tecnicas para gestao proativa de conflitos.

* 03 - Mapeamento de Stakeholders e Tecnicas de Negociacao (PBL)
    * Identificacao e analise dos stakeholders do projeto.
    * Estrategias de engajamento baseadas em poder e interesse.
    * Tecnicas de negociacao aplicadas no contexto PBL.

* 04 - Estrategia de Negocio, UX e Monetizacao
    * Ajuste de fluxos com base em estrategias de negocio potenciais.
    * Revisao de telas-chave (onboarding, paywall, funil de conversao).
    * Levantamento de hipoteses de monetizacao para o projeto.

Desenvolvido por: Lucas Ferreira de Vasconcelos Ribeiro, Luan Martins de Souza, Isaac Daniel Alvares Diniz, Antonio Tenorio Ferreira de Souza, Arthur Orange Vanderlei de Souza, Pedro Andre Falcao de Souza, Priscilla Maciel de Lima, Joao Lucas Santos Lira, Guilherme Chaves Sena
