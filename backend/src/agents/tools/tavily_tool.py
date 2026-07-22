"""
Module: tavily_tool
Layer:  Agents (Tools)

A web search fallback tool wrapping the Tavily Search API.
Used when the local knowledge base has insufficient matching context.

Author: Antigravity AI
"""

import httpx
import logging
from src.config import settings

logger = logging.getLogger(__name__)


async def search_tavily(query: str) -> str:
    """
    Queries Tavily Search API for the given search query.
    
    Args:
        query: Natural language query.
        
    Returns:
        Search results summary or direct answer.
    """
    api_key = settings.TAVILY_API_KEY
    if not api_key:
        logger.error("Tavily API key is missing.")
        return "Tavily web search is currently unavailable (API key not configured)."

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True
                },
                timeout=12.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Tavily include_answer gives a consolidated direct answer
            answer = data.get("answer")
            if answer:
                logger.info(f"Tavily search answer retrieved successfully for: '{query}'")
                return answer
                
            # If direct answer is not present, combine top 3 search snippet contents
            results = data.get("results", [])
            snippets = [r.get("content", "") for r in results[:3] if r.get("content")]
            
            if not snippets:
                return "No search results found on the web."
                
            logger.info(f"Tavily combined snippets retrieved successfully for: '{query}'")
            return "\n\n".join(snippets)

        except Exception as e:
            logger.error(f"Tavily search execution failed: {e}")
            raise e
