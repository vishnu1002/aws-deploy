from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer
import os

# Initialize Qdrant client
QDRANT_URL = "http://10.10.100.121:6333" 
QDRANT_API_KEY = "qdrantclientdocqakey"  
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
collections = qdrant.get_collections()
print("Available Collections:", collections)


COLLECTION_NAME = "resume"

EMBEDDING_MODEL_PATH = r"all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL_PATH)

def setup_qdrant():
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def store_in_qdrant(chunks):
    embeddings = model.encode(chunks, convert_to_numpy=True)
    points = [
        PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": chunks[i]})
        for i in range(len(chunks))
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

def search_qdrant(query, top_k=5):
    query_vector = model.encode(query).tolist()
    search_results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )
    return [hit.payload["text"] for hit in search_results]
