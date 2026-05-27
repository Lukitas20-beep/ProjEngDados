import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.data_security import anonymize_records
from src.security import SecurityManager


class Load:
    def __init__(self, uri):
        timeout_ms = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000"))
        self.client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        self.db = self.client["projeto_pncp"]

    def salvar_no_mongo(self, dados, colecao_nome, aplicar_anonimizacao=True):
        if not dados:
            return "Nenhum dado para salvar."

        colecao_segura = SecurityManager.sanitizar_nome_colecao(colecao_nome)
        dados_para_salvar = anonymize_records(dados) if aplicar_anonimizacao else dados

        try:
            colecao = self.db[colecao_segura]
            resultado = colecao.insert_many(dados_para_salvar, ordered=False)
        except PyMongoError as exc:
            return f"Erro ao salvar no MongoDB: {exc}"

        sufixo = " com anonimização aplicada" if aplicar_anonimizacao else " sem anonimização adicional"
        return f"Sucesso! {len(resultado.inserted_ids)} registros salvos{sufixo} na coleção {colecao_segura}."
