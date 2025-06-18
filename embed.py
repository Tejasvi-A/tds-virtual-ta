import os
import json
import re
from dotenv import load_dotenv
from utils.cleaner import clean_text
from utils.chunker import chunk_text
from utils.embedder import get_embedding


# ✅ Load environment variables
load_dotenv()
os.makedirs("data", exist_ok=True)


INPUT_DIRS = ["data/course", "data/discourse"]
OUTPUT_FILE = "data/embeddings.json"


all_chunks = []


# ✅ Loop through input folders
for directory in INPUT_DIRS:
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)


        if fname.endswith(".md"):
            with open(fpath, encoding="utf-8") as f:
                text = f.read()
            title = fname
            content = clean_text(text)


            # Detect if file is Q&A format like **Q1: ...
            qa_blocks = re.split(r"\*\*Q\d+:", content)
            if len(qa_blocks) > 1:
                for i, block in enumerate(qa_blocks[1:], start=1):
                    qa_text = f"**Q{i}:{block.strip()}"
                    all_chunks.append({
                        "source": fname,
                        "title": title,
                        "chunk_id": i,
                        "text": qa_text
                    })
                continue  # skip normal chunking if Q&A


        elif fname.endswith(".json"):
            with open(fpath, encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    print(f"⚠️ Skipping {fname} — invalid JSON:", e)
                    continue


            if isinstance(data, list):  # Handle array of topic objects
                for topic in data:
                    posts = topic.get("posts", [])
                    if isinstance(posts, list):
                        content = "\n\n".join(p.get("cooked", "") for p in posts if isinstance(p, dict))
                    else:
                        content = str(posts)
                    title = topic.get("title", fname)


                    content = clean_text(content)
                    chunks = chunk_text(content, chunk_size=300, overlap=100)
                    for i, chunk in enumerate(chunks):
                        all_chunks.append({
                            "source": fname,
                            "title": title,
                            "chunk_id": i,
                            "text": chunk
                        })
                continue


            posts = data.get("post_stream", {}).get("posts", [])
            if isinstance(posts, list):
                content = "\n\n".join(p.get("cooked", "") for p in posts if isinstance(p, dict))
            else:
                content = str(posts)
            title = data.get("title", fname)


        else:
            continue  # skip unknown file types


        content = clean_text(content)
        chunks = chunk_text(content, chunk_size=300, overlap=100)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source": fname,
                "title": title,
                "chunk_id": i,
                "text": chunk
            })


print(f"✅ Total chunks created: {len(all_chunks)}")


# ✅ Convert chunks to embeddings
embeddings = []
for i, chunk in enumerate(all_chunks):
    embedding = get_embedding(chunk["text"])


    if embedding is None:
        print(f"⚠️ Skipped chunk {chunk['chunk_id']} in {chunk['title']} — no embedding")
        continue


    embeddings.append({
        "source": chunk["source"],
        "title": chunk["title"],
        "chunk_id": chunk["chunk_id"],
        "text": chunk["text"],
        "embedding": embedding
    })


    if i % 10 == 0:
        print(f"🔹 Embedded {i}/{len(all_chunks)}")


# ✅ Save to output file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(embeddings, f, indent=2, ensure_ascii=False)


print(f"🎉 Done! Saved {len(embeddings)} embeddings to {OUTPUT_FILE}")



