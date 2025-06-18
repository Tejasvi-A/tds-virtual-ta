import json
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os

# Load your OpenAI key from environment or paste here
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    openai_api_key = "sk-..."  # Paste your key here if not using env

from openai import OpenAI
client = OpenAI(api_key=openai_api_key)

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def embed_chunks():
    with open("data/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    chroma_client = chromadb.Client(Settings(
        persist_directory="data/chroma",
        anonymized_telemetry=False
    ))

    collection = chroma_client.get_or_create_collection("tds_virtual_ta")

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk["content"]],
            metadatas=[{"source": chunk["source"], "type": chunk["type"]}],
            ids=[f"chunk_{i}"]
        )

    print(f"✅ {len(chunks)} chunks embedded and stored.")

if __name__ == "__main__":
    embed_chunks()
