import io
from PyPDF2 import PdfReader

def is_pdf_bytes(b: bytes) -> bool:
    return b.startswith(b'%PDF')

def extract_pages_from_pdf(path_or_bytes):
    texts = []
    if isinstance(path_or_bytes, (bytes, io.BytesIO)):
        reader = PdfReader(io.BytesIO(path_or_bytes))
    else:
        reader = PdfReader(path_or_bytes)
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or '')
        except Exception:
            texts.append('')
    return texts

def chunk_text(text, chunk_size=1200, overlap=200):
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + chunk_size)
        chunk = text[start:end].strip()
        if chunk: chunks.append(chunk)
        start = end - overlap
        if start < 0: start = 0
    return chunks
