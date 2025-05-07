import httpx
from llama_cpp import Llama

# Load model
llm = Llama(
    model_path="model/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=6
)
def classify_query_with_llm(query: str) -> str:
    """
    Uses the local Mistral LLM to classify a user query as 'order', 'product', or 'other'.

    Returns:
        classification (str): One of 'order', 'product', or 'other'.
    """
    classification_prompt = f"""You are a classifier for an e-commerce chatbot.

Decide whether the user query is about:
- order
- product
- other

Only respond with a single word: order, product, or other.

### Query:
{query}

### Classification:
"""
    try:
        result = llm(classification_prompt, max_tokens=10, temperature=0.0)
        text = result["choices"][0]["text"].strip().lower()
        if text in {"order", "product", "other"}:
            return text
        return "other" 
    except Exception as e:
        print("⚠️ LLM classification error:", e)
        return "other"

async def route_query(query: str) -> str:
    query_lower = query.lower()

    # Rule-based shortcut (optional)
    if any(keyword in query_lower for keyword in ["order", "purchase", "customer id", "shipping", "payment", "priority", "profit"]):
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8002/data/customer/37077")
            return f"Order info: {response.json()}"

    #elif any(keyword in query_lower for keyword in ["product", "guitar", "price", "rated", "accessory", "category", "recommend", "feature"]):
       # async with httpx.AsyncClient() as client:
       #     response = await client.post("http://localhost:8001/search", json={"query": query})
       #     return response.json().get("response", "No matching products found.")

    # Fallback to LLM-based zero-shot classification

    classification = classify_query_with_llm(query)

    if "order" in classification:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8002/data/customer/37077")
            return f"[LLM-Routed] Order info: {response.json()}"

    elif "product" in classification:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8001/search", json={"query": query})
            return response.json().get("response", "[LLM-Routed] No matching products found.")

    else:
        return "I'm not sure how to help with that. Can you rephrase your question?"