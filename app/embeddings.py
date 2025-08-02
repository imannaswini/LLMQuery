# app/embeddings.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# load sentence-transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# create a FAISS index
embedding_dim = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(embedding_dim)

# store metadata (which file / which text)
metadata = []

def add_text_to_index(text: str, filename: str):
    """Add a document's text to the FAISS index."""
    # split text into chunks
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    if not chunks:
        return
    # compute embeddings
    embeddings = model.encode(chunks)
    index.add(np.array(embeddings, dtype='float32'))
    for c in chunks:
        metadata.append({"filename": filename, "text": c})

def search_text(query: str, top_k: int = 3):
    """Search for similar text in the FAISS index."""
    if index.ntotal == 0:
        return []
    q_embedding = model.encode([query])
    D, I = index.search(np.array(q_embedding, dtype='float32'), k=top_k)
    results = []
    for idx in I[0]:
        if idx < len(metadata):
            results.append(metadata[idx])
    return results
