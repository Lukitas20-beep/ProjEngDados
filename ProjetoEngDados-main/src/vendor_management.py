import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from src.data_security import restrict_file_permissions
except Exception:  # pragma: no cover
    def restrict_file_permissions(path):
        return None


FORNECEDORES_PADRAO = [
    {
        "nome": "Portal Nacional de Contratações Públicas (PNCP)",
        "categoria": "API pública governamental",
        "tipo": "Serviço externo",
        "finalidade": "Fonte primária de dados de editais e contratações públicas.",
        "dados_processados": "Dados públicos administrativos de contratações públicas.",
        "dados_pessoais": "Baixo no escopo atual; possível presença futura de responsáveis ou contatos.",
        "criticidade": "Alta",
        "risco_principal": "Indisponibilidade, mudança de contrato da API ou retorno inesperado.",
        "mitigacao": "Timeout, retentativas, validação de parâmetros, tratamento de erro e documentação de contingência.",
        "variaveis_ambiente": "",
        "status": "Aprovado para uso acadêmico",
    },
    {
        "nome": "MongoDB Atlas",
        "categoria": "Banco de dados em nuvem",
        "tipo": "Fornecedor de infraestrutura/dados",
        "finalidade": "Persistência dos dados tratados pelo pipeline ETL.",
        "dados_processados": "Registros tratados do PNCP e dados anonimizados quando aplicável.",
        "dados_pessoais": "Baixo a médio; mitigado por anonimização preventiva e variáveis de ambiente.",
        "criticidade": "Alta",
        "risco_principal": "Exposição de credenciais, indisponibilidade ou perda de acesso ao banco.",
        "mitigacao": "Uso de MONGO_URI fora do código, timeout, health check e backup/exportação JSONL.",
        "variaveis_ambiente": "MONGO_URI;MONGO_SERVER_SELECTION_TIMEOUT_MS;MONGO_BACKUP_DATABASE;MONGO_BACKUP_DOCUMENT_LIMIT",
        "status": "Aprovado com controles",
    },
    {
        "nome": "Groq API",
        "categoria": "API de IA generativa/classificação",
        "tipo": "Serviço externo",
        "finalidade": "Classificação CNAE de objetos de licitação.",
        "dados_processados": "Texto do objeto da contratação enviado para classificação.",
        "dados_pessoais": "Baixo no escopo atual; entrada é validada e limitada antes do envio.",
        "criticidade": "Média",
        "risco_principal": "Envio de texto excessivo, indisponibilidade da API ou dependência de fornecedor externo.",
        "mitigacao": "Validação do texto, limite de tamanho, tratamento de erro e possibilidade de seguir sem classificação.",
        "variaveis_ambiente": "GROQ_API_KEY;MAX_CNAE_TEXT_CHARS",
        "status": "Aprovado com ressalvas",
    },
    {
        "nome": "Streamlit",
        "categoria": "Framework de interface",
        "tipo": "Biblioteca open source",
        "finalidade": "Interface web da aplicação acadêmica.",
        "dados_processados": "Dados exibidos em sessão autenticada; informações de usuário e resultados do pipeline.",
        "dados_pessoais": "Dados mínimos de cadastro exibidos ao próprio usuário.",
        "criticidade": "Alta",
        "risco_principal": "Falhas de sessão, exposição indevida de tela ou dependência de versão.",
        "mitigacao": "Controle de sessão, autenticação obrigatória e separação das áreas sensíveis.",
        "variaveis_ambiente": "",
        "status": "Aprovado para uso acadêmico",
    },
    {
        "nome": "Prefect",
        "categoria": "Orquestração de pipeline",
        "tipo": "Biblioteca/serviço de workflow",
        "finalidade": "Execução e organização do fluxo automatizado de extração, transformação e carga.",
        "dados_processados": "Parâmetros do pipeline e registros processados do PNCP.",
        "dados_pessoais": "Baixo no escopo atual.",
        "criticidade": "Média",
        "risco_principal": "Falha de execução automatizada ou configuração externa incompleta.",
        "mitigacao": "Variáveis de ambiente, execução manual pela interface e tratamento de falhas no pipeline.",
        "variaveis_ambiente": "PREFECT_API_URL;PREFECT_API_KEY",
        "status": "Aprovado para uso acadêmico",
    },
    {
        "nome": "Apache Kafka / kafka-python",
        "categoria": "Mensageria",
        "tipo": "Componente de infraestrutura/biblioteca",
        "finalidade": "Suporte a arquitetura de streaming ou comunicação assíncrona no projeto.",
        "dados_processados": "Eventos ou mensagens de pipeline quando a integração for utilizada.",
        "dados_pessoais": "Não aplicável no fluxo principal atual.",
        "criticidade": "Baixa",
        "risco_principal": "Configuração incorreta, indisponibilidade do broker ou acoplamento desnecessário.",
        "mitigacao": "Uso controlado, documentação e manutenção fora do fluxo principal crítico.",
        "variaveis_ambiente": "",
        "status": "Mapeado",
    },
    {
        "nome": "Apache Spark / PySpark",
        "categoria": "Processamento distribuído",
        "tipo": "Biblioteca/plataforma",
        "finalidade": "Processamento alternativo ou escalável dos dados.",
        "dados_processados": "Dados públicos administrativos do PNCP.",
        "dados_pessoais": "Baixo no escopo atual.",
        "criticidade": "Baixa",
        "risco_principal": "Complexidade operacional e dependência de ambiente específico.",
        "mitigacao": "Manter fluxo principal em Streamlit/Python e usar Spark apenas quando necessário.",
        "variaveis_ambiente": "",
        "status": "Mapeado",
    },
    {
        "nome": "Docker / Docker Compose",
        "categoria": "Empacotamento e ambiente",
        "tipo": "Ferramenta de infraestrutura",
        "finalidade": "Padronização de ambiente de execução e serviços auxiliares.",
        "dados_processados": "Configurações do ambiente e serviços do projeto.",
        "dados_pessoais": "Não aplicável diretamente.",
        "criticidade": "Média",
        "risco_principal": "Exposição de variáveis, imagens desatualizadas ou configuração insegura.",
        "mitigacao": "Uso de .env, .gitignore, documentação e revisão de dependências.",
        "variaveis_ambiente": "MONGO_URI;GROQ_API_KEY;PREFECT_API_KEY",
        "status": "Aprovado com controles",
    },
    {
        "nome": "Bibliotecas Python do projeto",
        "categoria": "Dependências open source",
        "tipo": "Pacotes de software",
        "finalidade": "Suporte a requisições, dados, autenticação, banco, IA, orquestração e interface.",
        "dados_processados": "Dados da aplicação conforme cada biblioteca utilizada.",
        "dados_pessoais": "Variável; mitigado por minimização, anonimização e controle de credenciais.",
        "criticidade": "Média",
        "risco_principal": "Vulnerabilidades, duplicidade ou incompatibilidade de versões.",
        "mitigacao": "Inventário, documentação, revisão periódica e fixação de versões quando necessário.",
        "variaveis_ambiente": "",
        "status": "Mapeado",
    },
]

CRITERIOS_AVALIACAO = [
    "Segurança da informação",
    "Privacidade e LGPD",
    "Disponibilidade",
    "Continuidade operacional",
    "Dependência tecnológica",
    "Adequação ao escopo acadêmico",
]

STATUS_AVALIACAO = ["Aprovado", "Aprovado com ressalvas", "Pendente", "Reprovado"]


class VendorManager:
    """Inventário e avaliação simplificada de fornecedores do PNCP Data Engine."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or os.getenv("VENDOR_DB_PATH", "vendors.db"))
        self._criar_tabelas()
        restrict_file_permissions(self.db_path)

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    @staticmethod
    def _agora() -> str:
        return datetime.now().isoformat(timespec="seconds")

    def _criar_tabelas(self) -> None:
        with self._conectar() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS fornecedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    categoria TEXT,
                    tipo TEXT,
                    finalidade TEXT,
                    dados_processados TEXT,
                    dados_pessoais TEXT,
                    criticidade TEXT,
                    risco_principal TEXT,
                    mitigacao TEXT,
                    variaveis_ambiente TEXT,
                    status TEXT,
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS avaliacoes_fornecedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fornecedor_id INTEGER NOT NULL,
                    criterio TEXT NOT NULL,
                    status TEXT NOT NULL,
                    observacao TEXT,
                    avaliado_por TEXT,
                    criado_em TEXT NOT NULL,
                    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
                )
                """
            )
            conn.commit()

    def inicializar_fornecedores_padrao(self) -> None:
        agora = self._agora()
        with self._conectar() as conn:
            for item in FORNECEDORES_PADRAO:
                conn.execute(
                    """
                    INSERT INTO fornecedores (
                        nome, categoria, tipo, finalidade, dados_processados, dados_pessoais,
                        criticidade, risco_principal, mitigacao, variaveis_ambiente, status,
                        criado_em, atualizado_em
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(nome) DO UPDATE SET
                        categoria=excluded.categoria,
                        tipo=excluded.tipo,
                        finalidade=excluded.finalidade,
                        dados_processados=excluded.dados_processados,
                        dados_pessoais=excluded.dados_pessoais,
                        criticidade=excluded.criticidade,
                        risco_principal=excluded.risco_principal,
                        mitigacao=excluded.mitigacao,
                        variaveis_ambiente=excluded.variaveis_ambiente,
                        status=excluded.status,
                        atualizado_em=excluded.atualizado_em
                    """,
                    (
                        item["nome"], item["categoria"], item["tipo"], item["finalidade"],
                        item["dados_processados"], item["dados_pessoais"], item["criticidade"],
                        item["risco_principal"], item["mitigacao"], item["variaveis_ambiente"],
                        item["status"], agora, agora,
                    ),
                )
            conn.commit()

    def listar_fornecedores(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, nome, categoria, tipo, finalidade, dados_processados, dados_pessoais,
                       criticidade, risco_principal, mitigacao, variaveis_ambiente, status,
                       atualizado_em
                FROM fornecedores
                ORDER BY
                    CASE criticidade
                        WHEN 'Alta' THEN 1
                        WHEN 'Média' THEN 2
                        WHEN 'Baixa' THEN 3
                        ELSE 4
                    END,
                    nome
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def obter_fornecedor_por_nome(self, nome: str) -> Optional[Dict[str, Any]]:
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM fornecedores WHERE nome = ?", (nome,)).fetchone()
        return dict(row) if row else None

    def registrar_avaliacao(
        self,
        fornecedor_id: int,
        criterio: str,
        status: str,
        observacao: str = "",
        avaliado_por: str = "",
    ) -> Tuple[bool, str]:
        if criterio not in CRITERIOS_AVALIACAO:
            return False, "Critério de avaliação inválido."
        if status not in STATUS_AVALIACAO:
            return False, "Status de avaliação inválido."

        with self._conectar() as conn:
            existe = conn.execute("SELECT 1 FROM fornecedores WHERE id = ?", (fornecedor_id,)).fetchone()
            if not existe:
                return False, "Fornecedor não encontrado."
            conn.execute(
                """
                INSERT INTO avaliacoes_fornecedores
                (fornecedor_id, criterio, status, observacao, avaliado_por, criado_em)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (fornecedor_id, criterio, status, observacao.strip(), avaliado_por, self._agora()),
            )
            conn.commit()
        return True, "Avaliação de fornecedor registrada com sucesso."

    def listar_avaliacoes(self, limite: int = 100) -> List[Dict[str, Any]]:
        limite = max(1, min(int(limite), 500))
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT a.criado_em, f.nome AS fornecedor, a.criterio, a.status,
                       a.observacao, a.avaliado_por
                FROM avaliacoes_fornecedores a
                JOIN fornecedores f ON f.id = a.fornecedor_id
                ORDER BY a.criado_em DESC
                LIMIT ?
                """,
                (limite,),
            ).fetchall()
        return [dict(row) for row in rows]

    def resumo_riscos(self) -> List[Dict[str, Any]]:
        fornecedores = self.listar_fornecedores()
        resumo: Dict[str, Dict[str, Any]] = {}
        for item in fornecedores:
            criticidade = item.get("criticidade") or "Não classificada"
            bucket = resumo.setdefault(criticidade, {"criticidade": criticidade, "total": 0, "fornecedores": []})
            bucket["total"] += 1
            bucket["fornecedores"].append(item.get("nome"))
        return list(resumo.values())

    def checar_configuracoes_ambiente(self) -> List[Dict[str, Any]]:
        resultado = []
        for item in self.listar_fornecedores():
            variaveis = [v.strip() for v in (item.get("variaveis_ambiente") or "").split(";") if v.strip()]
            if not variaveis:
                resultado.append({
                    "fornecedor": item["nome"],
                    "variavel": "n/a",
                    "configurada": "Não se aplica",
                    "criticidade": item.get("criticidade"),
                })
                continue
            for var in variaveis:
                resultado.append({
                    "fornecedor": item["nome"],
                    "variavel": var,
                    "configurada": "Sim" if bool(os.getenv(var)) else "Não",
                    "criticidade": item.get("criticidade"),
                })
        return resultado

    def exportar_inventario_json(self) -> str:
        payload = {
            "gerado_em": self._agora(),
            "fornecedores": self.listar_fornecedores(),
            "resumo_riscos": self.resumo_riscos(),
            "avaliacoes_recentes": self.listar_avaliacoes(limite=100),
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)
