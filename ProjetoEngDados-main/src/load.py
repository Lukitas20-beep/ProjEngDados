from pymongo import MongoClient

class Load:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['projeto_pncp']

    def salvar_no_mongo(self, dados, colecao_nome):
        if not dados:
            return "Nenhum dado para salvar."
            
        colecao = self.db[colecao_nome]
        resultado = colecao.insert_many(dados)
        return f"Sucesso! {len(resultado.inserted_ids)} registros salvos."