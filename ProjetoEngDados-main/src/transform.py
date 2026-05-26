class Transform:
    def processar_contratacoes(self, dados_brutos):
        # A API do PNCP retorna os dados dentro da chave 'data'
        lista = dados_brutos.get("data", [])

        dados_tratados = []
        for item in lista:
            dados_tratados.append({
                "numero_controle": item.get("numeroControlePNCP"),
                "objeto": item.get("objetoCompra"),
                "orgao": item.get("orgaoEntidade", {}).get("razaoSocial"),
                "valor": item.get("valorTotalEstimado"),
                "uf": item.get("unidadeOrgao", {}).get("ufSigla"),
                "municipio": item.get("unidadeOrgao", {}).get("municipioNome"),
                "modalidade": item.get("modalidadeNome"),
                "data_abertura": item.get("dataAberturaProposta"),
                "fonte_dado": "PNCP - Portal Nacional de Contratações Públicas",
                "contem_dado_pessoal": False,
                "base_legal_tratamento": "Dados públicos administrativos / execução de projeto acadêmico",
            })
        return dados_tratados
