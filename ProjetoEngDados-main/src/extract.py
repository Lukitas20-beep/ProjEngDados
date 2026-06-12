import os
import time
import requests

class Extract:
    def __init__(self, base_url=None, timeout=None, max_retries=None):
        # Recebe a URL por injeção de dependência ou adota o fallback padrão do governo
        self.url = base_url or "https://pncp.gov.br/api/pncp/v1/contratacoes/externas"
        self.timeout = int(timeout or os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
        self.max_retries = int(max_retries or os.getenv("REQUEST_MAX_RETRIES", "3"))

    def extract_contratacoes(self, dataInicial, dataFinal, codigoModalidade, uf, pagina, tamanhoPagina):
        # Parâmetros exatos mapeados para o endpoint real do PNCP externo
        params = {
            "dataInicial": dataInicial,
            "dataFinal": dataFinal,
            "codigoModalidadeContratacao": codigoModalidade,
            "uf": uf.upper(),
            "pagina": pagina,
            "tamanhoPagina": tamanhoPagina,
        }

        headers = {
            "User-Agent": "PNCP-Data-Engine/1.0",
            "Accept": "application/json",
        }

        ultima_excecao = None
        for tentativa in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    self.url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                
                # A API real retorna os resultados diretamente ou encapsulados numa lista
                return response.json()
                
            except requests.Timeout:
                ultima_excecao = f"Tempo limite excedido na tentativa {tentativa}."
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else "desconhecido"
                if status in {400, 401, 403, 404}:
                    return {"error": f"Erro HTTP {status} ao consultar o PNCP."}
                ultima_excecao = f"Erro HTTP {status} na tentativa {tentativa}."
            except requests.RequestException as exc:
                ultima_excecao = f"Falha de conexão na tentativa {tentativa}: {exc}"
            except ValueError as exc:
                return {"error": f"Resposta inválida (JSON corrompido): {exc}"}

            if tentativa < self.max_retries:
                time.sleep(min(2 ** (tentativa - 1), 5))

        return {"error": f"Não foi possível consultar o PNCP após {self.max_retries} tentativa(s). {ultima_excecao}"}
