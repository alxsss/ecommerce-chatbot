from fastapi import FastAPI, Request
from llama_cpp import Llama
import os

app = FastAPI()

model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../model/mistral-7b-instruct-v0.1.Q4_K_M.gguf"))

llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    n_threads=6
)

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    max_tokens = data.get("max_tokens", 200)
    try:
        result = llm(prompt, max_tokens=max_tokens)
        return {"response": result["choices"][0]["text"].strip()}
    except Exception as e:
        return {"error": str(e)}
