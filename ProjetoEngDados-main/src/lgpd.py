import json
import sqlite3
from datetime import datetime
from pathlib import Path

VERSAO_POLITICA_PRIVACIDADE = "1.0"

AVISO_PRIVACIDADE = """
O PNCP Data Engine trata dados pessoais mínimos para autenticação e segurança da aplicação, como nome, e-mail, hash de senha, data de criação do usuário e registros de solicitações de privacidade. Os dados de contratações públicas consultados na API do PNCP possuem natureza predominantemente pública e administrativa, mas a aplicação mantém mecanismos de anonimização preventiva para campos pessoais que possam aparecer em integrações futuras.

Finalidades principais: controlar o acesso à aplicação, proteger as funcionalidades de busca e carga de dados, registrar solicitações relacionadas aos direitos do titular e manter evidências mínimas de conformidade. A aplicação não utiliza os dados de cadastro para publicidade, venda de dados ou compartilhamento comercial com terceiros.

O usuário pode solicitar acesso, correção, informação sobre tratamento, portabilidade, anonimização, bloqueio ou eliminação de dados pessoais, conforme aplicável ao contexto do projeto acadêmico. As solicitações ficam registradas para acompanhamento pela equipe responsável.
""".strip()

OPERACOES_TRATAMENTO = [
    {
        "codigo": "OP01",
        "atividade": "Cadastro de usuários",
        "dados_tratados": "Nome, e-mail, hash de senha, status de aceite da política de privacidade",
        "finalidade": "Identificar usuários autorizados e controlar acesso à aplicação",
        "base_legal": "Execução de contrato/procedimentos preliminares e legítimo interesse em segurança da aplicação",
        "retencao": "Enquanto o usuário estiver ativo no projeto ou até solicitação aplicável de eliminação",
    },
    {
        "codigo": "OP02",
        "atividade": "Autenticação e controle de sessão",
        "dados_tratados": "E-mail, hash de senha e identificador do usuário autenticado",
        "finalidade": "Permitir acesso seguro às funcionalidades internas do PNCP Data Engine",
        "base_legal": "Legítimo interesse e prevenção à fraude/segurança do titular",
        "retencao": "Durante o uso da aplicação e pelo período necessário para segurança operacional",
    },
    {
        "codigo": "OP03",
        "atividade": "Tratamento de dados públicos do PNCP",
        "dados_tratados": "Número de controle, objeto, órgão, valor, UF, município, modalidade e data de abertura",
        "finalidade": "Extrair, transformar, visualizar e persistir dados de contratações públicas",
        "base_legal": "Execução de projeto acadêmico e tratamento de dados públicos de interesse administrativo",
        "retencao": "Enquanto necessário para análise e demonstração do projeto",
    },
    {
        "codigo": "OP04",
        "atividade": "Anonimização preventiva antes da persistência",
        "dados_tratados": "Campos eventualmente identificáveis, como e-mail, documento, telefone, responsável ou senha",
        "finalidade": "Reduzir exposição de dados pessoais em repouso e evitar persistência desnecessária de identificadores",
        "base_legal": "Princípios da necessidade, segurança, prevenção e responsabilização",
        "retencao": "Valores originais não são mantidos quando a anonimização é aplicada",
    },
    {
        "codigo": "OP05",
        "atividade": "Registro de solicitações de titulares",
        "dados_tratados": "Usuário solicitante, tipo de solicitação, descrição, status e datas de criação/atualização",
        "finalidade": "Permitir acompanhamento de pedidos relacionados aos direitos previstos na LGPD",
        "base_legal": "Cumprimento de obrigação legal/regulatória e responsabilização",
        "retencao": "Enquanto necessário para comprovar atendimento e governança do projeto",
    },
]

TIPOS_SOLICITACAO = [
    "Acesso aos dados pessoais",
    "Correção de dados pessoais",
    "Informação sobre tratamento",
    "Anonimização ou bloqueio",
    "Eliminação de dados pessoais",
    "Portabilidade/extração dos dados",
    "Revogação de aceite ou oposição ao tratamento",
]


class LGPDManager:
    def __init__(self, db_path="lgpd_requests.db"):
        self.db_path = Path(db_path)
        self._criar_tabelas()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabelas(self):
        with self._conectar() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS solicitacoes_titular (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    email TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    descricao TEXT,
                    status TEXT NOT NULL DEFAULT 'Recebida',
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS eventos_privacidade (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    email TEXT,
                    evento TEXT NOT NULL,
                    detalhe TEXT,
                    criado_em TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def registrar_solicitacao(self, user_id, email, tipo, descricao=""):
        if tipo not in TIPOS_SOLICITACAO:
            return False, "Tipo de solicitação inválido."

        agora = datetime.now().isoformat(timespec="seconds")
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT INTO solicitacoes_titular
                (user_id, email, tipo, descricao, status, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, email, tipo, descricao.strip(), "Recebida", agora, agora),
            )
            conn.commit()
        return True, "Solicitação registrada com sucesso."

    def listar_solicitacoes_usuario(self, user_id):
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT tipo, descricao, status, criado_em, atualizado_em
                FROM solicitacoes_titular
                WHERE user_id = ?
                ORDER BY criado_em DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def registrar_evento(self, user_id, email, evento, detalhe=""):
        agora = datetime.now().isoformat(timespec="seconds")
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT INTO eventos_privacidade (user_id, email, evento, detalhe, criado_em)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, email, evento, detalhe, agora),
            )
            conn.commit()

    def exportar_registro_tratamento_json(self):
        return json.dumps(OPERACOES_TRATAMENTO, ensure_ascii=False, indent=2)
