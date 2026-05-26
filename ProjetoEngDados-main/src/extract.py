import requests

class Extract:
    def __init__(self):
        # Mudando para o endpoint de editais, que costuma ser mais rápido
        self.url = "https://pncp.gov.br/api/consulta/v1/editais"

    def extract_contratacoes(self, dataInicial, dataFinal, codigoModalidade, uf, pagina, tamanhoPagina):
        params = {
            "dataInicial": dataInicial,
            "dataFinal": dataFinal,
            "codigoModalidadeContratacao": codigoModalidade,
            "uf": uf.upper(),
            "pagina": pagina,
            "tamanhoPagina": tamanhoPagina
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json"
        }

        try:
            # Vamos usar 60 segundos. Se não responder em 1 minuto, a API está offline.
            response = requests.get(self.url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Se der erro, retornamos para o Streamlit mostrar
            return {"error": str(e)}