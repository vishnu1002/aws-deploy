import os
import json
from src.rag import setup_faiss, store_in_faiss, search_faiss
from src.pdf_processor import process_multiple_pdfs
from src.llm_class import Qwen


QUERY_LOG_FILE = "query_logs_qwen.json"

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
    pdf_dir = "data/resume"

    setup_faiss()
    print("Processing PDFs...")
    chunks = process_multiple_pdfs(pdf_dir)
    store_in_faiss(chunks)
    print("Chunks stored in fa.")

    llm3 = Qwen() 
    
    queries_3 = [
        "Who are experienced python developers?"
    ]


    for query in queries_3:
        print(f"\n Query for Qwen: {query}")

        retrieved_chunks = search_faiss(query, top_k=5)
        print("\n Retrieved Chunks of Qwen:")
        for idx, chunk in enumerate(retrieved_chunks, 1):
            print(f"{idx}. {chunk}\n")

        response = llm3.query(query)
        print("\n Generated Response for Qwen:", response)
        save_query_to_json(query, retrieved_chunks, response)

if __name__ == "__main__":
    main()
