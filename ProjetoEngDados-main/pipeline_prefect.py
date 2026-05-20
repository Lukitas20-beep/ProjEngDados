import os

from dotenv import load_dotenv
from prefect import flow, task

from src.extract import Extract
from src.load import Load
from src.transform import Transform

load_dotenv()


@task
def extrair(data_ini, data_fim, uf, tamanho):
    return Extract().extract_contratacoes(data_ini, data_fim, 8, uf, 1, tamanho)


@task
def transformar(dados):
    return Transform().processar_contratacoes(dados)


@task
def carregar(dados, uf):
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("Configure a variável MONGO_URI antes de executar a carga.")
    return Load(uri=uri).salvar_no_mongo(dados, f"contratacoes_{uf.lower()}", aplicar_anonimizacao=True)


@flow(name="pncp-data-engine")
def pipeline_pncp(data_ini="20231201", data_fim="20231201", uf="PE", tamanho=10):
    dados = extrair(data_ini, data_fim, uf, tamanho)
    tratados = transformar(dados)
    return carregar(tratados, uf)


if __name__ == "__main__":
    print(pipeline_pncp())
