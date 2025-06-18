from fastapi import FastAPI, Query
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI  # ✅ New client-style usage

from utils.search import load_embeddings, search
from utils.embedder import get_embedding

# Load environment variables
load_dotenv()

# Initialize OpenAI client (new syntax)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()
DATA = load_embeddings("data/embeddings.json")

# Pydantic model for /ask response
class AskResponse(BaseModel):
    query: str
    top_chunks: list

# /ask endpoint to return top matching chunks
@app.get("/ask")
def ask(q: str = Query(..., description="Your question")):
    query_embedding = get_embedding(q)
    if query_embedding is None:
        return {
            "query": q,
            "top_chunks": [],
            "error": "Failed to generate embedding. Please check your OpenAI API key or quota."
        }

    top_chunks = search(query_embedding, DATA, top_k=5)
    return {
        "query": q,
        "top_chunks": [
            {"title": chunk["title"], "text": chunk["text"]}
            for chunk in top_chunks
        ]
    }

# /answer endpoint to generate GPT-style answer from top chunks
@app.get("/answer")
def answer(q: str = Query(..., description="Your question")):
    query_embedding = get_embedding(q)
    if query_embedding is None:
        return {"error": "Could not generate embedding."}

    top_chunks = search(query_embedding, DATA, top_k=5)

    print("🧩 Top Chunks:")
    for chunk in top_chunks:
        print(f" - {chunk['title']}")


    context = "\n\n".join(chunk["text"] for chunk in top_chunks)

    prompt = f"""
You are a virtual teaching assistant for a data science course.
Answer the student's question based only on the context provided.

Context:
{context}

Question:
{q}

Answer:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400
        )
        return {
            "question": q,
            "answer": response.choices[0].message.content.strip()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"status": "Virtual TA API is running"}
