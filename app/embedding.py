import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

MODEL_NAME = "nlpaueb/legal-bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()

embedding_dim = 768

faiss_index = faiss.IndexFlatL2(embedding_dim)
doc_id_mapping = []

def embed_text(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    if cls_embedding.ndim == 1:
        cls_embedding = np.expand_dims(cls_embedding, axis=0)
    return cls_embedding.astype("float32")

def add_document_embedding(document):
    global faiss_index, doc_id_mapping
    text = document.content
    if not text:
        return
    embedding = embed_text(text)
    faiss_index.add(embedding)
    doc_id_mapping.append(document.id)

def semantic_search_documents(query: str, top_k: int = 5):
    global faiss_index, doc_id_mapping
    query_embedding = embed_text(query)
    distances, indices = faiss_index.search(query_embedding, top_k)
    results = []
    for idx in indices[0]:
        if idx < len(doc_id_mapping):
            results.append(doc_id_mapping[idx])
    return results