import requests


class Extract:
    def __init__(self):
        pass
        
        self.url = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"

    def extract_contratacoes(self, dataFinal, codigoModalidadeContratacao, uf, pagina, tamanhoPagina):

        #Método responsável por acessar a API do PNCP e retornar os dados de contratações


        params = {
            "dataFinal": dataFinal,
            "codigoModalidadeContratacao": codigoModalidadeContratacao,
            "uf": uf,
            "pagina": pagina,
            "tamanhoPagina": tamanhoPagina
        }

        response = requests.get(self.url, params=params)

        response.raise_for_status()

        dados = response.json()

        print(dados)
        
        return dados