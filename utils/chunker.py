def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits the input text into overlapping chunks.
    
    Parameters:
        text (str): The complete text to split.
        chunk_size (int): Maximum number of characters in each chunk.
        overlap (int): Number of overlapping characters between consecutive chunks.
    
    Returns:
        List[str]: List of chunked text strings.
    """
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap  # move start with overlap

    return chunks
