from src.extract import Extract
from src.transform import Transform  # Nova importação
from src.load import Load

extractor = Extract()
transformer = Transform()
loader = Load(uri="////////////////////////////")

print("Iniciando Extração...")
dados_brutos = extractor.extract_contratacoes(
    dataFinal="20260430", 
    codigoModalidadeContratacao=8, 
    uf="pe", 
    pagina=1, 
    tamanhoPagina=20
)

print("Iniciando Transformação...")
dados_limpos = transformer.processar_contratacoes(dados_brutos)

print("Iniciando Carga...")
loader.salvar_no_mongo(dados_limpos, "contratacoes_pe")

loader.create_sqlite_table(dados_limpos, "contratacoes", "contratacoes_pe")