import os, json, numpy as np
try:
    import faiss
except Exception:
    faiss = None

class FaissVectorStore:
    def __init__(self, dim=384, index_path='./db/faiss.index', metadata_path='./db/metadata.jsonl'):
        self.dim = dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.metadatas = []
        if faiss is None:
            raise ImportError('faiss is required. Install faiss-cpu or faiss-gpu.')
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path,'r',encoding='utf-8') as f:
                        self.metadatas = [json.loads(line) for line in f]
            except Exception as e:
                print('Failed to load FAISS index, creating new one:', e)
                self.index = faiss.IndexFlatIP(self.dim)
        else:
            self.index = faiss.IndexFlatIP(self.dim)
    def _normalize(self, vectors):
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms==0] = 1.0
        return vectors / norms
    def add(self, vectors, metadatas):
        assert vectors.shape[0] == len(metadatas)
        if vectors.dtype != np.float32:
            vectors = vectors.astype('float32')
        vecs = self._normalize(vectors)
        self.index.add(vecs)
        self.metadatas.extend(metadatas)
        self.save()
    def search(self, query_vector, top_k=5):
        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype('float32')
        q = self._normalize(query_vector.reshape(1,-1))
        D, I = self.index.search(q, top_k)
        results = []
        for score, idx in zip(D[0].tolist(), I[0].tolist()):
            if idx < 0 or idx >= len(self.metadatas): continue
            md = self.metadatas[idx].copy()
            results.append((float(score), md))
        return results
    def save(self):
        try:
            faiss.write_index(self.index, self.index_path)
        except Exception as e:
            print('Failed to write faiss index:', e)
        with open(self.metadata_path,'w',encoding='utf-8') as f:
            for md in self.metadatas:
                f.write(json.dumps(md, ensure_ascii=False) + '\n')
