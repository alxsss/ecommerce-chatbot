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

📦 Product Search

curl -X POST http://<EC2-IP>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top rated guitar products?"}'

curl -X POST http://<EC2-IP>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "cheap acoustic guitar strings"}'

🧾 Order Search

curl -X POST http://<EC2-IP>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the details of my last order?"}'

# Then reply:
curl -X POST http://<EC2-IP>:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "My customer id is 37077"}'

🧰 Implementation Summary
All services run in containers via docker-compose
Queries are routed from chat_service to the appropriate microservice based on:
Rule-based keyword checks
LLM zero-shot classification
The product service uses dense retrieval via all-MiniLM-L6-v2 and ChromaDB
The order service constructs appropirate prompt to LLM to get possible endpoint (e.g., /data/customer/{id})
The mock API exposes the real order dataset and queries the endpoint supplied by LLM
Response from mock API is sent again to LLM for summarization
The LLM service handles:
Classifying intent (product vs order)
Suggesting endpoint using user query and history of conversation
Summarizing retrieved records conversationally

🐳 Deployment

Launch t3.large EC2 instance
Install Docker and Docker Compose:
sudo apt update && sudo apt install docker.io docker-compose -y
Clone this repo and run:
docker-compose up --build
Access your assistant at:
http://<EC2-IP>:8000/chat


## Running Locally

## Getting model file
  If you need model locally
    Run the following commands
    1. chmod +x download_model.sh
    2. ./download_model.sh
  Otherwise, get API from third party companies like openrouter

  Start services in different terminals:

```bash


cd chat_service
uvicorn main:app --port 8000

cd product_search_service
uvicorn main:app --port 8001

cd order_lookup_service
uvicorn main:app --port 8002
uvicorn mock_api:app --port 8005

cd llm_service
uvicorn main:app --port 8003


Query via curl:
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"query": "What are the top-rated guitar strings?"}'

See [sample_interactions.md](./sample_interactions.md) for example chatbot queries and responses.