import time
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI

QDRANT_URL = "http://10.10.100.121:6333"
QDRANT_API_KEY = "qdrantclientdocqakey"
COLLECTION_NAME = "resume"

DEEPSEEK_API_BASE = "http://10.10.100.122:4444/v1"
DEEPSEEK_API_KEY = "c2VjdXJlc2VydmVyCg=="
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
collections = qdrant.get_collections()
print("Available Collections:", collections)
embed_model = SentenceTransformer(r"C:\Users\navin.s\all-MiniLM-L6-v2")
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_BASE)

def fetch_similar_passage(query):
    query_vector = embed_model.encode(query).tolist()

    search_results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=1
    )

    if search_results:
        top_result = search_results[0]
        return top_result.payload["text"]
    
    return "No relevant passage found."

def query_deepseek(prompt):
    try:
        response = deepseek_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek Error: {str(e)}"

def test_pipeline(query_text):
    print("\n🔍 Searching for relevant passage in Qdrant...")
    retrieved_passage = fetch_similar_passage(query_text)
    print("✅ Retrieved Passage:\n", retrieved_passage)

    if retrieved_passage == "No relevant passage found.":
        print("\n⚠️ No relevant passage found. Exiting test.")
        return

    print("\n🤖 Querying DeepSeek model with retrieved passage...")
    prompt = f"Based on the passage below, provide a detailed explanation:\n\n{retrieved_passage}\n\nExplain in simple terms."
    start_time = time.time()
    deepseek_response = query_deepseek(prompt)
    end_time = time.time()

    print("\n📝 DeepSeek Response:\n", deepseek_response)
    print(f"\n⏱️ Time Taken: {round(end_time - start_time, 2)}s")

if __name__ == "__main__":
    user_query = "What skills does kumaraguru have?"
    test_pipeline(user_query)
