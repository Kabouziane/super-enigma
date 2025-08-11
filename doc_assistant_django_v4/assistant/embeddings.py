import os, numpy as np
OPENAI_AVAILABLE = False
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

class EmbeddingsProvider:
    def __init__(self, model_name_local='all-MiniLM-L6-v2', openai_model='text-embedding-3-small'):
        self.openai_model = openai_model
        self.model_name_local = model_name_local
        self.use_openai = False
        if os.getenv('OPENAI_API_KEY') and os.getenv('EMBEDDINGS_PROVIDER','openai') == 'openai' and OPENAI_AVAILABLE:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.use_openai = True
        else:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name_local)
    def embed_texts(self, texts):
        if self.use_openai:
            import openai
            all_vecs = []
            B = 64
            for i in range(0, len(texts), B):
                batch = texts[i:i+B]
                res = openai.Embedding.create(model=self.openai_model, input=batch)
                vecs = [r['embedding'] for r in res['data']]
                all_vecs.extend(vecs)
            return np.array(all_vecs, dtype=np.float32)
        else:
            vecs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            return np.array(vecs, dtype=np.float32)
