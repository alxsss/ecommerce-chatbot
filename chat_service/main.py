from fastapi import FastAPI, Request , HTTPException
from router import route_query
import json
from typing import Dict, Any
app = FastAPI(title="Chat Router")

@app.post("/chat")
async def chat(request: Request) -> Dict[str, Any]:
    try:
        # Get raw bytes first
        raw_body = await request.body()
        
        # Try UTF-8 first, fallback to latin-1 if needed
        try:
            body = raw_body.decode('utf-8')
        except UnicodeDecodeError:
            body = raw_body.decode('latin-1')
            # Replace common problematic characters
            body = body.replace('\x92', "'")  # Smart single quote
            body = body.replace('\x91', "'")  # Another smart quote variant
            body = body.replace('\x96', '-')   # En dash
            body = body.replace('\x97', '--')  # Em dash
        
        # Parse the cleaned JSON
        try:
            data = json.loads(body)
            user_input = data.get("query", "").strip()
            
            if not user_input:
                raise HTTPException(status_code=400, detail="Empty query")
                
            response = await route_query(user_input)
            return {"response": response}
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )