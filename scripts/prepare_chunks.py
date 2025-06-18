import os
import json
import re
import textwrap
import tiktoken
import pandas as pd

# Folder with discourse JSONs
DISCOURSE_DIR = "data/discourse"
COURSE_DIR = "data/course"

# Output file
OUTPUT_PATH = "data/chunks.json"

# Tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

def clean_text(text):
    # Remove code, links, markdown junk
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)      # Inline/block code
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Markdown links
    text = re.sub(r'https?://\S+', '', text)           # URLs
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text, max_tokens=200):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        tokens = tokenizer.encode(" ".join(current_chunk))
        if len(tokens) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def load_discourse_chunks():
    chunks = []
    for fname in os.listdir(DISCOURSE_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(DISCOURSE_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(data)
                posts = data.get("post_stream", {}).get("posts", [])
                for post in posts:
                    content = clean_text(post.get("cooked", ""))
                    for chunk in chunk_text(content):
                        chunks.append({
                            "source": fname,
                            "type": "discourse",
                            "content": chunk
                        })
    return chunks

def load_course_chunks():
    chunks = []
    for fname in os.listdir(COURSE_DIR):
        if fname.endswith(".md"):
            with open(os.path.join(COURSE_DIR, fname), "r", encoding="utf-8") as f:
                content = clean_text(f.read())
                for chunk in chunk_text(content):
                    chunks.append({
                        "source": fname,
                        "type": "course",
                        "content": chunk
                    })
    return chunks

def main():
    all_chunks = load_discourse_chunks() + load_course_chunks()
    print(f"Total chunks: {len(all_chunks)}")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

if __name__ == "__main__":
    main()
