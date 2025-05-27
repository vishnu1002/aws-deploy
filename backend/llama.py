import os
import json
from src.rag import setup_qdrant, store_in_qdrant, search_qdrant
from src.pdf_processor import process_multiple_pdfs
from src.llm_class import Llama


QUERY_LOG_FILE = "query_logs_llama.json"

def save_query_to_json(query, retrieved_chunks, response):
    data = {
        "query": query,
        "retrieved_chunks": retrieved_chunks,
        "response": response
    }

    if os.path.exists(QUERY_LOG_FILE):
        with open(QUERY_LOG_FILE, "r") as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(data)

    with open(QUERY_LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)

def main():
    pdf_dir = r"C:\Users\navin.s\Desktop\Navin S\model_search\data\Resume"

    setup_qdrant()
    print("Processing PDFs...")
    chunks = process_multiple_pdfs(pdf_dir)
    store_in_qdrant(chunks)
    print("Chunks stored in qdrant.")

    

if __name__ == "__main__":
    main()
