from vector_store import get_similar_products
import httpx
async def call_llm(prompt):
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post("http://127.0.0.1:8003/generate", json={"prompt": prompt, "max_tokens": 200})
            print("🟢 LLM Response JSON:", response.json())
            return response.json().get("response", "[LLM] No response.")
    except httpx.RequestError as e:
        print(f"❌ HTTP request failed: {e}")
        return "[LLM] Request failed."

async def retrieve_with_llm(query: str) -> str:
    products = get_similar_products(query, top_k=10)

        # Format for LLM prompt
    product_list = "\n".join(
        f"{p.get('title', 'Unknown')} — ${p.get('price', 'N/A')} (Rating: {p.get('average_rating', 'N/A')})"
        for i, p in enumerate(products)
    )

    prompt = f"""You are a helpful e-commerce assistant.

    The user asked: "{query}"

    Here are some product options:

    {product_list}

    Based on the user's question, choose the most suitable product and briefly explain why.
    """

    return await call_llm(prompt)