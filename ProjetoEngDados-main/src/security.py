import os
import re
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

try:
    from src.data_security import restrict_file_permissions
except Exception:  # pragma: no cover
    def restrict_file_permissions(path):
        return None


UF_VALIDAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
}


class SecurityManager:
    """Controles básicos de disponibilidade e proteção contra ataques digitais.

    Esta classe concentra validação de entrada, limitação de tentativas de login,
    registro de eventos de segurança e checagens simples de saúde da aplicação.
    """

    def __init__(
        self,
        db_path: str = "security_events.db",
        max_login_attempts: Optional[int] = None,
        lockout_minutes: Optional[int] = None,
    ):
        self.db_path = Path(db_path)
        self.max_login_attempts = int(max_login_attempts or os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.lockout_minutes = int(lockout_minutes or os.getenv("LOGIN_LOCKOUT_MINUTES", "15"))
        self._criar_tabelas()
        restrict_file_permissions(self.db_path)

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabelas(self) -> None:
        with self._conectar() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    sucesso INTEGER NOT NULL,
                    motivo TEXT,
                    criado_em TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    email TEXT,
                    evento TEXT NOT NULL,
                    detalhe TEXT,
                    severidade TEXT NOT NULL DEFAULT 'INFO',
                    criado_em TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _agora() -> str:
        return datetime.now().isoformat(timespec="seconds")

    def registrar_evento(
        self,
        evento: str,
        detalhe: str = "",
        severidade: str = "INFO",
        user_id: Optional[int] = None,
        email: Optional[str] = None,
    ) -> None:
        severidade = severidade.upper()
        if severidade not in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
            severidade = "INFO"
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT INTO security_events (user_id, email, evento, detalhe, severidade, criado_em)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, self.normalizar_email(email), evento, detalhe, severidade, self._agora()),
            )
            conn.commit()

    @staticmethod
    def normalizar_email(email: Optional[str]) -> str:
        return (email or "").strip().lower()

    def registrar_tentativa_login(self, email: str, sucesso: bool, motivo: str = "") -> None:
        email_normalizado = self.normalizar_email(email)
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT INTO login_attempts (email, sucesso, motivo, criado_em)
                VALUES (?, ?, ?, ?)
                """,
                (email_normalizado, 1 if sucesso else 0, motivo, self._agora()),
            )
            conn.commit()
        if not sucesso:
            self.registrar_evento(
                "login_falhou",
                motivo or "Credenciais inválidas",
                "WARNING",
                email=email_normalizado,
            )

    def tentativas_falhas_recentes(self, email: str) -> int:
        email_normalizado = self.normalizar_email(email)
        limite = (datetime.now() - timedelta(minutes=self.lockout_minutes)).isoformat(timespec="seconds")
        with self._conectar() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*)
                FROM login_attempts
                WHERE email = ? AND sucesso = 0 AND criado_em >= ?
                """,
                (email_normalizado, limite),
            ).fetchone()
        return int(row[0] if row else 0)

    def login_bloqueado(self, email: str) -> Tuple[bool, str]:
        falhas = self.tentativas_falhas_recentes(email)
        if falhas >= self.max_login_attempts:
            return (
                True,
                f"Login temporariamente bloqueado após {falhas} tentativas inválidas. "
                f"Tente novamente em alguns minutos.",
            )
        return False, ""

    def registrar_login_sucesso(self, email: str, user_id: Optional[int] = None) -> None:
        self.registrar_tentativa_login(email, True, "Login bem-sucedido")
        self.registrar_evento("login_sucesso", "Usuário autenticado", "INFO", user_id=user_id, email=email)

    def validar_uf(self, uf: str) -> Tuple[bool, str, Optional[str]]:
        uf_normalizada = (uf or "").strip().upper()
        if uf_normalizada not in UF_VALIDAS:
            return False, "UF inválida. Informe uma sigla válida, como PE, SP ou RJ.", None
        return True, "UF válida.", uf_normalizada

    @staticmethod
    def validar_data_yyyymmdd(valor: str, nome_campo: str) -> Tuple[bool, str, Optional[datetime]]:
        valor = (valor or "").strip()
        if not re.fullmatch(r"\d{8}", valor):
            return False, f"{nome_campo} deve estar no formato AAAAMMDD.", None
        try:
            data = datetime.strptime(valor, "%Y%m%d")
        except ValueError:
            return False, f"{nome_campo} contém uma data inválida.", None
        return True, "Data válida.", data

    def validar_intervalo_datas(self, data_ini: str, data_fim: str, max_dias: Optional[int] = None) -> Tuple[bool, str]:
        max_dias = int(max_dias or os.getenv("MAX_DATE_RANGE_DAYS", "31"))
        ok_ini, msg_ini, dt_ini = self.validar_data_yyyymmdd(data_ini, "Data inicial")
        if not ok_ini:
            return False, msg_ini
        ok_fim, msg_fim, dt_fim = self.validar_data_yyyymmdd(data_fim, "Data final")
        if not ok_fim:
            return False, msg_fim
        if dt_fim < dt_ini:
            return False, "A data final não pode ser anterior à data inicial."
        if (dt_fim - dt_ini).days > max_dias:
            return False, f"O intervalo máximo permitido é de {max_dias} dias."
        return True, "Intervalo de datas válido."

    @staticmethod
    def validar_tamanho_pagina(tamanho: int, limite: Optional[int] = None) -> Tuple[bool, str, int]:
        limite = int(limite or os.getenv("MAX_PAGE_SIZE", "50"))
        try:
            tamanho = int(tamanho)
        except (TypeError, ValueError):
            return False, "Quantidade por página inválida.", 10
        if tamanho < 1 or tamanho > limite:
            return False, f"Quantidade por página deve estar entre 1 e {limite}.", min(max(tamanho, 1), limite)
        return True, "Quantidade por página válida.", tamanho

    @staticmethod
    def sanitizar_nome_colecao(nome: str) -> str:
        nome = (nome or "contratacoes").strip().lower()
        nome = re.sub(r"[^a-z0-9_\-]", "_", nome)
        nome = re.sub(r"_+", "_", nome).strip("_")
        if not nome:
            nome = "contratacoes"
        return nome[:80]

    @staticmethod
    def validar_texto_cnae(texto: str, max_chars: Optional[int] = None) -> Tuple[bool, str, str]:
        max_chars = int(max_chars or os.getenv("MAX_CNAE_TEXT_CHARS", "1000"))
        texto_limpo = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", texto or "").strip()
        texto_limpo = re.sub(r"\s+", " ", texto_limpo)
        if len(texto_limpo) < 5:
            return False, "Texto do objeto muito curto para classificação.", texto_limpo
        if len(texto_limpo) > max_chars:
            texto_limpo = texto_limpo[:max_chars]
        return True, "Texto válido para classificação.", texto_limpo

    def listar_eventos_recentes(self, limite: int = 50) -> list[dict[str, Any]]:
        limite = max(1, min(int(limite), 200))
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT criado_em, severidade, evento, email, detalhe
                FROM security_events
                ORDER BY criado_em DESC
                LIMIT ?
                """,
                (limite,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def checar_ambiente() -> Dict[str, str]:
        checks = {
            "MONGO_URI": "Configurada" if os.getenv("MONGO_URI") else "Ausente",
            "USERS_DB_PATH": os.getenv("USERS_DB_PATH", "users.db"),
            "LGPD_DB_PATH": os.getenv("LGPD_DB_PATH", "lgpd_requests.db"),
            "SECURITY_DB_PATH": os.getenv("SECURITY_DB_PATH", "security_events.db"),
            "ANONYMIZATION_SALT": "Configurado" if os.getenv("ANONYMIZATION_SALT") else "Ausente",
        }
        return checks

    @staticmethod
    def checar_api_pncp(timeout: Optional[int] = None) -> Tuple[bool, str]:
        timeout = int(timeout or os.getenv("PNCP_HEALTH_TIMEOUT_SECONDS", "10"))
        url = "https://pncp.gov.br/api/consulta/v1/editais"
        params = {
            "dataInicial": "20240101",
            "dataFinal": "20240101",
            "codigoModalidadeContratacao": 8,
            "uf": "PE",
            "pagina": 1,
            "tamanhoPagina": 1,
        }
        headers = {"User-Agent": "PNCP-Data-Engine/1.0", "Accept": "application/json"}
        try:
            inicio = time.time()
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            duracao_ms = int((time.time() - inicio) * 1000)
            if response.status_code < 500:
                return True, f"API PNCP respondeu com status {response.status_code} em {duracao_ms} ms."
            return False, f"API PNCP retornou status {response.status_code}."
        except requests.RequestException as exc:
            return False, f"Falha ao consultar API PNCP: {exc}"

    @staticmethod
    def checar_mongodb(uri: Optional[str], timeout_ms: Optional[int] = None) -> Tuple[bool, str]:
        if not uri:
            return False, "MONGO_URI não configurada."
        timeout_ms = int(timeout_ms or os.getenv("MONGO_HEALTH_TIMEOUT_MS", "5000"))
        client = None
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
            client.admin.command("ping")
            return True, "MongoDB respondeu ao ping."
        except (ServerSelectionTimeoutError, PyMongoError, Exception) as exc:
            return False, f"Falha ao conectar ao MongoDB: {exc}"
        finally:
            if client:
                client.close()
