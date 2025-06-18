import json
import numpy as np

# Load embeddings from file
def load_embeddings(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        emb = item.get("embedding")
        if emb is not None:
            item["embedding"] = np.array(emb)
        else:
            item["embedding"] = None
    return data


# Compute cosine similarity between vectors
def cosine_similarity(a, b):
    if a is None or b is None:
        return -1  # return a very low score if embedding is missing
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return -1
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# Search top-k similar chunks
def search(query_embedding, data, top_k=5, score_threshold=0.65):
    if query_embedding is None:
        return []

    results = []
    for item in data:
        if item["embedding"] is None:
            continue
        score = cosine_similarity(query_embedding, item["embedding"])
        print(f"🔍 Score: {score:.4f} | Title: {item['title']}")
        if score >= score_threshold:
            results.append((score, item))

    results.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in results[:top_k]]



