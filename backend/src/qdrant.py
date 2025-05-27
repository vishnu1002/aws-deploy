from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_URL = "http://10.10.100.121:6333" 
QDRANT_API_KEY = "qdrantclientdocqakey"  
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

COLLECTION_NAME = "resume"

existing_collections = [col.name for col in qdrant.get_collections().collections]
if COLLECTION_NAME not in existing_collections:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' created successfully.")
else:
    print(f"Collection '{COLLECTION_NAME}' already exists.")
