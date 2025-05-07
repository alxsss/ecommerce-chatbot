from vector_store import get_similar_products
from llama_cpp import Llama

# Load the Mistral model (only once)
llm = Llama(
    model_path = "../shared_models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=6
)

def retrieve_with_llm(query: str) -> str:
    context = get_similar_products(query)

    prompt = f"""You are a helpful product assistant. Answer the question using the provided passage. 
    Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. 

User query: {query}

Relevant product info:
{context}

Answer:"""

    try:
        result = llm(prompt, max_tokens=200, temperature=0.7)
        return result["choices"][0]["text"].strip()
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

