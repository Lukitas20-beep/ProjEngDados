import os
import pickle
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

class CnaeClassifier:
    def __init__(self, db_path="data/cnae_database.pkl"):
        # Garante que as variáveis de ambiente (como OPENAI_API_KEY) sejam carregadas
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Carrega o banco de embeddings
        # O caminho precisa ser resolvido a partir da raiz do projeto onde o main.py roda
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_db_path = os.path.join(base_dir, db_path)
        
        if not os.path.exists(full_db_path):
            raise FileNotFoundError(f"Banco de embeddings não encontrado em {full_db_path}. Execute o gerador de embeddings primeiro.")
            
        with open(full_db_path, "rb") as f:
            self.df_database = pickle.load(f)
            
        # Pré-calcula a matriz de embeddings do banco de dados para a memória
        self.cnae_embeddings_matrix = np.vstack(self.df_database['Embedding'].values)

    def get_embedding(self, text):
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Erro ao gerar embedding: {e}")
            return None

    def infer_cnae(self, text, top_k=1):
        """
        Gera a inferência e retorna apenas os dados do melhor CNAE (ou top_k).
        """
        if not text:
            return None

        edital_embedding = self.get_embedding(text)
        if edital_embedding is None:
            return None
            
        edital_embedding_matrix = np.array(edital_embedding).reshape(1, -1)
        similarities = cosine_similarity(edital_embedding_matrix, self.cnae_embeddings_matrix)[0]
        
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'CNAE': self.df_database.iloc[idx]['CNAE'],
                'Ocupacao': self.df_database.iloc[idx]['Ocupacao'],
                'Descricao': self.df_database.iloc[idx]['Descricao'],
                'Similaridade': round(similarities[idx] * 100, 2)
            })
            
        return results[0] if top_k == 1 else results
