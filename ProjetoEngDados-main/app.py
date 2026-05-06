import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.auth import AuthManager
from src.extract import Extract
from src.load import Load
from src.transform import Transform

load_dotenv()

st.set_page_config(page_title="PNCP Data Engine", layout="wide")

auth = AuthManager(db_path=os.getenv("USERS_DB_PATH", "users.db"))

if os.getenv("ADMIN_EMAIL") and os.getenv("ADMIN_PASSWORD"):
    auth.criar_admin_inicial(
        nome=os.getenv("ADMIN_NAME", "Administrador"),
        email=os.getenv("ADMIN_EMAIL"),
        senha=os.getenv("ADMIN_PASSWORD"),
    )

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "dados_limpos" not in st.session_state:
    st.session_state.dados_limpos = None


def tela_login():
    st.title("🔐 Acesso ao PNCP Data Engine")
    st.caption("Entre com seu usuário para acessar a busca, o processamento e a carga dos dados.")

    aba_login, aba_cadastro = st.tabs(["Entrar", "Criar usuário"])

    with aba_login:
        with st.form("form_login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            enviar = st.form_submit_button("Entrar")

        if enviar:
            sucesso, usuario, mensagem = auth.autenticar_usuario(email, senha)
            if sucesso:
                st.session_state.usuario_logado = usuario
                st.success(mensagem)
                st.rerun()
            else:
                st.error(mensagem)

    with aba_cadastro:
        with st.form("form_cadastro"):
            nome = st.text_input("Nome")
            novo_email = st.text_input("E-mail", key="cadastro_email")
            nova_senha = st.text_input("Senha", type="password", key="cadastro_senha")
            confirmar_senha = st.text_input("Confirmar senha", type="password")
            cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            if nova_senha != confirmar_senha:
                st.error("As senhas informadas não conferem.")
            else:
                sucesso, mensagem = auth.cadastrar_usuario(nome, novo_email, nova_senha)
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)


def tela_alterar_senha():
    with st.expander("Alterar senha"):
        with st.form("form_alterar_senha"):
            senha_atual = st.text_input("Senha atual", type="password")
            nova_senha = st.text_input("Nova senha", type="password")
            confirmar_nova_senha = st.text_input("Confirmar nova senha", type="password")
            alterar = st.form_submit_button("Salvar nova senha")

        if alterar:
            if nova_senha != confirmar_nova_senha:
                st.error("As senhas informadas não conferem.")
            else:
                sucesso, mensagem = auth.alterar_senha(
                    st.session_state.usuario_logado["id"],
                    senha_atual,
                    nova_senha,
                )
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)


def tela_app():
    usuario = st.session_state.usuario_logado

    st.title("🔍 Portal de Compras Públicas (PNCP)")
    st.caption(f"Usuário autenticado: {usuario['nome']} ({usuario['email']})")

    with st.sidebar:
        st.header("Configurações de Busca")
        uf = st.text_input("UF", "PE").upper()
        data_ini = st.text_input("Data Inicial", "20231201")
        data_fim = st.text_input("Data Final", "20231201")
        tamanho = st.slider("Qtd. por página", 1, 50, 10)

        st.divider()
        if st.button("Sair"):
            st.session_state.usuario_logado = None
            st.session_state.dados_limpos = None
            st.rerun()

    tela_alterar_senha()

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
            else:
                st.warning("A busca não retornou registros para os filtros informados.")

    if st.session_state.dados_limpos:
        if st.button("💾 Salvar no MongoDB Atlas"):
            uri = os.getenv("MONGO_URI")
            if not uri:
                st.error("Configure a variável de ambiente MONGO_URI antes de salvar no MongoDB.")
            else:
                loader = Load(uri=uri)
                msg = loader.salvar_no_mongo(
                    st.session_state.dados_limpos,
                    f"contratacoes_{uf.lower()}",
                )
                st.balloons()
                st.info(msg)


if st.session_state.usuario_logado is None:
    tela_login()
else:
    tela_app()
