import hashlib
import json
import os
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
except Exception:  # pragma: no cover
    MongoClient = None
    PyMongoError = Exception
    ServerSelectionTimeoutError = Exception

try:
    from src.data_security import restrict_file_permissions
except Exception:  # pragma: no cover
    def restrict_file_permissions(path):
        return None


class BackupManager:
    """Rotinas simples de backup, restauração e continuidade operacional.

    A classe foi criada para o escopo acadêmico do PNCP Data Engine. Ela cobre os
    bancos SQLite locais usados pelas entregas anteriores e, opcionalmente, permite
    exportar uma coleção do MongoDB em JSONL para compor o pacote de backup.
    """

    def __init__(self, backup_dir: Optional[str] = None):
        self.backup_dir = Path(backup_dir or os.getenv("BACKUP_DIR", "backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.backup_dir.chmod(0o700)
        except Exception:
            pass

    @staticmethod
    def _agora() -> str:
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _sqlite_integrity(path: Path) -> Tuple[bool, str]:
        if not path.exists():
            return False, "Arquivo inexistente."
        try:
            with sqlite3.connect(path) as conn:
                row = conn.execute("PRAGMA integrity_check").fetchone()
            status = row[0] if row else "sem resposta"
            return status == "ok", str(status)
        except sqlite3.Error as exc:
            return False, str(exc)

    @staticmethod
    def _default_sqlite_sources() -> Dict[str, Path]:
        configured = {
            "usuarios": os.getenv("USERS_DB_PATH", "users.db"),
            "lgpd": os.getenv("LGPD_DB_PATH", "lgpd_requests.db"),
            "seguranca": os.getenv("SECURITY_DB_PATH", "security_events.db"),
            "contratacoes": os.getenv("CONTRATACOES_DB_PATH", "contratacoes.db"),
        }
        return {name: Path(path) for name, path in configured.items() if path}

    def criar_backup_sqlite(self, incluir_ausentes: bool = True) -> Tuple[Path, Dict[str, Any]]:
        backup_id = self._timestamp()
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=False)

        manifest: Dict[str, Any] = {
            "backup_id": backup_id,
            "criado_em": self._agora(),
            "tipo": "sqlite_local",
            "status": "concluido",
            "arquivos": [],
            "ausentes": [],
            "observacoes": [],
        }

        for nome_logico, origem in self._default_sqlite_sources().items():
            if origem.exists() and origem.is_file():
                destino = backup_path / f"{nome_logico}_{origem.name}"
                shutil.copy2(origem, destino)
                ok_integridade, detalhe_integridade = self._sqlite_integrity(destino)
                manifest["arquivos"].append(
                    {
                        "nome_logico": nome_logico,
                        "origem": str(origem),
                        "arquivo": destino.name,
                        "tamanho_bytes": destino.stat().st_size,
                        "sha256": self._sha256(destino),
                        "integridade_sqlite": ok_integridade,
                        "detalhe_integridade": detalhe_integridade,
                    }
                )
            elif incluir_ausentes:
                manifest["ausentes"].append({"nome_logico": nome_logico, "origem": str(origem)})

        if not manifest["arquivos"]:
            manifest["status"] = "sem_arquivos"
            manifest["observacoes"].append("Nenhum banco SQLite local foi encontrado para backup.")

        self._salvar_manifest(backup_path, manifest)
        zip_path = self._compactar_backup(backup_path)
        return zip_path, manifest

    def exportar_mongodb_jsonl(
        self,
        uri: Optional[str],
        database: str = "projeto_pncp",
        colecao: str = "contratacoes",
        limite: Optional[int] = None,
    ) -> Tuple[bool, str, Optional[Path]]:
        if MongoClient is None:
            return False, "pymongo não está disponível no ambiente.", None
        if not uri:
            return False, "MONGO_URI não configurada.", None

        limite = int(limite or os.getenv("MONGO_BACKUP_DOCUMENT_LIMIT", os.getenv("MONGO_BACKUP_LIMIT", "10000")))
        backup_id = f"mongo_{self._timestamp()}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=False)
        arquivo_jsonl = backup_path / f"{database}_{colecao}.jsonl"

        client = None
        try:
            timeout_ms = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000"))
            client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
            client.admin.command("ping")
            cursor = client[database][colecao].find({}).limit(limite)
            total = 0
            with arquivo_jsonl.open("w", encoding="utf-8") as f:
                for doc in cursor:
                    doc["_id"] = str(doc.get("_id"))
                    f.write(json.dumps(doc, ensure_ascii=False, default=str) + "\n")
                    total += 1

            manifest = {
                "backup_id": backup_id,
                "criado_em": self._agora(),
                "tipo": "mongodb_jsonl",
                "database": database,
                "colecao": colecao,
                "limite": limite,
                "registros_exportados": total,
                "arquivos": [
                    {
                        "arquivo": arquivo_jsonl.name,
                        "tamanho_bytes": arquivo_jsonl.stat().st_size,
                        "sha256": self._sha256(arquivo_jsonl),
                    }
                ],
            }
            self._salvar_manifest(backup_path, manifest)
            zip_path = self._compactar_backup(backup_path)
            return True, f"Exportação MongoDB concluída com {total} registro(s).", zip_path
        except (ServerSelectionTimeoutError, PyMongoError, Exception) as exc:
            return False, f"Falha ao exportar MongoDB: {exc}", None
        finally:
            if client:
                client.close()

    def _salvar_manifest(self, backup_path: Path, manifest: Dict[str, Any]) -> None:
        manifest_path = backup_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        restrict_file_permissions(manifest_path)

    def _compactar_backup(self, backup_path: Path) -> Path:
        zip_path = backup_path.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for file in backup_path.rglob("*"):
                if file.is_file():
                    z.write(file, arcname=file.relative_to(backup_path))
        restrict_file_permissions(zip_path)
        return zip_path

    def listar_backups(self) -> List[Dict[str, Any]]:
        backups = []
        for zip_file in sorted(self.backup_dir.glob("*.zip"), reverse=True):
            item = {
                "arquivo": zip_file.name,
                "caminho": str(zip_file),
                "tamanho_bytes": zip_file.stat().st_size,
                "modificado_em": datetime.fromtimestamp(zip_file.stat().st_mtime).isoformat(timespec="seconds"),
                "manifesto": None,
            }
            try:
                with zipfile.ZipFile(zip_file, "r") as z:
                    if "manifest.json" in z.namelist():
                        item["manifesto"] = json.loads(z.read("manifest.json").decode("utf-8"))
            except Exception as exc:
                item["erro"] = str(exc)
            backups.append(item)
        return backups

    def verificar_backup(self, zip_path: str | Path) -> Tuple[bool, Dict[str, Any]]:
        zip_path = Path(zip_path)
        resultado: Dict[str, Any] = {
            "arquivo": str(zip_path),
            "valido": False,
            "itens": [],
            "erros": [],
        }
        if not zip_path.exists():
            resultado["erros"].append("Arquivo de backup não encontrado.")
            return False, resultado

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                if "manifest.json" not in z.namelist():
                    resultado["erros"].append("Manifesto não encontrado no backup.")
                    return False, resultado
                manifest = json.loads(z.read("manifest.json").decode("utf-8"))
                resultado["manifesto"] = manifest
                for item in manifest.get("arquivos", []):
                    nome_arquivo = item.get("arquivo")
                    esperado = item.get("sha256")
                    if nome_arquivo not in z.namelist():
                        resultado["itens"].append({"arquivo": nome_arquivo, "ok": False, "erro": "ausente"})
                        continue
                    tmp_dir = self.backup_dir / ".verify_tmp"
                    tmp_dir.mkdir(exist_ok=True)
                    tmp_file = tmp_dir / Path(nome_arquivo).name
                    tmp_file.write_bytes(z.read(nome_arquivo))
                    calculado = self._sha256(tmp_file)
                    tmp_file.unlink(missing_ok=True)
                    resultado["itens"].append(
                        {
                            "arquivo": nome_arquivo,
                            "ok": calculado == esperado,
                            "sha256_esperado": esperado,
                            "sha256_calculado": calculado,
                        }
                    )
                resultado["valido"] = all(item.get("ok") for item in resultado["itens"]) and not resultado["erros"]
                return resultado["valido"], resultado
        except zipfile.BadZipFile:
            resultado["erros"].append("Arquivo ZIP inválido ou corrompido.")
            return False, resultado
        except Exception as exc:
            resultado["erros"].append(str(exc))
            return False, resultado

    def restaurar_sqlite(self, zip_path: str | Path, nome_logico: str) -> Tuple[bool, str]:
        destinos = self._default_sqlite_sources()
        if nome_logico not in destinos:
            return False, "Banco lógico inválido para restauração."

        zip_path = Path(zip_path)
        ok, verificacao = self.verificar_backup(zip_path)
        if not ok:
            return False, f"Backup inválido: {verificacao.get('erros') or verificacao.get('itens')}"

        manifest = verificacao.get("manifesto", {})
        entrada = next((item for item in manifest.get("arquivos", []) if item.get("nome_logico") == nome_logico), None)
        if not entrada:
            return False, f"O backup não contém o banco lógico '{nome_logico}'."

        destino = destinos[nome_logico]
        destino.parent.mkdir(parents=True, exist_ok=True)
        safety_copy = None
        if destino.exists():
            safety_copy = destino.with_suffix(destino.suffix + f".antes_restore_{self._timestamp()}")
            shutil.copy2(destino, safety_copy)

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                data = z.read(entrada["arquivo"])
            destino.write_bytes(data)
            ok_integridade, detalhe = self._sqlite_integrity(destino)
            if not ok_integridade:
                if safety_copy and safety_copy.exists():
                    shutil.copy2(safety_copy, destino)
                return False, f"Restauração revertida: integrity_check retornou {detalhe}."
            restrict_file_permissions(destino)
            msg = f"Banco '{nome_logico}' restaurado com sucesso."
            if safety_copy:
                msg += f" Cópia anterior preservada em {safety_copy}."
            return True, msg
        except Exception as exc:
            if safety_copy and safety_copy.exists():
                shutil.copy2(safety_copy, destino)
            return False, f"Falha na restauração: {exc}"

    def aplicar_retencao(self, manter_ultimos: Optional[int] = None, dias: Optional[int] = None) -> Dict[str, Any]:
        manter_ultimos = int(manter_ultimos or os.getenv("BACKUP_RETENTION_COUNT", "10"))
        dias = int(dias or os.getenv("BACKUP_RETENTION_DAYS", "30"))
        limite_data = datetime.now() - timedelta(days=dias)
        backups = sorted(self.backup_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        removidos = []

        for idx, zip_file in enumerate(backups):
            modificado = datetime.fromtimestamp(zip_file.stat().st_mtime)
            if idx >= manter_ultimos or modificado < limite_data:
                try:
                    zip_file.unlink()
                    removidos.append(zip_file.name)
                except Exception:
                    pass

        return {
            "manter_ultimos": manter_ultimos,
            "dias_retencao": dias,
            "removidos": removidos,
            "total_removido": len(removidos),
        }

    def checar_continuidade(self) -> Dict[str, Any]:
        backups = self.listar_backups()
        fontes = self._default_sqlite_sources()
        bancos = []
        for nome, path in fontes.items():
            ok_integridade, detalhe = self._sqlite_integrity(path) if path.exists() else (False, "ausente")
            bancos.append(
                {
                    "nome_logico": nome,
                    "caminho": str(path),
                    "existe": path.exists(),
                    "integridade": ok_integridade,
                    "detalhe": detalhe,
                }
            )

        backup_dir_ok = self.backup_dir.exists() and os.access(self.backup_dir, os.W_OK)
        ultimo_backup = backups[0] if backups else None
        return {
            "backup_dir": str(self.backup_dir),
            "backup_dir_gravavel": backup_dir_ok,
            "total_backups_zip": len(backups),
            "ultimo_backup": ultimo_backup["arquivo"] if ultimo_backup else None,
            "ultimo_backup_em": ultimo_backup["modificado_em"] if ultimo_backup else None,
            "bancos_locais": bancos,
        }
