from pydantic import BaseModel, Field
from typing import Optional

class ContratacaoSchema(BaseModel):
    id: str = Field(description="ID ou numero_controle")
    orgao: str = Field(description="Nome do órgão")
    objeto: str = Field(description="Objeto da contratação")
    valor: float = Field(description="Valor estimado da contratação")
    uf: str = Field(description="Unidade Federativa")
    
    # Campo opcional que será preenchido pelo Consumer via LLM
    cnae_classificado: Optional[str] = None
