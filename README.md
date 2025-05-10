E-Commerce Assistant Chatbot

This is a modular, microservices-based AI chatbot designed to assist users in querying product and order data from a simulated e-commerce environment. The system includes product search, order lookup, natural language query routing, and LLM-powered summarization.

🚀 Microservices Overview

chat_service: Routes queries to product, order, or LLM services

product_search_service: Semantic product search via ChromaDB + MiniLM

order_lookup_service: Parses structured queries and summarizes results

mock_api_service: Serves order data (e.g., /data/customer/{id})

llm_service: Local or remote model (e.g., Mistral 7B) for classification & summarization

🧪 Testing Instructions

🔁 Chat with the Assistant

curl -X POST http://<EC2-IP>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top rated guitar products?", "session_id": "test1"}'

📦 Product Search (directly)

curl -X POST http://<EC2-IP>:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "cheap acoustic guitar strings"}'

🧾 Order Query

curl -X POST http://<EC2-IP>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the details of my last order?", "session_id": "test2"}'

# Then reply:
curl -X POST http://<EC2-IP>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "customer_id: 37077", "session_id": "test2"}'

🧰 Implementation Summary

All services run in containers via docker-compose

Queries are routed from chat_service to the appropriate microservice based on:

LLM zero-shot classification

Rule-based keyword checks

The product service uses dense retrieval via all-MiniLM-L6-v2 and ChromaDB

The order service translates freeform questions into endpoint calls (e.g., /data/customer/{id})

The mock API exposes the real order dataset for use by the agent

The LLM service handles:

Classifying intent (product vs order)

Summarizing retrieved records conversationally

🐳 Deployment

Launch t3.large EC2 instance

Install Docker and Docker Compose:

sudo apt update && sudo apt install docker.io docker-compose -y

Clone this repo and run:

docker-compose up --build

Access your assistant at:

http://<EC2-IP>:8000/chat

For any questions or improvements, please open an issue or contribute to the repo.

how can I download or get readme 

## Running Locally

Start services in different terminals:

```bash
cd order_lookup_service
uvicorn mock_api:app --port 8002

cd product_search_service
uvicorn main:app --port 8001

cd chat_service
uvicorn main:app --port 8000

Query via curl:
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"query": "What are the top-rated guitar strings?"}'