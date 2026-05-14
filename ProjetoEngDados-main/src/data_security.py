import hashlib
import os
import re
from copy import deepcopy
from pathlib import Path


SENSITIVE_FIELD_PATTERNS = (
    "cpf",
    "email",
    "e_mail",
    "telefone",
    "celular",
    "senha",
    "nome_responsavel",
    "responsavel",
)

DOCUMENT_FIELD_PATTERNS = (
    "cpf",
    "cnpj",
    "documento",
    "identificacao",
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ONLY_DIGITS_RE = re.compile(r"\D+")


def get_anonymization_salt():
    return os.getenv("ANONYMIZATION_SALT", "pncp-data-engine-local-salt")


def hash_value(value, salt=None):
    if value is None:
        return None
    salt = salt or get_anonymization_salt()
    raw = f"{salt}:{str(value).strip().lower()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def mask_email(email):
    if not email:
        return email

    email = str(email).strip().lower()
    if not EMAIL_RE.match(email):
        return "[email_mascarado]"

    local, domain = email.split("@", 1)
    local_mask = f"{local[:2]}***" if len(local) >= 2 else "***"
    domain_parts = domain.split(".")
    domain_name = domain_parts[0]
    suffix = ".".join(domain_parts[1:]) if len(domain_parts) > 1 else ""
    domain_mask = f"{domain_name[:2]}***"

    return f"{local_mask}@{domain_mask}.{suffix}" if suffix else f"{local_mask}@{domain_mask}"


def mask_document(document):
    if document is None:
        return None

    digits = ONLY_DIGITS_RE.sub("", str(document))
    if len(digits) <= 4:
        return "****"

    return f"***{digits[-4:]}"


def is_sensitive_key(key):
    normalized_key = str(key).lower()
    return any(pattern in normalized_key for pattern in SENSITIVE_FIELD_PATTERNS)


def is_document_key(key):
    normalized_key = str(key).lower()
    return any(pattern in normalized_key for pattern in DOCUMENT_FIELD_PATTERNS)


def anonymize_value(key, value):
    if value is None:
        return None

    normalized_key = str(key).lower()

    if "senha" in normalized_key:
        return "[removido]"

    if "email" in normalized_key or "e_mail" in normalized_key:
        return {
            "valor_mascarado": mask_email(value),
            "hash": hash_value(value),
        }

    if is_document_key(key):
        return {
            "valor_mascarado": mask_document(value),
            "hash": hash_value(value),
        }

    if is_sensitive_key(key):
        return hash_value(value)

    return value


def anonymize_record(record):
    if not isinstance(record, dict):
        return record

    anonymized = {}
    for key, value in record.items():
        if isinstance(value, dict):
            anonymized[key] = anonymize_record(value)
        elif isinstance(value, list):
            anonymized[key] = [anonymize_record(item) for item in value]
        else:
            anonymized[key] = anonymize_value(key, value)
    return anonymized


def anonymize_records(records):
    if records is None:
        return []
    return [anonymize_record(deepcopy(record)) for record in records]


def set_private_file_permissions(path):
    """Restricts local database/config files to the current user when the OS supports chmod."""
    file_path = Path(path)
    if not file_path.exists():
        return False

    if os.name == "nt":
        return False

    file_path.chmod(0o600)
    return True


def ensure_local_storage_protection(paths):
    results = {}
    for path in paths:
        results[str(path)] = set_private_file_permissions(path)
    return results
