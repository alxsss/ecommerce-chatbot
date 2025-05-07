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
    context = get_similar_products(query)
    prompt = f"""You are a helpful product assistant. Answer the question using the provided passage. 
    Be sure to respond in a complete sentence, include price and ratings of products. 

User query: {query}

Relevant product info:
{context}

Answer:"""

    return await call_llm(prompt)