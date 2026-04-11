class Transform:
    def __init__(self):
        pass

    def processar_contratacoes(self, dados_brutos):
        lista = dados_brutos.get("data", []) if isinstance(dados_brutos, dict) else dados_brutos
        
        dados_tratados = []
        for item in lista:
            dados_tratados.append({
                "numero_controle": item.get("numeroControlePNCP"),
                "objeto": item.get("objetoCompra"),
                "orgao": (item.get("orgaoEntidade") or {}).get("razaoSocial"),
                "valor": item.get("valorTotalEstimado"),
                "uf": (item.get("unidadeOrgao") or {}).get("ufSigla"),
                "municipio": (item.get("unidadeOrgao") or {}).get("municipioNome"),
                "modalidade": item.get("modalidadeNome"),
                "data_abertura": item.get("dataAberturaProposta")
            })
        return dados_tratados