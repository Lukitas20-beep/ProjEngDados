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
if user_input := st.chat_input("Ex: Quais editais existem para o CNAE 56.10-1-00?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Inicializa o cliente do Groq com a chave direta
    groq_client = Groq(api_key="ApiGrokKeyInsiraAqui")

    with st.chat_message("assistant"):
        with st.spinner("Pensando e consultando servidor MCP..."):
            
            try:
                print("🔄 Conectando ao Servidor MCP via Stdio...")
                
                # Importação sincrona
                from mcp_server import consultar_editais_por_cnae
                
                # Extrai e busca flexivel CNAE
                cnae_detectado = "".join(filter(str.isdigit, user_input))
                
                #Escrita extensa
                if not cnae_detectado:
                    if "buffet" in user_input.lower() or "aliment" in user_input.lower():
                        cnae_detectado = "56.10"
                    elif "computador" in user_input.lower() or "informática" in user_input.lower() or "ti" in user_input.lower():
                        cnae_detectado = "47.51"
                    else:
                        cnae_detectado = "56.10" 

                # Chamar
                resposta_mcp = consultar_editais_por_cnae(cnae_detectado)
                
                # Groq Formata
                prompt_final = f"Com base nos dados fornecidos pelo servidor MCP, monte uma resposta encorajadora e amigável orientando o Microempreendedor Individual (MEI):\n{resposta_mcp}"
                
                try:
                    completion = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt_final}],
                        temperature=0.3
                    )
                    resposta_final = completion.choices[0].message.content
                except Exception as e_groq:
                    # Salvaguarda local caso a cota do Groq estoure
                    resposta_final = f"Olá! Com base na consulta em tempo real via **Servidor MCP**, localizei estas oportunidades:\n\n{resposta_mcp}\n\n💡 *Recomendação do Sistema:* Prepare os documentos habilitatórios no Portal do PNCP."

                st.write(resposta_final)
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                
            except Exception as e:
                st.error(f"Erro na comunicação do Agente/MCP: {e}")
