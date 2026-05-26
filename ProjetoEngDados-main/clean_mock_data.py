import os
from pymongo import MongoClient
from dotenv import load_dotenv

# só rodar python clean_mock_data.py para limpar o cluster do mongo!

load_dotenv()

def limpar_dados_mock():
    uri = os.getenv("MONGO_URI")
    if not uri:
        print("Erro: MONGO_URI não encontrada no arquivo .env")
        return

    print("Conectando ao MongoDB Atlas...")
    client = MongoClient(uri)
    db = client["projeto_pncp"]
    colecao = db["streaming_contratacoes_pe"]
    
    # Busca por documentos cujo ID comece com 'mock-'
    filtro = {"id": {"$regex": "^mock-"}}
    
    # Opcional: Você também poderia filtrar por órgão
    # filtro = {"orgao": "PREFEITURA MUNICIPAL DE RECIFE"}

    quantidade = colecao.count_documents(filtro)
    if quantidade == 0:
        print("Nenhum dado mockado foi encontrado na coleção.")
        return

    print(f"Foram encontrados {quantidade} registros mockados. Deletando...")
    resultado = colecao.delete_many(filtro)
    
    print(f"Sucesso! {resultado.deleted_count} registros apagados da coleção 'streaming_contratacoes_pe'.")

if __name__ == "__main__":
    limpar_dados_mock()
