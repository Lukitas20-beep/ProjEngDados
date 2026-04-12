# Pipeline ETL - Portal Nacional de Contratações Públicas (PNCP) 🏛️

## 📌 Descrição do Projeto
Este projeto foi desenvolvido para a disciplina de **Engenharia de Dados**. O objetivo principal é implementar um fluxo completo de **ETL (Extract, Transform, Load)** utilizando a API oficial do PNCP para monitorar e armazenar propostas de licitações.

A solução utiliza **Orientação a Objetos (POO)** para garantir que cada etapa do processo (Extração, Transformação e Carga) seja modular, documentada e fácil de manter.

## 🏗️ Arquitetura da Solução
A arquitetura do pipeline segue a separação de responsabilidades em três camadas fundamentais:

1.  **Extração (Extract):** Consumo de dados brutos da API REST do PNCP utilizando a biblioteca `requests`.
2.  **Transformação (Transform):** Limpeza e normalização dos dados. Objetos aninhados são "achatados" para um formato plano e campos irrelevantes são descartados para otimizar o armazenamento.
3.  **Carga (Load):**
    * **Persistência NoSQL:** Os dados tratados são enviados para um Cluster no **MongoDB Atlas**.
    * **Persistência Relacional:** O pipeline também realiza a carga em um banco de dados local **SQLite** como backup e auditoria.

## 🛠️ Tecnologias e Dependências
* **Linguagem:** Python 3.14+
* **Consumo de API:** `requests` 
* **Banco de Dados Cloud:** `pymongo` e `dnspython` (MongoDB Atlas) 
* **Banco de Dados Local:** `sqlite3`

## 📁 Estrutura do Repositório
```text
.
├── src/                # Módulos de lógica do sistema
│   ├── extract.py      # Classe de consumo da API PNCP
│   ├── transform.py    # Classe de tratamento e limpeza de dados
│   └── load.py         # Classe de conexão com MongoDB e SQLite
├── main.py             # Script orquestrador do pipeline
├── requirements.txt    # Gerenciador de dependências 
├── .gitignore          # Filtro de arquivos (.venv) [cite: 39]
└── README.md           # Documentação técnica do projeto

🚀 Como Executar
Clonar o repositório:

Bash
git clone [https://github.com/Lukitas20-beep/ProjetoEngDados.git](https://github.com/Lukitas20-beep/ProjetoEngDados.git)
Instalar as dependências:
Utilize o arquivo de requirements.txt para configurar o ambiente:

Bash
pip install -r requirements.txt
Configurar a conexão:
No arquivo main.py, insira sua URI de conexão do MongoDB Atlas:

Python
loader = Load(uri="mongodb+srv://lf_db_user:SUA_SENHA_AQUI@cluster0.zxflhho.mongodb.net/?appName=Cluster0")
Executar o Pipeline:

Bash
python main.py


📊 Modelagem dos Dados Tratados
Após o processo de transformação, os dados persistidos seguem a estrutura mapeada abaixo:


numero_controle: Identificador único da contratação no portal.


orgao: Razão social da entidade pública responsável.


objeto: Descrição detalhada do item ou serviço contratado.


valor: Valor total estimado da proposta.


uf / municipio: Localização geográfica da unidade vinculada.


modalidade: Tipo de contratação (ex: Pregão).


data_abertura: Data e hora previstas para a abertura das propostas.



Desenvolvido por: Lucas Ferreira, Isaac Daniel, Arthur Orange, Antônio, Guilherme, Gabriel Garcia
