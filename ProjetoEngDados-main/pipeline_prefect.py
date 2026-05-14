import os
from prefect import task, flow
from src.extract import Extract
from src.transform import Transform
from src.load import Load
from dotenv import load_dotenv

load_dotenv()

# Task 1: Extração com Retry (Timeout)
@task(retries=3, retry_delay_seconds=30, name="Extrair Dados PNCP")
def task_extract(uf, data_ini, data_fim):
    ext = Extract()
    dados = ext.extract_contratacoes(data_ini, data_fim, 8, uf, 1, 10)
    if "error" in dados:
        raise Exception(dados["error"])
    return dados

# Task 2: Transformação
@task(name="Transformar Dados")
def task_transform(dados_brutos):
    tra = Transform()
    return tra.processar_contratacoes(dados_brutos)

# Task 3: Carga no MongoDB
@task(name="Carregar no MongoDB")
def task_load(dados_limpos, uf):
    uri = os.getenv("MONGO_URI")
    loader = Load(uri=uri)
    return loader.salvar_no_mongo(dados_limpos, f"contratacoes_{uf.lower()}", anonimizar=True)

# O Fluxo que orquestra tudo
@flow(name="Pipeline ETL PNCP")
def pncp_pipeline_flow(uf="PE", data_ini="20231201", data_fim="20231201"):
    brutos = task_extract(uf, data_ini, data_fim)
    limpos = task_transform(brutos)
    task_load(limpos, uf)

if __name__ == "__main__":
    # Executa o fluxo localmente
    pncp_pipeline_flow(uf="RR", data_ini="20240101", data_fim="20240101")
