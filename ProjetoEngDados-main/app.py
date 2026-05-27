import json
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.auth import AuthManager
from src.extract import Extract
from src.lgpd import (
    AVISO_PRIVACIDADE,
    OPERACOES_TRATAMENTO,
    TIPOS_SOLICITACAO,
    VERSAO_POLITICA_PRIVACIDADE,
    LGPDManager,
)
from src.load import Load
from src.security import SecurityManager
from src.transform import Transform

load_dotenv()

st.set_page_config(page_title="PNCP Data Engine", layout="wide")

auth = AuthManager(db_path=os.getenv("USERS_DB_PATH", "users.db"))
lgpd = LGPDManager(db_path=os.getenv("LGPD_DB_PATH", "lgpd_requests.db"))
security = SecurityManager(db_path=os.getenv("SECURITY_DB_PATH", "security_events.db"))

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


def atualizar_usuario_sessao():
    usuario = auth.obter_usuario(st.session_state.usuario_logado["id"])
    if usuario:
        st.session_state.usuario_logado = usuario


# Camada de governança da pipeline. O sistema de autenticação atua como gatekeeper,
# assegurando que apenas usuários autorizados possam disparar a orquestração de dados.
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
            bloqueado, mensagem_bloqueio = security.login_bloqueado(email)
            if bloqueado:
                security.registrar_evento(
                    "login_bloqueado",
                    mensagem_bloqueio,
                    "WARNING",
                    email=email,
                )
                st.error(mensagem_bloqueio)
            else:
                sucesso, usuario, mensagem = auth.autenticar_usuario(email, senha)
                if sucesso:
                    security.registrar_login_sucesso(email, user_id=usuario["id"])
                    st.session_state.usuario_logado = usuario
                    lgpd.registrar_evento(usuario["id"], usuario["email"], "login_realizado")
                    st.success(mensagem)
                    st.rerun()
                else:
                    security.registrar_tentativa_login(email, False, mensagem)
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


def tela_aceite_privacidade():
    usuario = st.session_state.usuario_logado
    aceite_atual = usuario.get("versao_politica_privacidade") == VERSAO_POLITICA_PRIVACIDADE

    if aceite_atual:
        return True

    st.warning("Para acessar a aplicação, leia e aceite o aviso de privacidade da versão atual.")
    st.subheader("Aviso de privacidade e tratamento de dados")
    st.info(AVISO_PRIVACIDADE)

    with st.form("form_aceite_privacidade"):
        aceite = st.checkbox("Li e aceito o aviso de privacidade do PNCP Data Engine.")
        enviar = st.form_submit_button("Aceitar e continuar")

    if enviar:
        if not aceite:
            st.error("É necessário confirmar a leitura e aceite do aviso de privacidade.")
        else:
            sucesso, mensagem = auth.aceitar_politica_privacidade(
                usuario["id"],
                VERSAO_POLITICA_PRIVACIDADE,
            )
            if sucesso:
                lgpd.registrar_evento(
                    usuario["id"],
                    usuario["email"],
                    "politica_privacidade_aceita",
                    f"Versão {VERSAO_POLITICA_PRIVACIDADE}",
                )
                atualizar_usuario_sessao()
                st.success(mensagem)
                st.rerun()
            else:
                st.error(mensagem)

    return False


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
                    lgpd.registrar_evento(
                        st.session_state.usuario_logado["id"],
                        st.session_state.usuario_logado["email"],
                        "senha_alterada",
                    )
                    st.success(mensagem)
                else:
                    st.error(mensagem)


def tela_privacidade_lgpd():
    usuario = st.session_state.usuario_logado

    with st.expander("Privacidade e LGPD"):
        st.subheader("Aviso de privacidade")
        st.write(AVISO_PRIVACIDADE)
        st.caption(f"Versão vigente: {VERSAO_POLITICA_PRIVACIDADE}")

        st.subheader("Registro simplificado das operações de tratamento")
        st.dataframe(pd.DataFrame(OPERACOES_TRATAMENTO), use_container_width=True)

        st.download_button(
            "Baixar registro de tratamento em JSON",
            data=lgpd.exportar_registro_tratamento_json(),
            file_name="registro_tratamento_lgpd.json",
            mime="application/json",
        )

        st.subheader("Meus dados de cadastro")
        dados_usuario = auth.exportar_dados_usuario(usuario["id"])
        st.json(dados_usuario)
        st.download_button(
            "Baixar meus dados em JSON",
            data=json.dumps(dados_usuario, ensure_ascii=False, indent=2),
            file_name="meus_dados_pncp_data_engine.json",
            mime="application/json",
        )

        st.subheader("Solicitações do titular")
        with st.form("form_solicitacao_lgpd"):
            tipo = st.selectbox("Tipo de solicitação", TIPOS_SOLICITACAO)
            descricao = st.text_area("Descrição da solicitação", height=100)
            enviar = st.form_submit_button("Registrar solicitação")

        if enviar:
            sucesso, mensagem = lgpd.registrar_solicitacao(
                usuario["id"],
                usuario["email"],
                tipo,
                descricao,
            )
            if sucesso:
                lgpd.registrar_evento(usuario["id"], usuario["email"], "solicitacao_titular_registrada", tipo)
                st.success(mensagem)
            else:
                st.error(mensagem)

        solicitacoes = lgpd.listar_solicitacoes_usuario(usuario["id"])
        if solicitacoes:
            st.dataframe(pd.DataFrame(solicitacoes), use_container_width=True)
        else:
            st.caption("Nenhuma solicitação registrada para este usuário.")


def tela_seguranca_disponibilidade():
    usuario = st.session_state.usuario_logado

    with st.expander("Segurança e disponibilidade"):
        st.subheader("Controles implementados")
        st.write(
            "A aplicação usa limitação de tentativas de login, bloqueio temporário, "
            "validação de entradas, sanitização de nomes de coleção, timeouts, retentativas "
            "e registros locais de eventos de segurança."
        )

        st.subheader("Parâmetros de segurança")
        st.json({
            "MAX_LOGIN_ATTEMPTS": security.max_login_attempts,
            "LOGIN_LOCKOUT_MINUTES": security.lockout_minutes,
            "MAX_DATE_RANGE_DAYS": os.getenv("MAX_DATE_RANGE_DAYS", "31"),
            "REQUEST_TIMEOUT_SECONDS": os.getenv("REQUEST_TIMEOUT_SECONDS", "20"),
            "REQUEST_MAX_RETRIES": os.getenv("REQUEST_MAX_RETRIES", "3"),
        })

        st.subheader("Saúde do ambiente")
        ambiente = security.checar_ambiente()
        st.dataframe(pd.DataFrame([{"item": k, "status": v} for k, v in ambiente.items()]), use_container_width=True)

        if st.button("Verificar disponibilidade dos serviços", key="btn_healthcheck"):
            ok_pncp, msg_pncp = security.checar_api_pncp()
            ok_mongo, msg_mongo = security.checar_mongodb(os.getenv("MONGO_URI"))

            if ok_pncp:
                st.success(msg_pncp)
            else:
                st.error(msg_pncp)

            if ok_mongo:
                st.success(msg_mongo)
            else:
                st.warning(msg_mongo)

            security.registrar_evento(
                "healthcheck_executado",
                f"PNCP={ok_pncp}; MongoDB={ok_mongo}",
                "INFO",
                user_id=usuario["id"],
                email=usuario["email"],
            )

        st.subheader("Eventos recentes de segurança")
        eventos = security.listar_eventos_recentes(limite=30)
        if eventos:
            st.dataframe(pd.DataFrame(eventos), use_container_width=True)
        else:
            st.caption("Nenhum evento de segurança registrado até o momento.")


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
        aplicar_anonimizacao = st.checkbox("Aplicar anonimização antes de salvar", value=True)
        st.caption("Recomendado para atender aos princípios de minimização, segurança e prevenção.")

        st.divider()
        if st.button("Sair"):
            lgpd.registrar_evento(usuario["id"], usuario["email"], "logout_realizado")
            st.session_state.usuario_logado = None
            st.session_state.dados_limpos = None
            st.rerun()

    tela_alterar_senha()
    tela_privacidade_lgpd()
    tela_seguranca_disponibilidade()

    # Implementação da orquestração da pipeline ETL.
    if st.button("🚀 Buscar e Processar Dados"):
        ok_uf, msg_uf, uf_validada = security.validar_uf(uf)
        ok_datas, msg_datas = security.validar_intervalo_datas(data_ini, data_fim)
        ok_tamanho, msg_tamanho, tamanho_validado = security.validar_tamanho_pagina(tamanho)

        if not ok_uf:
            security.registrar_evento("entrada_invalida", msg_uf, "WARNING", user_id=usuario["id"], email=usuario["email"])
            st.error(msg_uf)
        elif not ok_datas:
            security.registrar_evento("entrada_invalida", msg_datas, "WARNING", user_id=usuario["id"], email=usuario["email"])
            st.error(msg_datas)
        elif not ok_tamanho:
            security.registrar_evento("entrada_invalida", msg_tamanho, "WARNING", user_id=usuario["id"], email=usuario["email"])
            st.error(msg_tamanho)
        else:
            ext = Extract()
            tra = Transform()
            with st.spinner("Acessando PNCP..."):
                dados = ext.extract_contratacoes(data_ini, data_fim, 8, uf_validada, 1, tamanho_validado)

            if "error" in dados:
                security.registrar_evento(
                    "falha_consulta_pncp",
                    dados["error"],
                    "ERROR",
                    user_id=usuario["id"],
                    email=usuario["email"],
                )
                st.error(dados["error"])
            else:
                st.session_state.dados_limpos = tra.processar_contratacoes(dados)
                if st.session_state.dados_limpos:
                    security.registrar_evento(
                        "consulta_pncp_sucesso",
                        f"UF={uf_validada}; registros={len(st.session_state.dados_limpos)}",
                        "INFO",
                        user_id=usuario["id"],
                        email=usuario["email"],
                    )
                    lgpd.registrar_evento(usuario["id"], usuario["email"], "dados_pncp_processados", f"UF={uf_validada}")
                    st.success("Dados prontos!")
                    st.dataframe(pd.DataFrame(st.session_state.dados_limpos))
                else:
                    st.warning("A busca não retornou registros para os filtros informados.")

    # Fase de Carga (Load) da pipeline.
    if st.session_state.dados_limpos:
        if st.button("💾 Salvar no MongoDB Atlas"):
            uri = os.getenv("MONGO_URI")
            if not uri:
                st.error("Configure a variável de ambiente MONGO_URI antes de salvar no MongoDB.")
            else:
                loader = Load(uri=uri)
                colecao_segura = security.sanitizar_nome_colecao(f"contratacoes_{uf.lower()}")
                msg = loader.salvar_no_mongo(
                    st.session_state.dados_limpos,
                    colecao_segura,
                    aplicar_anonimizacao=aplicar_anonimizacao,
                )
                security.registrar_evento(
                    "carga_mongodb_executada",
                    f"Coleção={colecao_segura}; anonimização={aplicar_anonimizacao}",
                    "INFO",
                    user_id=usuario["id"],
                    email=usuario["email"],
                )
                lgpd.registrar_evento(
                    usuario["id"],
                    usuario["email"],
                    "dados_salvos_mongodb",
                    f"Coleção={colecao_segura}, anonimização={aplicar_anonimizacao}",
                )
                st.balloons()
                st.info(msg)


if st.session_state.usuario_logado is None:
    tela_login()
elif tela_aceite_privacidade():
    tela_app()
