# utils/embedder.py

from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str, model="text-embedding-ada-002"):
    if not text.strip():
        print("⚠️ Skipped empty text for embedding.")
        return None

    try:
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print("❌ Failed to get embedding:", e)
        return None
