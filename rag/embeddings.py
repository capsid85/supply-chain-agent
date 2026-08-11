import os
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer

class EmbeddingsSelector:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.model = None

    def get_embeddings(self):
        if self.openai_key:
            try:
                return OpenAIEmbeddings(model="text-embedding-3-small")
            except Exception as e:
                print(f"Failed to load OpenAIEmbeddings: {e}. Falling back to SentenceTransformer.")
        
        # Local fallback using SentenceTransformer
        try:
            if not self.model:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            return self.model
        except Exception as e:
            print(f"Local SentenceTransformer loading failed: {e}. Using dummy embedding model.")
            return DummyEmbeddings()

class DummyEmbeddings:
    def embed_documents(self, texts):
        return [[0.1] * 384 for _ in texts]
    def embed_query(self, text):
        return [0.1] * 384
