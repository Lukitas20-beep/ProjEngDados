import streamlit as st
import pandas as pd
from src.extract import Extract
from src.transform import Transform
from src.load import Load

st.set_page_config(page_title="PNCP Data Engine", layout="wide")
st.title("🔍 Portal de Compras Públicas (PNCP)")

# Sidebar
with st.sidebar:
    st.header("Configurações de Busca")
    uf = st.text_input("UF", "PE").upper()
    data_ini = st.text_input("Data Inicial", "20231201")
    data_fim = st.text_input("Data Final", "20231201") # Teste com 1 dia só!
    tamanho = st.slider("Qtd. por página", 1, 50, 10)

if "dados_limpos" not in st.session_state:
    st.session_state.dados_limpos = None

if st.button("🚀 Buscar e Processar Dados"):
    ext = Extract()
    tra = Transform()
    with st.spinner("Acessando PNCP..."):
        dados = ext.extract_contratacoes(data_ini, data_fim, 8, uf, 1, tamanho)
    
    if "error" in dados:
        st.error(dados["error"])
    else:
        st.session_state.dados_limpos = tra.processar_contratacoes(dados)
        if st.session_state.dados_limpos:
            st.success("Dados prontos!")
            st.dataframe(pd.DataFrame(st.session_state.dados_limpos))

# Botão de carga (Só aparece se houver dados)
if st.session_state.dados_limpos:
    if st.button("💾 Salvar no MongoDB Atlas"):
        # Sua URI com a senha 1234
        uri = "mongodb+srv://lf_db_user:1234@cluster0.zxflhho.mongodb.net/projeto_pncp?retryWrites=true&w=majority"
        loader = Load(uri=uri)
        msg = loader.salvar_no_mongo(st.session_state.dados_limpos, f"contratacoes_{uf.lower()}")
        st.balloons()
        st.info(msg)