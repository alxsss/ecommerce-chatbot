import pandas as pd
import chromadb
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

import time
print("🟡 Loading vector store...")

start = time.time()

try:
    # Load and clean product data
    df = pd.read_csv("Product_Information_Dataset.csv")
    # Drop rows with missing essential fields
    df = df.dropna(subset=["description", "title", "price", "average_rating"])

    # Fill remaining text fields with empty strings to avoid issues
    for col in df.select_dtypes(include="object").columns:
        df.loc[:, col] = df[col].fillna("")

    chroma_client = PersistentClient(path="./chroma_db")
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = chroma_client.get_or_create_collection(
        name="product_descriptions",
        embedding_function=embedding_fn
    )
    # Populate collection if empty
    if collection.count() == 0:
        print("🟡 Populating ChromaDB...")
        documents = df["description"].tolist()
        metadatas = df[["title", "price", "average_rating"]].to_dict("records")
        ids = [f"id_{i}" for i in range(len(df))]

        for start in range(0, len(df), 166):
            end = min(start + 166, len(df))
            #print(f"📦 Adding batch {start}–{end}")
            collection.add(
                documents=documents[start:end],
                metadatas=metadatas[start:end],
                ids=ids[start:end]
            )
except Exception as e:
    import traceback
    print("❌ Error during vector store setup:", e)
    traceback.print_exc()
    raise

print(f"✅ Vector store ready in {round(time.time() - start, 2)}s")

def get_similar_products(query: str, top_k: int = 10) -> str:
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["metadatas"][0]