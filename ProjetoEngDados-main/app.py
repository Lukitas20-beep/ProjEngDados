import os
import subprocess
import threading

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

from src.auth import AuthManager
from src.classify import CnaeClassifier
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

if "anonimizar_dados" not in st.session_state:
    st.session_state.anonimizar_dados = True

# Camada de governança da pipeline. Foi implementado um sistema de autenticação 
# (AuthManager) que atua como um gatekeeper, assegurando que apenas usuários autorizados
#  possam disparar a orquestração de dados e acessar o banco de dados de produção.
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
###################################################################################

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


def _listar_runs_prefect(limit: int = 8):
    api_url = os.getenv("PREFECT_API_URL", "")
    api_key = os.getenv("PREFECT_API_KEY", "")
    if not api_url or not api_key:
        return None, "Configure PREFECT_API_URL e PREFECT_API_KEY no .env"
    try:
        resp = requests.post(
            f"{api_url}/flow_runs/filter",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"limit": limit, "sort": "EXPECTED_START_TIME_DESC"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json(), None
    except Exception as exc:
        return None, str(exc)


def _disparar_pipeline(uf: str, data_ini: str, data_fim: str):
    env = {
        **os.environ,
        "PIPELINE_UF": uf,
        "PIPELINE_DATA_INI": data_ini,
        "PIPELINE_DATA_FIM": data_fim,
    }
    cwd = os.path.dirname(os.path.abspath(__file__))
    threading.Thread(
        target=lambda: subprocess.run(["python", "pipeline_prefect.py"], env=env, cwd=cwd),
        daemon=True,
    ).start()


def aba_busca(uf, data_ini, data_fim, tamanho):
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
                    anonimizar=st.session_state.anonimizar_dados,
                )
                st.balloons()
                st.info(msg)


def aba_classificador():
    st.subheader("Classificador CNAE com IA")
    st.caption("Usa o modelo LLaMA 3 (Groq) para identificar o código CNAE de um objeto de licitação.")

    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        st.error("Variável de ambiente GROQ_API_KEY não configurada.")
        return

    objeto = st.text_area("Objeto da licitação", placeholder="Ex: Contratação de empresa para fornecimento de refeições...")

    if st.button("🤖 Classificar CNAE"):
        if not objeto.strip():
            st.warning("Informe o objeto da licitação.")
        else:
            with st.spinner("Classificando via Groq LLaMA..."):
                classifier = CnaeClassifier(api_key=groq_key)
                resultado = classifier.classificar(objeto)
            st.success("Classificação concluída!")
            st.metric("CNAE Identificado", resultado["cnae_classificado"])

    if st.session_state.dados_limpos:
        st.divider()
        st.subheader("Classificar dados já carregados em lote")
        st.caption(f"{len(st.session_state.dados_limpos)} registros disponíveis na sessão atual.")

        if st.button("🔁 Classificar todos em lote"):
            with st.spinner("Classificando todos os registros via Groq..."):
                classifier = CnaeClassifier(api_key=groq_key)
                dados_classificados = classifier.classificar_lote(st.session_state.dados_limpos)
            st.session_state.dados_limpos = dados_classificados
            st.success("Lote classificado! Dados atualizados na sessão.")
            st.dataframe(pd.DataFrame(dados_classificados))


def aba_pipeline(uf, data_ini, data_fim):
    st.subheader("Pipeline DataOps — Prefect Cloud")

    col1, col2, col3 = st.columns(3)
    with col1:
        ok = bool(os.getenv("PREFECT_API_KEY"))
        st.metric("Prefect Cloud", "✅ Configurado" if ok else "❌ Não configurado")
    with col2:
        ok = bool(os.getenv("GROQ_API_KEY"))
        st.metric("Groq API", "✅ Configurado" if ok else "❌ Não configurado")
    with col3:
        ok = bool(os.getenv("MONGO_URI"))
        st.metric("MongoDB Atlas", "✅ Configurado" if ok else "❌ Não configurado")

    st.divider()
    st.subheader("Disparar Pipeline")
    st.caption("Executa o fluxo Prefect localmente e envia os logs para o Prefect Cloud.")

    col_uf, col_ini, col_fim = st.columns(3)
    pipe_uf = col_uf.text_input("UF", uf, key="pipe_uf")
    pipe_ini = col_ini.text_input("Data Inicial", data_ini, key="pipe_ini")
    pipe_fim = col_fim.text_input("Data Final", data_fim, key="pipe_fim")

    if st.button("▶ Disparar Pipeline"):
        _disparar_pipeline(pipe_uf.upper(), pipe_ini, pipe_fim)
        st.success("Pipeline iniciado em background. Acompanhe o progresso no Prefect Cloud.")

    st.divider()
    st.subheader("Runs Recentes no Prefect Cloud")

    if st.button("🔄 Atualizar Runs"):
        runs, erro = _listar_runs_prefect()
        if erro:
            st.error(erro)
        elif not runs:
            st.info("Nenhum run encontrado.")
        else:
            STATUS_EMOJI = {
                "COMPLETED": "✅",
                "RUNNING": "🔄",
                "FAILED": "❌",
                "CRASHED": "💥",
                "CANCELLED": "⛔",
                "PENDING": "⏳",
                "SCHEDULED": "📅",
            }
            rows = [
                {
                    "Status": f"{STATUS_EMOJI.get(r.get('state_type', ''), '❓')} {r.get('state_type', 'N/A')}",
                    "Nome do Run": r.get("name", "—"),
                    "Início": r.get("start_time", r.get("expected_start_time", "—"))[:19] if r.get("start_time") or r.get("expected_start_time") else "—",
                    "Total de Runs": "",
                }
                for r in runs
            ]
            st.dataframe(pd.DataFrame(rows).drop(columns=["Total de Runs"]), use_container_width=True)


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
        st.session_state.anonimizar_dados = st.checkbox(
            "Aplicar anonimização antes de salvar",
            value=st.session_state.anonimizar_dados,
            help="Mascara ou substitui por hash campos sensíveis identificados antes da persistência."
        )

        st.divider()
        if st.button("Sair"):
            st.session_state.usuario_logado = None
            st.session_state.dados_limpos = None
            st.rerun()

    tela_alterar_senha()

    tab_busca, tab_cnae, tab_pipeline = st.tabs([
        "🔍 Busca PNCP",
        "🤖 Classificador CNAE",
        "🔁 Pipeline DataOps",
    ])

    with tab_busca:
        aba_busca(uf, data_ini, data_fim, tamanho)

    with tab_cnae:
        aba_classificador()

    with tab_pipeline:
        aba_pipeline(uf, data_ini, data_fim)


if st.session_state.usuario_logado is None:
    tela_login()
else:
    tela_app()
