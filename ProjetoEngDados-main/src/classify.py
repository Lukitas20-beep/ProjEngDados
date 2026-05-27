from groq import Groq

from src.security import SecurityManager

SYSTEM_PROMPT = (
    "Você é especialista em CNAE (Classificação Nacional de Atividades Econômicas). "
    "Dado o objeto de uma licitação pública, identifique o código CNAE mais adequado. "
    "Responda APENAS no formato: CÓDIGO - DESCRIÇÃO. "
    "Exemplo: 56.20-1-02 - Serviços de buffet."
)


class CnaeClassifier:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def classificar(self, objeto: str) -> dict:
        ok, mensagem, objeto_validado = SecurityManager.validar_texto_cnae(objeto)
        if not ok:
            return {
                "objeto": objeto,
                "cnae_classificado": "N/A",
                "status_ia": mensagem,
            }

        try:
            completion = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Objeto da licitação: {objeto_validado}"},
                ],
                max_tokens=150,
                temperature=0.1,
            )
            return {
                "objeto": objeto_validado,
                "cnae_classificado": completion.choices[0].message.content.strip(),
                "status_ia": "Sucesso",
            }
        except Exception as exc:
            return {
                "objeto": objeto_validado,
                "cnae_classificado": "N/A",
                "status_ia": f"Erro na classificação: {exc}",
            }

    def classificar_lote(self, itens: list[dict], campo_objeto: str = "objeto") -> list[dict]:
        resultado = []
        for item in itens:
            objeto = item.get(campo_objeto, "")
            if objeto:
                classif = self.classificar(objeto)
                resultado.append({**item, "cnae_classificado": classif["cnae_classificado"], "status_ia": classif.get("status_ia", "Sucesso")})
            else:
                resultado.append({**item, "cnae_classificado": "N/A", "status_ia": "Objeto vazio"})
        return resultado
