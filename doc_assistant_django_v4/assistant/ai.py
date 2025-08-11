import os, uuid, numpy as np, textwrap
from .embeddings import EmbeddingsProvider
from .vectorstore import FaissVectorStore
try:
    from .vectorstore_pinecone import PineconeVectorStore
except Exception:
    PineconeVectorStore = None

from .ingest import extract_pages_from_pdf, chunk_text

EMB_DIM = None
_embedder = None
_store = None

def get_embedder():
    global _embedder, EMB_DIM
    if _embedder is None:
        _embedder = EmbeddingsProvider()
        try:
            if hasattr(_embedder, 'model') and getattr(_embedder.model,'get_sentence_embedding_dimension',None):
                EMB_DIM = _embedder.model.get_sentence_embedding_dimension()
        except Exception:
            EMB_DIM = int(os.getenv('EMB_DIM','1536'))
    return _embedder

def get_store():
    global _store, EMB_DIM
    if _store is None:
        if EMB_DIM is None:
            EMB_DIM = int(os.getenv('EMB_DIM','1536'))
        vectorstore = os.getenv('VECTORSTORE','faiss').lower()
        if vectorstore == 'pinecone':
            if PineconeVectorStore is None:
                raise ImportError('Pinecone support not available; install pinecone-client and set PINECONE_API_KEY')
            _store = PineconeVectorStore()
        else:
            _store = FaissVectorStore(dim=EMB_DIM, index_path=os.getenv('FAISS_INDEX_PATH','./db/faiss.index'), metadata_path=os.getenv('METADATA_PATH','./db/metadata.jsonl'))
    return _store

def ingest_and_index(path_or_bytes, filename, chunk_size=1200, overlap=200):
    embedder = get_embedder()
    store = get_store()
    pages = extract_pages_from_pdf(path_or_bytes)
    texts = []
    metadatas = []
    for p, page_text in enumerate(pages, start=1):
        if not page_text or not page_text.strip(): continue
        chunks = chunk_text(page_text, chunk_size=chunk_size, overlap=overlap)
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({'id': str(uuid.uuid4()), 'filename': filename, 'page': p, 'chunk_index': i, 'text_snippet': chunk[:400].replace('\n',' ')})
    if not texts: return 0
    B = 64
    vecs = []
    for i in range(0, len(texts), B):
        batch = texts[i:i+B]
        v = embedder.embed_texts(batch)
        vecs.append(v)
    vectors = np.vstack(vecs)
    store.add(vectors, metadatas)
    return len(texts)

def answer_query(query, top_k=5):
    embedder = get_embedder()
    store = get_store()
    qv = embedder.embed_texts([query])[0]
    retrieved = store.search(qv, top_k=top_k)
    # build simple answer using top snippet if no OpenAI key
    if os.getenv('OPENAI_API_KEY'):
        try:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            SYSTEM = 'You are an assistant that answers with citations like [filename:page].'
            pieces = [md.get('text_snippet') for _,md in retrieved]
            prompt = SYSTEM + "\n\n" + "\n\n".join(pieces) + "\n\nQuestion: " + query
            resp = openai.ChatCompletion.create(model=os.getenv('OPENAI_CHAT_MODEL','gpt-4'), messages=[{'role':'user','content':prompt}], temperature=0.0, max_tokens=400)
            answer = resp['choices'][0]['message']['content'].strip()
        except Exception as e:
            answer = f'[OpenAI error: {e}]'
    else:
        answer = retrieved[0][1].get('text_snippet') if retrieved else 'No documents found.'
    sources = [{'id':md.get('id'),'filename':md.get('filename'),'page':md.get('page'),'text_snippet':md.get('text_snippet'),'score':score} for score,md in retrieved]
    return {'answer': answer, 'sources': sources}
