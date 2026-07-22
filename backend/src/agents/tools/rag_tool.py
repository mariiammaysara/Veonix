"""
Module: rag_tool
Layer:  Agents (Tools)

A local RAG (Retrieval-Augmented Generation) knowledge retrieval tool.
Chunks, embeds, and indexes local nutrition reference markdown files.
Calculates cosine similarity to retrieve relevant knowledge.

Author: Antigravity AI
"""

import os
import glob
import math
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types

from src.config import settings
from src.providers.vision.factory import get_gemini_client

logger = logging.getLogger(__name__)

# Simple in-memory database of chunks and their embedding vectors
# Structure: [{"text": str, "embedding": List[float]}]
_vector_store: List[Dict[str, Any]] = []


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into overlapping chunks using token count (estimated by whitespace).
    
    Args:
        text: Source text string.
        chunk_size: Target token count per chunk.
        overlap: Token overlap between adjacent chunks.
        
    Returns:
        List of text chunks.
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
        
    chunks = []
    start = 0
    while start < len(words):
        # Prevent creating a trailing chunk if the remaining words are fully covered 
        # by the overlap of the previous chunk.
        if start > 0 and len(words) - start <= overlap:
            break
            
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        
        # We choose a 50-token overlap to ensure that semantic context (like sentences 
        # or definitions) crossing chunk boundaries is not lost and is represented in 
        # both adjacent chunks.
        start += chunk_size - overlap
        
    return chunks


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Computes the cosine similarity between two vectors.
    """
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot_product / (norm_a * norm_b)


def _read_markdown_files(doc_paths: List[str]) -> List[str]:
    all_chunks = []
    for path in doc_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                chunks = chunk_text(content, chunk_size=500, overlap=50)
                all_chunks.extend(chunks)
        except Exception as e:
            logger.error(f"Failed to read doc {path}: {e}")
    return all_chunks


async def initialize_vector_store():
    """
    Reads local nutrition markdown files, chunks them, generates embeddings,
    and stores them in the in-memory vector database.
    """
    global _vector_store
    if _vector_store:
        return
        
    client = get_gemini_client()
    
    # Try multiple search paths to handle running from root vs backend folder
    search_paths = [
        os.path.join("data", "nutrition_docs", "*.md"),
        os.path.join("backend", "data", "nutrition_docs", "*.md"),
        os.path.join("..", "backend", "data", "nutrition_docs", "*.md")
    ]
    
    doc_paths = []
    for path_pattern in search_paths:
        matches = glob.glob(path_pattern)
        if matches:
            doc_paths = matches
            break
            
    if not doc_paths:
        logger.warning("No nutrition reference docs found to index.")
        return
        
    import asyncio
    all_chunks = await asyncio.to_thread(_read_markdown_files, doc_paths)
            
    if not all_chunks:
        logger.warning("No document chunks extracted for indexing.")
        return
        
    try:
        # Batch embed all text chunks
        response = await client.aio.models.embed_content(
            model="text-embedding-004",
            contents=all_chunks,
        )
        
        for chunk, emb_obj in zip(all_chunks, response.embeddings):
            _vector_store.append({
                "text": chunk,
                "embedding": emb_obj.values
            })
            
        logger.info(f"Indexed {len(_vector_store)} nutrition reference document chunks.")
    except Exception as e:
        logger.error(f"Failed to generate embeddings during indexing: {e}")
        raise e


async def search_nutrition_knowledge(query: str, threshold: float = 0.6) -> str:
    """
    Searches the local knowledge base for a query.
    Returns the most relevant chunk if similarity exceeds the threshold, otherwise empty string.
    """
    await initialize_vector_store()
    if not _vector_store:
        return ""
        
    client = get_gemini_client()
    try:
        response = await client.aio.models.embed_content(
            model="text-embedding-004",
            contents=query,
        )
        query_embedding = response.embeddings[0].values
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        raise e
        
    best_score = -1.0
    best_chunk = ""
    
    for item in _vector_store:
        score = cosine_similarity(query_embedding, item["embedding"])
        if score > best_score:
            best_score = score
            best_chunk = item["text"]
            
    logger.info(f"RAG search best score: {best_score:.3f} for query: '{query}'")
    if best_score >= threshold:
        return best_chunk
        
    return ""
