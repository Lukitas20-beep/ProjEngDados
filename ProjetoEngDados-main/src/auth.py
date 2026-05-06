import sqlite3
from datetime import datetime
from pathlib import Path

import bcrypt


class AuthManager:
    def __init__(self, db_path="users.db"):
        self.db_path = Path(db_path)
        self._criar_tabela_usuarios()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabela_usuarios(self):
        with self._conectar() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1,
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _gerar_hash_senha(self, senha):
        senha_bytes = senha.encode("utf-8")
        return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")

    def _verificar_hash_senha(self, senha, senha_hash):
        senha_bytes = senha.encode("utf-8")
        hash_bytes = senha_hash.encode("utf-8")
        return bcrypt.checkpw(senha_bytes, hash_bytes)

    def cadastrar_usuario(self, nome, email, senha):
        nome = nome.strip()
        email = email.strip().lower()

        if len(nome) < 2:
            return False, "Informe um nome válido."

        if "@" not in email or "." not in email:
            return False, "Informe um e-mail válido."

        senha_valida, mensagem = self.validar_forca_senha(senha)
        if not senha_valida:
            return False, mensagem

        agora = datetime.now().isoformat(timespec="seconds")
        senha_hash = self._gerar_hash_senha(senha)

        try:
            with self._conectar() as conn:
                conn.execute(
                    """
                    INSERT INTO usuarios (nome, email, senha_hash, criado_em, atualizado_em)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (nome, email, senha_hash, agora, agora),
                )
                conn.commit()
            return True, "Usuário cadastrado com sucesso."
        except sqlite3.IntegrityError:
            return False, "Já existe um usuário cadastrado com este e-mail."

    def autenticar_usuario(self, email, senha):
        email = email.strip().lower()

        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            usuario = conn.execute(
                """
                SELECT id, nome, email, senha_hash, ativo
                FROM usuarios
                WHERE email = ?
                """,
                (email,),
            ).fetchone()

        if usuario is None:
            return False, None, "E-mail ou senha inválidos."

        if usuario["ativo"] != 1:
            return False, None, "Usuário inativo."

        if not self._verificar_hash_senha(senha, usuario["senha_hash"]):
            return False, None, "E-mail ou senha inválidos."

        dados_usuario = {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
        }
        return True, dados_usuario, "Login realizado com sucesso."

    def alterar_senha(self, user_id, senha_atual, nova_senha):
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            usuario = conn.execute(
                "SELECT id, senha_hash FROM usuarios WHERE id = ?",
                (user_id,),
            ).fetchone()

            if usuario is None:
                return False, "Usuário não encontrado."

            if not self._verificar_hash_senha(senha_atual, usuario["senha_hash"]):
                return False, "Senha atual incorreta."

            senha_valida, mensagem = self.validar_forca_senha(nova_senha)
            if not senha_valida:
                return False, mensagem

            agora = datetime.now().isoformat(timespec="seconds")
            nova_senha_hash = self._gerar_hash_senha(nova_senha)

            conn.execute(
                """
                UPDATE usuarios
                SET senha_hash = ?, atualizado_em = ?
                WHERE id = ?
                """,
                (nova_senha_hash, agora, user_id),
            )
            conn.commit()

        return True, "Senha alterada com sucesso."

    def validar_forca_senha(self, senha):
        if len(senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres."
        if not any(char.isupper() for char in senha):
            return False, "A senha deve conter pelo menos uma letra maiúscula."
        if not any(char.islower() for char in senha):
            return False, "A senha deve conter pelo menos uma letra minúscula."
        if not any(char.isdigit() for char in senha):
            return False, "A senha deve conter pelo menos um número."
        return True, "Senha válida."

    def criar_admin_inicial(self, nome, email, senha):
        email = email.strip().lower()
        with self._conectar() as conn:
            existe = conn.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (email,),
            ).fetchone()

        if existe:
            return False, "Usuário administrador já existe."

        return self.cadastrar_usuario(nome, email, senha)
