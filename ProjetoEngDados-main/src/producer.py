import json
import os
import time
from datetime import datetime
import uuid

from kafka import KafkaProducer
from prefect import flow, task
from pydantic import ValidationError

from src.extract import Extract
from src.schema import ContratacaoSchema

# Configurações do Kafka
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = "pncp_raw_editais"

producer = None

def get_kafka_producer():
    global producer
    if producer is not None:
        return producer
    
    print(f"Tentando conectar ao Kafka em {KAFKA_BROKER}...")
    for _ in range(3):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Conectado ao Kafka com sucesso.")
            return producer
        except Exception as e:
            print(f"Falha ao conectar. Tentando novamente em 3s... Erro: {e}")
            time.sleep(3)
    return None

def mock_pncp_data(uf="PE"):
    print("API Governamental instável - Ativando Payload de Contingência (Mock).")
    mock_id = str(uuid.uuid4())[:8]
    return {
        "data": [
            {
                "id": f"mock-{mock_id}",
                "orgao": "PREFEITURA MUNICIPAL DE RECIFE",
                "objeto": f"Contratação de empresa especializada no fornecimento de refeições e serviços de buffet para eventos institucionais. Lote {mock_id}",
                "valor": 45000.00,
                "uf": uf
            }
        ]
    }

@task(name="Extrair Dados PNCP", retries=1)
def fetch_data():
    ext = Extract()
    hoje = datetime.now().strftime("%Y%m%d")
    
    print(f"Buscando dados na API PNCP para data {hoje}...")
    try:
        dados = ext.extract_contratacoes(
            dataInicial=hoje,
            dataFinal=hoje,
            codigoModalidade=8,
            uf="PE",
            pagina=1,
            tamanhoPagina=5
        )
        if "error" in dados or not dados or "data" not in dados:
            print(f"Falha na API ou retorno vazio: {dados.get('error', 'Sem dados')}")
            return mock_pncp_data("PE")
        return dados
    except Exception as e:
        print(f"Erro ao extrair: {e}")
        return mock_pncp_data("PE")

@task(name="Validar e Publicar no Kafka")
def publish_to_kafka(dados):
    prod = get_kafka_producer()
    if not prod:
        print("Producer Kafka não pôde ser instanciado. O Kafka pode estar fora do ar.")
        return

    registros_publicados = 0
    for item in dados.get("data", []):
        try:
            item_validar = {
                "id": str(item.get("id") or item.get("numero_controle") or uuid.uuid4()),
                "orgao": item.get("orgao", "Desconhecido"),
                "objeto": item.get("objeto", "Sem descrição"),
                "valor": float(item.get("valor", 0.0)),
                "uf": item.get("uf", "XX")
            }
            
            contratacao = ContratacaoSchema(**item_validar)
            prod.send(TOPIC_NAME, contratacao.dict())
            registros_publicados += 1
            print(f"Publicado no Kafka: {contratacao.id} - {contratacao.orgao}")
        
        except ValidationError as e:
            print(f"Erro de Qualidade de Dados (Schema Validation): {e}")
            
    prod.flush()
    print(f"Total de registros publicados neste ciclo: {registros_publicados}")

@flow(name="Streaming Producer PNCP", log_prints=True)
def producer_flow():
    print(f"Iniciando ciclo de extração às {datetime.now()}")
    dados = fetch_data()
    publish_to_kafka(dados)

if __name__ == "__main__":
    producer_flow()
