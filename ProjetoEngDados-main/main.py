from src.extract import Extract
from src.transform import Transform
from src.load import Load
from dotenv import load_dotenv
import os

load_dotenv()

def executar_pipeline(dataFinal, modalidade, uf, pagina, tamanho):
    extractor = Extract()
    transformer = Transform()
    loader = Load(uri=os.getenv("MONGO_URI"))

    print("Iniciando Extração...")
    dados_brutos = extractor.extract_contratacoes(
        dataFinal=dataFinal,
        codigoModalidadeContratacao=modalidade,
        uf=uf,
        pagina=pagina,
        tamanhoPagina=tamanho
    )

    print("Iniciando Transformação...")
    dados_limpos = transformer.processar_contratacoes(dados_brutos)

    return dados_limpos, loader