
import os
import logging
from openai import AsyncOpenAI, APIStatusError
import asyncio
from fastapi import HTTPException
from typing import Optional

from app.core.config import get_settings

# Setup logging
logger = logging.getLogger(__name__)

# Constants
PRIMARY_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic"
FALLBACK_MODEL = "llava-hf/llava-v1.6-mistral-7b-hf"
BASE_URL = "https://router.huggingface.co/v1"

def get_client() -> AsyncOpenAI:
    """Get the AsyncOpenAI client configured for Hugging Face."""
    settings = get_settings()
    api_key = settings.hf_token
    if not api_key:
        logger.error("HF_TOKEN environment variable is not set")
        raise ValueError("HF_TOKEN environment variable is required")
        
    return AsyncOpenAI(
        base_url=BASE_URL,
        api_key=api_key
    )

async def call_model_with_retry(client: AsyncOpenAI, model: str, messages: list, max_retries: int = 3) -> Optional[str]:
    """
    Calls the AI model with automatic retry logic for 503 errors.
    
    Args:
        client: AsyncOpenAI client
        model: Model identifier string
        messages: List of message objects
        max_retries: Number of retry attempts
        
    Returns:
        Generated text content or None if failed
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} calling model: {model}")
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024,
                temperature=0.1
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
                
        except APIStatusError as e:
            if e.status_code == 503:
                logger.warning(f"Model {model} unavailable (503). Attempt {attempt + 1} failed.")
                if attempt < max_retries - 1:
                    wait_time = 2  # Wait 2 seconds
                    logger.info(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    continue
            logger.error(f"API Error calling {model}: {str(e)}")
            break # Don't retry for non-503 errors or if 503 handling logic allows
            
        except Exception as e:
            logger.error(f"Unexpected error calling {model}: {str(e)}")
            break
            
    return None

async def call_fallback_model(client: AsyncOpenAI, messages: list) -> str:
    """
    Calls the fallback model if the primary model fails.
    
    Args:
        client: AsyncOpenAI client
        messages: List of message objects
        
    Returns:
        Generated text content
        
    Raises:
        HTTPException: If fallback also fails
    """
    logger.info(f"Switching to fallback model: {FALLBACK_MODEL}")
    try:
        response = await client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.1
        )
        
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            raise ValueError("Empty response from fallback model")
            
    except Exception as e:
        logger.error(f"Fallback model failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable. Both primary and backup models failed to respond."
        )

async def analyze_image(image_url: str, prompt: str) -> str:
    """
    Analyzes an image using the primary model, falling back to the secondary model if needed.
    
    Args:
        image_url: URL or data URI of the image
        prompt: Initial instruction prompt
        
    Returns:
        Generated text response
        
    Raises:
        HTTPException: If service is unavailable
    """
    client = get_client()
    
    # Common messages structure
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]

    # Try Primary Model with Retry
    result = await call_model_with_retry(client, PRIMARY_MODEL, messages)
    
    if result:
        return result
        
    # If Primary failed, try Fallback
    logger.warning("Primary model failed after retries. Invoking fallback.")
    return await call_fallback_model(client, messages)
