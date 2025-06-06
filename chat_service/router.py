import httpx
from fastapi import Request
from uuid import uuid4
import os

# Store session history in memory
session_histories = {}
ORDER_API = os.getenv("ORDER_API")
PRODUCT_SEARCH_API = os.getenv("PRODUCT_SEARCH_API")
LLM_API = os.getenv("LLM_API")

async def route_query(query: str, session_id: str = None) -> str:
    query_lower = query.lower()
    if session_id is None:
        session_id = str(uuid4())
    history = session_histories.setdefault(session_id, [])

    async with httpx.AsyncClient(timeout=600.0) as client:
        # Rule-based order check
        if any(keyword in query_lower for keyword in [
            "order", "purchase", "customer id", "shipping", "payment", "priority", "profit", "category"
        ]):
            response = await client.post(ORDER_API, json={
                "query": query,
                "session_id": session_id
            })
            return response.json().get("response", "[Order] No response.")

        # Rule-based product check
        elif any(keyword in query_lower for keyword in [
            "product", "guitar", "price", "rated", "accessory", "recommend", "feature"
        ]):
            response = await client.post(PRODUCT_SEARCH_API, json={
                "query": query,
                "session_id": session_id
            })
            return response.json().get("response", "[Product] No response.")

        # Fallback: classify via LLM
        classification_prompt = f"""### Instruction:
You are a classifier for an e-commerce chatbot.

Decide whether the user query is about:
- "order" (for anything related to orders, customers, shipping, etc.)
- "product" (for questions about products, features, prices, etc.)
- "other" (if it’s not related to e-commerce)
Note: If the input is only a number (like "37077"), and the last assistant message asked for a customer ID or order detail, classify it as an "order".
Only respond with one of these labels: order, product, or other.

### Query:
{query}

### Classification:"""

        response = await client.post(LLM_API, json={"prompt": classification_prompt, "max_tokens": 10})
        category = response.json().get("response", "").strip().lower()

        if category == "order":
            response = await client.post(ORDER_API, json={
                "query": query,
                "session_id": session_id
            })
            return response.json().get("response", "[Order] No response.")

        elif category == "product":
            response = await client.post(PRODUCT_SEARCH_API, json={
                "query": query,
                "session_id": session_id
            })
            return response.json().get("response", "[Product] No response.")

        else:
            return "I'm not sure how to help with that. Please rephrase your question."
