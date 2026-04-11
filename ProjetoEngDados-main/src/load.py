from pymongo import MongoClient

class Load:
    def __init__(self, uri="/////////////////////////////"):
        self.client = MongoClient(uri)
        self.db = self.client['projeto_pncp']

    def salvar_no_mongo(self, dados, colecao_nome):
        if not dados:
            print("Nenhum dado para salvar.")
            return
            
        colecao = self.db[colecao_nome]
        resultado = colecao.insert_many(dados)
        print(f"Sucesso! {len(resultado.inserted_ids)} registros salvos no MongoDB.")