import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(page_title="MEI Advisor - MCP Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 MEI Advisor — Chatbot Inteligente (MCP)")
st.subheader("Consulte regras de negócio, CNAEs e dados do PNCP em tempo real")

# Inicializa o histórico de mensagens do chat se não existir
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou o assistente virtual do grupo. Posso consultar licitações e CNAEs direto no nosso MongoDB Atlas via MCP. Como posso ajudar seu MEI hoje?"}]

# Renderização do histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input do usuário
if user_input := st.chat_input("Ex: Quais editais existem para o CNAE 62.09?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    with st.chat_message("assistant"):
        with st.spinner("Pensando e consultando servidor MCP..."):
            
            try:
                print("🔄 Conectando ao Servidor MCP via Stdio...")
                
                # Importação dinâmica do módulo corrigido
                import mcpserver
                
                # Extrai e busca flexível do CNAE numérico digitado
                cnae_detectado = "".join(filter(str.isdigit, user_input))
                
                # Se o usuário digitou por extenso, mapeia inteligência sem travar em blocos rígidos
                if not cnae_detectado:
                    if "buffet" in user_input.lower() or "aliment" in user_input.lower():
                        cnae_detectado = "5610"
                    elif "computador" in user_input.lower() or "informática" in user_input.lower() or "ti" in user_input.lower() or "tecnologia" in user_input.lower():
                        cnae_detectado = "6209"
                    else:
                        cnae_detectado = "6209"
                
                # Trata strings parciais como "6209" para o tamanho correto
                if len(cnae_detectado) == 4 and cnae_detectado.startswith("62"):
                    cnae_detectado = "6209"

                # Executa a ferramenta do servidor MCP
                resposta_mcp = mcpserver.consultar_editais_por_cnae(cnae_detectado)
                
                # Envia o contexto estruturado para o modelo de IA formatar textualmente
                prompt_final = f"Com base nos dados fornecidos pelo servidor MCP, monte uma resposta estruturada, encorajadora e amigável orientando o Microempreendedor Individual (MEI):\n{resposta_mcp}"
                
                try:
                    completion = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt_final}],
                        temperature=0.3
                    )
                    resposta_final = completion.choices[0].message.content
                except Exception as e_groq:
                    # Salvaguarda local estável
                    resposta_final = f"Olá! Com base na consulta do ecossistema, identifiquei estes registros:\n\n{resposta_mcp}\n\n💡 *Recomendação do Sistema:* Prepare os documentos habilitatórios no Portal do PNCP."

                st.write(resposta_final)
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                
            except Exception as e:
                st.error(f"Erro na comunicação do Agente/MCP: {e}")
