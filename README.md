# Smart E-Commerce Assistant Chatbot

This project implements an AI-powered chatbot that answers product and order queries using microservices.

## Services

- `chat_service`: Routes user input to relevant microservice.
- `product_search_service`: Uses RAG to suggest and describe products.
- `order_lookup_service`: Serves mock order data via API.

## Getting model file
Run the following commands
1. chmod +x download_model.sh
2. ./download_model.sh

## Running Locally

Start services in different terminals:

```bash


cd chat_service
uvicorn main:app --port 8000

cd product_search_service
uvicorn main:app --port 8001

cd order_lookup_service
uvicorn main:app --port 8002
uvicorn mock_api:app --port 8004

cd llm_service
uvicorn main:app --port 8003



Query via curl:
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"query": "What are the top-rated guitar strings?"}'

## Running Remote
1. Checkout remote-run branch of this repo and follow instuctions