import os

from dotenv import load_dotenv
from prefect import flow, task

from src.classify import CnaeClassifier
from src.extract import Extract
from src.load import Load
from src.transform import Transform

load_dotenv()


@task(retries=3, retry_delay_seconds=5, name="Extrair Dados PNCP")
def task_extract(uf, data_ini, data_fim):
    extractor = Extract()
    dados = extractor.extract_contratacoes(data_ini, data_fim, 8, uf, 1, 10)
    if "error" in dados:
        raise RuntimeError(f"Falha na API PNCP: {dados['error']}")
    return dados


@task(name="Transformar Dados e Classificar CNAE")
def task_transform(dados_brutos):
    transformer = Transform()
    classifier = CnaeClassifier(api_key=os.getenv("GROQ_API_KEY"))

    dados_processados = transformer.processar_contratacoes(dados_brutos)
    return classifier.classificar_lote(dados_processados)


@task(name="Carregar no MongoDB Atlas")
def task_load(dados_limpos, uf):
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI não configurado")
    loader = Load(uri=uri)
    return loader.salvar_no_mongo(dados_limpos, f"contratacoes_{uf.lower()}")


@flow(name="Pipeline ETL PNCP - Oficial")
def pncp_pipeline_flow(uf="PE", data_ini="20240101", data_fim="20240110"):
    brutos = task_extract(uf, data_ini, data_fim)
    limpos = task_transform(brutos)
    task_load(limpos, uf)


if __name__ == "__main__":
    pncp_pipeline_flow(
        uf=os.getenv("PIPELINE_UF", "PE"),
        data_ini=os.getenv("PIPELINE_DATA_INI", "20240101"),
        data_fim=os.getenv("PIPELINE_DATA_FIM", "20240110"),
    )
