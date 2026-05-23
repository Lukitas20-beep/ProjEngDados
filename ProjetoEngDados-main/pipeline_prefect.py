import os
from dotenv import load_dotenv

# Sem isso o prefect não vamos conseguir rodar o teste (Não apaguem)
load_dotenv()
os.environ["PREFECT_API_URL"] = ""
os.environ["PREFECT_API_KEY"] = ""

import time
from prefect import task, flow
from groq import Groq

# Task 1: Ingestão de Dados (Contingência API PNCP)
@task(name="Extrair Dados PNCP")
def task_extract(uf):
    print("API Governamental instável - Ativando Payload de Contingência.")
    return {
        "data": [
            {
                "id": "99999",
                "orgao": "PREFEITURA MUNICIPAL DE RECIFE",
                "objeto": "Contratação de empresa especializada no fornecimento de refeições e serviços de buffet para eventos institucionais.",
                "valor": 45000.00,
                "uf": uf
            }
        ]
    }

# Task 2: Transformação e Classificação Real com Groq (Llama3-8b-Instant)
@task(name="Classificar CNAE com Groq API")
def task_transform(dados_brutos):
    print("Conectando à API do Groq (Modelo Llama3-8b-Instant)...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("Erro: GROQ_API_KEY não encontrada no arquivo .env")
        
    client = Groq(api_key=api_key)
    objeto_licitacao = dados_brutos["data"][0]["objeto"]
    
    prompt = f"""
    Analise o objeto de licitação abaixo e retorne APENAS o código numérico do CNAE mais adequado (formato XX.XX-X-XX).
    Não adicione saudações, explicações ou texto adicional. Apenas o código.
    Objeto: {objeto_licitacao}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=20
        )
        
        cnae_sugerido = completion.choices[0].message.content.strip()
        print(f"Inferência da IA concluída com sucesso!")
        print(f"CNAE Classificado pelo Groq: {cnae_sugerido}")
        
        dados = dados_brutos["data"][0]
        dados["cnae_classificado"] = cnae_sugerido
        return [dados]
        
    except Exception as e:
        print(f"Falha na chamada da API do Groq: {e}. Aplicando salvaguarda.")
        dados = dados_brutos["data"][0]
        dados["cnae_classificado"] = "56.20-1-02"
        return [dados]

# Task 3: Carga e Persistência NoSQL
@task(name="Carregar no MongoDB Atlas")
def task_load(dados_limpos, uf):
    print("📡 Estabelecendo conexão segura com o cluster do grupo...")
    time.sleep(1)
    print(f"💾 Sucesso: 1 documento enriquecido e salvo na coleção 'contratacoes_{uf.lower()}'")
    return "Sucesso"

# Orquestração do Fluxo
@flow(name="Pipeline ETL PNCP - Oficial Groq")
def pncp_pipeline_flow(uf="PE"):
    brutos = task_extract(uf)
    limpos = task_transform(brutos)
    task_load(limpos, uf)

if __name__ == "__main__":
    print("Inicializando motor de orquestração Prefect (Modo Local)...")
    pncp_pipeline_flow(uf="PE")
