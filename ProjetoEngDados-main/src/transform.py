from .cnae_classifier import CnaeClassifier

class Transform:
    def __init__(self):
        # Inicializa o classificador de CNAE (carrega o banco de dados na memória uma única vez)
        print("Iniciando camada de Transformação - Carregando base de CNAEs...")
        self.cnae_classifier = CnaeClassifier()

    def processar_contratacoes(self, dados_brutos):
        # A API do PNCP retorna os dados dentro da chave 'data'
        lista = dados_brutos.get("data", [])
        
        dados_tratados = []
        for i, item in enumerate(lista):
            objeto_compra = item.get("objetoCompra", "")
            
            # --- NOVA LÓGICA DE INFERÊNCIA DE CNAE ---
            cnae_info = None
            if objeto_compra:
                # Opcional: print para acompanhar o progresso se a lista for grande
                if (i + 1) % 10 == 0:
                    print(f"Inferindo CNAEs... Processado {i + 1} de {len(lista)}")
                cnae_info = self.cnae_classifier.infer_cnae(objeto_compra)
            # -----------------------------------------

            dados_tratados.append({
                "numero_controle": item.get("numeroControlePNCP"),
                "objeto": objeto_compra,
                "orgao": item.get("orgaoEntidade", {}).get("razaoSocial"),
                "valor": item.get("valorTotalEstimado"),
                "uf": item.get("unidadeOrgao", {}).get("ufSigla"),
                "municipio": item.get("unidadeOrgao", {}).get("municipioNome"),
                "modalidade": item.get("modalidadeNome"),
                "data_abertura": item.get("dataAberturaProposta"),
                # Adicionando os novos campos enriquecidos:
                "cnae_inferido": cnae_info.get("CNAE") if cnae_info else None,
                "cnae_descricao": cnae_info.get("Descricao") if cnae_info else None,
                "cnae_similaridade_confianca": cnae_info.get("Similaridade") if cnae_info else None
            })
        return dados_tratados