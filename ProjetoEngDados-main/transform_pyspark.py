import os
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length, when
from dotenv import load_dotenv

load_dotenv()

def transformar_dados_pyspark():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("Erro: Variável MONGO_URI não encontrada.")
        return

    def gerar_dados_mockados():
        return [
            {
                "id": "mock-001",
                "orgao": "PREFEITURA MUNICIPAL DE RECIFE",
                "objeto": "Aquisicao de computadores para escolas",
                "valor": 150000.0,
                "data_publicacao": "2023-10-01",
                "uf": "PE",
                "cnae_classificado": "47.51-2-01"
            },
            {
                "id": "mock-002",
                "orgao": "GOVERNO DO ESTADO DE PERNAMBUCO",
                "objeto": "Obras de recapeamento asfaltico",
                "valor": 2500000.0,
                "data_publicacao": "2023-10-05",
                "uf": "PE",
                "cnae_classificado": "42.11-1-01"
            }
        ]

    print("Conectando ao MongoDB Atlas para extração dos dados (PyMongo)...")
    
    try:
        import certifi
        client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
        db = client["projeto_pncp"]
        colecao = db["streaming_contratacoes_pe"]
        
        # Tenta extrair
        try:
            dados_brutos = list(colecao.find({}, {"_id": 0}))
        except Exception as mongo_err:
            print(f"Erro de conexão/SSL no Atlas: {mongo_err}")
            dados_brutos = []
            
        if not dados_brutos:
            print("Coleção vazia ou inacessível. Injetando dados mockados para demonstração do PySpark.")
            dados_brutos = gerar_dados_mockados()
            
        print(f"Extraídos {len(dados_brutos)} registros com sucesso!")
        
        print("\nInicializando Engine Analítica (PySpark)...")
        spark = SparkSession.builder \
            .appName("PNCP_Transformacao_Analitica") \
            .getOrCreate()
            
        spark.sparkContext.setLogLevel("ERROR")
        
        # Transforma a lista de dicionários nativa em um Spark DataFrame distribuído
        df = spark.createDataFrame(dados_brutos)
        
        print("\nEstrutura NoSQL Original Encontrada (Schema):")
        df.printSchema()

        if df.count() == 0:
            print("Nenhum dado encontrado na coleção. Deixe o Consumer rodar por mais tempo.")
            return

        print("\nExecutando Pipeline de Transformação Estrutural (PySpark DataFrames)...")
        
        # O DataFrame original possui campos misturados gerados pelo stream (incluindo _id gerado pelo Mongo)
        # Vamos selecionar, renomear e criar colunas condicionalmente para criar uma tabela analítica
        
        df_transformado = df.select(
            col("id").alias("id_licitacao"),
            col("orgao").alias("orgao_comprador"),
            col("objeto"),
            col("valor").cast("double").alias("valor_estimado"),
            col("uf"),
            col("cnae_classificado")
        )
        
        # Regra de negócio fictícia: Criar coluna porte_licitacao baseada no valor
        df_transformado = df_transformado.withColumn(
            "porte_licitacao",
            when(col("valor_estimado") < 50000, "PEQUENO")
            .when((col("valor_estimado") >= 50000) & (col("valor_estimado") <= 500000), "MÉDIO")
            .otherwise("GRANDE")
        )
        
        # Ajustando o tamanho da descrição do objeto para não quebrar a tabela no console
        df_transformado = df_transformado.withColumn(
            "objeto_resumo",
            when(length(col("objeto")) > 30, col("objeto").substr(1, 30))
            .otherwise(col("objeto"))
        )
        
        # Seleção final para a tabela relacional
        df_final = df_transformado.select(
            "id_licitacao", "orgao_comprador", "objeto_resumo", 
            "valor_estimado", "uf", "porte_licitacao", "cnae_classificado"
        )
        
        print("\nRESULTADO FINAL: Dados Convertidos para Formato Tabular Relacional:")
        df_final.show(truncate=False)

        print("\nProcessamento analítico finalizado com sucesso.")

    except Exception as e:
        print(f"\nErro durante o processamento do PySpark: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    transformar_dados_pyspark()
