from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
import os
import PyPDF2
from typing import List, Dict
import time
import uuid
import hashlib

# Qdrant Configuration
QDRANT_URL = "http://10.10.100.121:6333" 
QDRANT_API_KEY = "qdrantclientdocqakey"  
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

COLLECTION_NAME = "resume"

embed_model = SentenceTransformer(r"C:\Users\navin.s\all-MiniLM-L6-v2")

def generate_point_id(file_name: str, chunk_id: int) -> str:
    """Generate a UUID based on file name and chunk ID."""
    unique_string = f"{file_name}_{chunk_id}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

def extract_text_from_pdf(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return ""

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_document(file_path: str, doc_type: str) -> List[Dict]:
    text = extract_text_from_pdf(file_path)
    if not text:
        return []
    
    chunks = split_text_into_chunks(text)
    documents = []
    
    for i, chunk in enumerate(chunks):
        file_name = os.path.basename(file_path)
        point_id = generate_point_id(file_name, i)
        
        documents.append({
            "id": point_id,
            "text": chunk,
            "metadata": {
                "source": file_name,
                "chunk_id": i,
                "doc_type": doc_type,
                "file_path": file_path
            }
        })
    
    return documents

def embed_and_store_documents(documents: List[Dict]):
    for doc in documents:
        try:
            embedding = embed_model.encode(doc["text"]).tolist()
            
            qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=[{
                    "id": doc["id"],  
                    "vector": embedding,
                    "payload": {
                        "text": doc["text"],
                        "metadata": doc["metadata"]
                    }
                }]
            )
        except Exception as e:
            print(f"Error processing document {doc['metadata']['source']}: {e}")
            print(f"Error details: {str(e)}")

def process_data_directory():
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} not found")
        return
    
    existing_collections = [col.name for col in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing_collections:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION_NAME}' created successfully.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists. Adding new documents...")
    
    for doc_type in os.listdir(data_dir):
        doc_type_path = os.path.join(data_dir, doc_type)
        if os.path.isdir(doc_type_path):
            print(f"\nProcessing {doc_type} documents...")
            
            for file in os.listdir(doc_type_path):
                if file.endswith('.pdf'):
                    file_path = os.path.join(doc_type_path, file)
                    print(f"Processing {file}...")
                    
                    try:
                        documents = process_document(file_path, doc_type)
                        
                        embed_and_store_documents(documents)
                        
                        print(f"Completed processing {file}")
                    except Exception as e:
                        print(f"Error processing file {file}: {e}")
                        continue
                    
                    time.sleep(1)

def main():
    print("Starting document processing...")
    process_data_directory()
    print("\nDocument processing completed!")

if __name__ == "__main__":
    main()