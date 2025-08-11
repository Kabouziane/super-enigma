import os, json
try:
    import pinecone
except Exception:
    pinecone = None

class PineconeVectorStore:
    def __init__(self, index_name=None, namespace=None):
        if pinecone is None:
            raise ImportError('pinecone-client is required for PineconeVectorStore')
        api_key = os.getenv('PINECONE_API_KEY')
        env = os.getenv('PINECONE_ENV')
        if not api_key or not env:
            raise ValueError('PINECONE_API_KEY and PINECONE_ENV must be set')
        pinecone.init(api_key=api_key, environment=env)
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME')
        if self.index_name not in pinecone.list_indexes():
            # user must create index externally; do not create automatically in prod
            raise ValueError(f'Pinecone index {self.index_name} not found')
        self.index = pinecone.Index(self.index_name)
        self.namespace = namespace or ''

    def add(self, vectors, metadatas):
        # vectors: np.ndarray shape (n,d)
        # metadatas: list of dicts with 'id' key
        to_upsert = []
        for vec, md in zip(vectors.tolist(), metadatas):
            vid = md.get('id')
            to_upsert.append((vid, vec, md))
        self.index.upsert(to_upsert, namespace=self.namespace)

    def search(self, query_vector, top_k=5):
        q = query_vector.tolist() if hasattr(query_vector,'tolist') else query_vector
        res = self.index.query(q, top_k=top_k, include_metadata=True, namespace=self.namespace)
        results = []
        for match in res['matches']:
            score = match['score']
            md = match.get('metadata', {})
            results.append((float(score), md))
        return results

    def save(self):
        # Pinecone is managed; nothing to do locally
        pass
