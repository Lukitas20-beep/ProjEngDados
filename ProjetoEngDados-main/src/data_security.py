import hashlib
import os
import re
from pathlib import Path

EMAIL_KEYS = {"email", "e_mail", "mail", "correio_eletronico"}
DOCUMENT_KEYS = {"cpf", "cnpj", "documento", "identificacao", "numero_documento"}
PASSWORD_KEYS = {"senha", "password", "passwd", "senha_hash"}
CONTACT_KEYS = {"telefone", "celular", "fone", "whatsapp"}
RESPONSIBLE_KEYS = {"responsavel", "nome_responsavel", "gestor", "fiscal"}


def _salt():
    return os.getenv("ANONYMIZATION_SALT", "pncp-data-engine-salt-local")


def hash_value(value):
    if value is None:
        return None
    raw = f"{_salt()}::{str(value)}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def mask_email(email):
    email = str(email)
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    prefix = local[:2] if len(local) >= 2 else local[:1]
    return f"{prefix}***@{domain}"


def mask_document(value):
    digits = re.sub(r"\D", "", str(value))
    if len(digits) <= 4:
        return "***"
    return f"***{digits[-4:]}"


def anonymize_value(key, value):
    normalized_key = str(key).strip().lower()

    if value in (None, ""):
        return value

    if normalized_key in PASSWORD_KEYS:
        return "[REMOVIDO]"

    if normalized_key in EMAIL_KEYS:
        return {"valor_mascarado": mask_email(value), "hash": hash_value(value)}

    if normalized_key in DOCUMENT_KEYS:
        return {"valor_mascarado": mask_document(value), "hash": hash_value(value)}

    if normalized_key in CONTACT_KEYS or normalized_key in RESPONSIBLE_KEYS:
        return {"hash": hash_value(value)}

    return value


def anonymize_record(record):
    return {key: anonymize_value(key, value) for key, value in record.items()}


def anonymize_records(records):
    return [anonymize_record(record) for record in records]


def restrict_file_permissions(path):
    try:
        Path(path).chmod(0o600)
        return True
    except Exception:
        return False
