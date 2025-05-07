from fastapi import FastAPI, Request
from rag_search import retrieve_with_llm

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