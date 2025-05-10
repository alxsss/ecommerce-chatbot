import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import pandas as pd
from typing import Dict, Optional
import httpx

import os

app = FastAPI()

MOCK_API = os.getenv("MOCK_API")
LLM_API = os.getenv("LLM_API")
LLM_LIMIT=os.getenv("LLM_LIMIT")

# Conversation state storage
conversation_states: Dict[str, Dict] = {}  # {session_id: {history: [], pending_query: str, customer_id: int}}

class UserQuery(BaseModel):
    query: str
    session_id: str = "default"
    history_str: Optional[str] = None


def extract_customer_id(query: str) -> Optional[int]:
    """Extracts customer ID from natural language"""
    match = re.search(r'(?:customer|id)\s*(?:is|:)?\s*(\d+)', query, re.IGNORECASE)
    return int(match.group(1)) if match else None

def build_prompt(query: str, history_str: str) -> str:

    return f"""   
    You are an e-commerce assistant that routes user queries to specific API endpoints.
    We have the following endpoints:
    - /data — Get all records in the dataset.
    - /data/customer/{{customer_id}} — Filter data by Customer ID (a number, required).
    - /data/product-category/{{category}} — Filter data by Product Category (a string, required).
    - /data/order-priority/{{priority}} — Filter data by Order Priority (a string, required).
    - /data/total-sales-by-category — Total sales by product category.
    - /data/high-profit-products — Products with high profit.
    - /data/shipping-cost-summary — Shipping cost summary.
    - /data/profit-by-gender — Profit summary by gender.
    Rules:
    1. If the query contains a number like 12345, assume it is a cutomer ID and respond with `/data/customer/{{number}}`
    2. If the query contains a string like "high", "low", or "office supplies", treat it as a category or priority.
    3. If the query requires a `customer_id` but none is provided, ask for it.
    4. When `customer_id` is provided, respond with the correct `/data/customer/{{id}}` endpoint.
    5. If the query mentions `min_profit = X` or similar, respond with:`/data/high-profit-products?min_profit=X`
    5. Respond **ONLY** using one of the following formats:
    ```text
    ENDPOINT: /data/endpoint/params
    ```
    or if missing info:
    ```text
    NEED_ID: Please provide Customer ID
    ```
    HISTORY OF CONVERSATION:{history_str}

    Examples:
    1. Query: "show my orders"
       Response:
       ```text
       NEED_ID: Please provide Customer ID
       ```
    2. Query: "12345"
       Response:
       ```text
       ENDPOINT: /data/customer/12345
    3. Query: "Find high priority orders"
       Response:
       ```text
       ENDPOINT: /data/order-priority/high
       ```
    4. Query: "My customer ID is 12345"
       Response:
       ```text
       ENDPOINT: /data/customer/12345
       ```
    Current Query: {query}
    """

def call_llm_with_context(query: str, history_str: str) -> str:
    prompt = build_prompt(query, history_str)   
    response = requests.post(
        LLM_API,
        json={"prompt": prompt, "max_tokens": 50, "stop": ["```"]},
        timeout=500
    ).json()
    
    return response["response"]

async def route_query_to_mock_api(endpoint: str) -> Dict:
    """Makes HTTP request to mock API endpoint"""
    base_url = MOCK_API

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"API request failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# --- LLM Response Parser ---
def extract_endpoint(llm_response: str) -> str:
    """
    Extracts endpoint from responses like:
    '\n    ### Response:\n    ```\n    ENDPOINT: /data/customer/123\n    ```'
    """
    # Method 1: Regex (most reliable)
    match = re.search(r'ENDPOINT:\s*(/data/[^\s`]+)', llm_response)
    if match:
        return match.group(1).strip()
    
    # Method 2: Line-by-line fallback
    for line in llm_response.split('\n'):
        if 'ENDPOINT:' in line:
            return line.split('ENDPOINT:')[1].strip().strip('`')
    
    raise ValueError("No endpoint found in LLM response")

@app.post("/order")
async def order(query: UserQuery):
    """Interactive endpoint with conversation history"""
    try:        
        # Use only the last 3 messages in history
        short_history = "\n".join((query.history_str or "").splitlines()[-6:])  # 3 user-bot pairs = 6 lines
        llm_response = call_llm_with_context(query.query, short_history)
      
        # Parse LLM response
        if "NEED_ID:" in llm_response:        
            return {"response": llm_response.split("NEED_ID:")[1].strip()}
        
        endpoint = extract_endpoint(llm_response)
        data = await route_query_to_mock_api(endpoint) 
        #since openrouter has restrinction on the length of the prompts we need truncate data
        if isinstance(data, list):
           data = data[:10]
        summary_prompt = f"""
        ### Instruction:
        The user asked: "{query.query}"
        The backend returned the following data from endpoint `{endpoint}`:
        {json.dumps(data, indent=2)}

        Summarize the key insights in a clear, friendly way that makes sense to a customer.
        Avoid listing raw fields unless helpful. You can also end with a follow-up suggestion like:
        "Would you like to know more details?" or "Is there anything else I can help you with?"
        """
        summary_response = requests.post(
            LLM_API,
            json={"prompt": summary_prompt, "max_tokens": 300},
            timeout=500
        ).json()
        summary = summary_response["response"].strip().strip('"')
        summary = summary.replace('\\n', '\n')

        return {
            "response": summary_response["response"],
            #"endpoint": endpoint,
            #"raw_data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))