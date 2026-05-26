import json
import os
import time
from kafka import KafkaConsumer
from groq import Groq

from src.load import Load

# Configurações do Kafka
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = "pncp_raw_editais"
MONGO_URI = os.getenv("MONGO_URI")

def classificar_cnae(objeto_licitacao):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Aviso: GROQ_API_KEY não encontrada. Aplicando CNAE padrão de contingência.")
        return "56.20-1-02"
        
    client = Groq(api_key=api_key)
    prompt = f"""
    Analise o objeto de licitação abaixo e retorne APENAS o código numérico do CNAE mais adequado (formato XX.XX-X-XX).
    Não adicione saudações, explicações ou texto adicional. Apenas o código.
    Objeto: {objeto_licitacao}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=20
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Falha na chamada da API do Groq: {e}. Aplicando CNAE de contingência.")
        return "56.20-1-02"

def main():
    print(f"Consumer iniciando conexao com Kafka em {KAFKA_BROKER}...")
    
    consumer = None
    for _ in range(15):
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=KAFKA_BROKER,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='pncp-consumer-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print("Conectado ao Kafka com sucesso.")
            break
        except Exception as e:
            print(f"Falha ao conectar ao Kafka. Tentando novamente em 5s... Erro: {e}")
            time.sleep(5)
            
    if not consumer:
        print("Erro crítico: Consumer não conseguiu conectar ao Kafka.")
        return

    if not MONGO_URI:
        print("Aviso: MONGO_URI não está definida. Os dados não serão salvos no banco de dados.")

    print("Escutando mensagens do stream...")
    for message in consumer:
        dado_bruto = message.value
        print(f"Mensagem recebida: {dado_bruto['id']} - {dado_bruto['orgao']}")
        
        # Transformação - Enriquecimento via LLM
        cnae = classificar_cnae(dado_bruto['objeto'])
        dado_bruto['cnae_classificado'] = cnae
        
        # Load
        if MONGO_URI:
            try:
                loader = Load(uri=MONGO_URI)
                uf = dado_bruto.get('uf', 'XX').lower()
                # O loader original pede uma lista
                loader.salvar_no_mongo([dado_bruto], f"streaming_contratacoes_{uf}")
                print(f"Registro {dado_bruto['id']} processado e salvo no MongoDB (streaming_contratacoes_{uf})")
            except Exception as e:
                print(f"Erro ao salvar no MongoDB: {e}")
        else:
            print(f"Processado (Simulação): {dado_bruto['id']} | CNAE: {cnae}")

if __name__ == "__main__":
    main()
