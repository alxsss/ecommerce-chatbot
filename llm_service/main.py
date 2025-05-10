from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY")
LLM_URL = os.getenv("LLM_URL")
  
@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
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
