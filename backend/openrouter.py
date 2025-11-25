"""OpenRouter API client for making LLM requests."""

import httpx
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenRouter API.

    Args:
        model: OpenRouter model identifier (e.g., "openai/gpt-4o")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except Exception as e:
        print(f"Error querying model {model}: {e}")
        return None


async def query_base_model_parallel(
    base_model: str,
    messages: List[Dict[str, str]],
    count: int
) -> List[Optional[Dict[str, Any]]]:
    """
    Query the base model multiple times in parallel with the same messages.
    Args:
        base_model: The OpenRouter model identifier to use for all queries.
        messages: The messages to send to the model.
        count: The number of times to query the model.
    Returns:
        A list of responses.
    """
    import asyncio

    tasks = [query_model(base_model, messages) for _ in range(count)]
    return await asyncio.gather(*tasks)


async def query_personas_parallel(
    base_model: str,
    user_query: str,
    personas: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query a single model with multiple personas in parallel.
    Args:
        base_model: The OpenRouter model identifier to use for all queries.
        user_query: The user's query.
        personas: A list of persona dictionaries, each with "name" and "prompt".
    Returns:
        A dictionary mapping persona name to the response.
    """
    import asyncio

    tasks = []
    for p in personas:
        messages = [
            {"role": "system", "content": p["prompt"]},
            {"role": "user", "content": user_query}
        ]
        tasks.append(query_model(base_model, messages))

    responses = await asyncio.gather(*tasks)

    return {persona["name"]: response for persona, response in zip(personas, responses)}


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenRouter model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
