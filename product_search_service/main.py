from fastapi import FastAPI, Request
from rag_search import retrieve_with_llm
from vector_store import get_similar_products
import httpx
app = FastAPI(title="Product Search RAG Service")

@app.post("/search")
async def search(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        if not query:
            return {"response": "Please provide a query."}
        
        result = await retrieve_with_llm(query)
        return {"response": result}

    except Exception as e:
        print("❌ Error in /search:", e)
        return {"error": str(e)}

session_histories = {}

@app.post("/product")
async def handle_product(request: Request):
    data = await request.json()
    query = data.get("query", "")
    session_id = data.get("session_id")

    if not session_id:
        return {"response": "Missing session_id"}

    history = session_histories.setdefault(session_id, [])
    product_info = get_similar_products(query, top_k=10)
    
    # Format for LLM prompt
    context = "\n".join(
        f"{p.get('title', 'Unknown')} — ${p.get('price', 'N/A')} (Rating: {p.get('average_rating', 'N/A')})"
        for i, p in enumerate(product_info)
    )

    messages = history + [{"role": "user", "content": query}]
    prompt = (
        "You are a helpful e-commerce assistant.\n\n"
        + "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages)
        + f"Here are some product options:\n{context}\nPlease recommend the best product based on the user's question, one and ask if the user wants more suggestions. Start your response directly — do not repeat the user's question."
    )
    

    async with httpx.AsyncClient(timeout=180.0) as client:
        llm_response = await client.post("http://localhost:8003/generate", json={
            "prompt": prompt,
            "max_tokens": 200
        })

    answer = llm_response.json().get("response", "[LLM] No response.")
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": answer})

    return {"response": answer}
