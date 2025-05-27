import os
import json
from src.rag import setup_qdrant, store_in_qdrant, search_qdrant
from src.pdf_processor import process_multiple_pdfs
from src.llm_class import DeepSeek

QUERY_LOG_FILE = "query_logs_deepseek.json"

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

    setup_qdrant()
    print("Processing PDFs...")
    chunks = process_multiple_pdfs(pdf_dir)
    store_in_qdrant(chunks)
    print("Chunks stored in faiss.")

    llm1 = DeepSeek() 
    
    queries_1 = [
        "What is visual search and what are its advantages?",
        "Who are the primary stakeholders who use visual search in their enterprise?",
        "What is the main use of visual search?",
        "What is the different types of search algorithms used in visual search?",
        "What is the machine learning and how organizations use it?",
        "What is deep learning and why is it efficient than traditional machine learning algorithms?",
        "How can LLM be leveraged for a particular use case catered to a particular enterprise?"
    ]


    for query in queries_1:
        print(f"\n Query for DeepSeek: {query}")

        retrieved_chunks = search_qdrant(query, top_k=5)
        print("\n Retrieved Chunks for DeepSeek:")
        for idx, chunk in enumerate(retrieved_chunks, 1):
            print(f"{idx}. {chunk}\n")

        response = llm1.query(query)
        print("\n Generated Response for DeepSeek:", response)
        save_query_to_json(query, retrieved_chunks, response)

if __name__ == "__main__":
    main()
