from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_URL = "https://openrouter.ai/api/v1/chat/completions"

  
@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [           
            {"role": "system", "content": prompt}
        ],
        "max_tokens": 200
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(LLM_URL, headers=headers, json=payload)
        result = response.json()
        res=result["choices"][0]["message"]["content"].strip()        
        return {"response": res}
