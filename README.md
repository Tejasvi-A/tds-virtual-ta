# TDS Virtual Teaching Assistant

This project is a FastAPI-based assistant that answers student questions using:

- Tools in Data Science course content
- Discourse posts from 1st January 2025 to 14th April 2025
- OpenAI GPT (with semantic context via embeddings)

## Endpoints

- `/ask?q=...` — returns most relevant chunks
- `/answer?q=...` — returns GPT-based response using course chunks

## How to Run

1. Clone or unzip the project folder. 
2. Install requirements: pip install -r requirements.txt
3. Add `.env` file: OPENAI_API_KEY="sk-..."
4. Before you run the API server, you must generate the embeddings using: python embed.py
5. Run the server: python -m uvicorn app:app --reload
6. Test it in your browser:
- `http://127.0.0.1:8000/ask?q=What is MapReduce`
- `http://127.0.0.1:8000/answer?q=What is MapReduce`


## Files

- `embed.py` — creates `data/embeddings.json`
- `app.py` — FastAPI app
- `data/` — folder with embeddings
- `utils/` — helper logic
