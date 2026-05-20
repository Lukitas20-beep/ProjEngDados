from pymongo import MongoClient

from src.data_security import anonymize_records


class Load:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["projeto_pncp"]

    def salvar_no_mongo(self, dados, colecao_nome, aplicar_anonimizacao=True):
        if not dados:
            return "Nenhum dado para salvar."

        dados_para_salvar = anonymize_records(dados) if aplicar_anonimizacao else dados
        colecao = self.db[colecao_nome]
        resultado = colecao.insert_many(dados_para_salvar)
        sufixo = " com anonimização aplicada" if aplicar_anonimizacao else " sem anonimização adicional"
        return f"Sucesso! {len(resultado.inserted_ids)} registros salvos{sufixo}."
