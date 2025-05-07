from fastapi import FastAPI, Request
from router import route_query

app = FastAPI(title="Chat Router")

@app.post("/chat")
async def chat(request: Request):
    user_input = (await request.json()).get("query", "")
    response = await route_query(user_input)
    return {"response": response}
