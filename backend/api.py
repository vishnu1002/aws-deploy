from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge
from sentence_transformers import SentenceTransformer
from src.rag import QdrantClient, search_qdrant, store_in_qdrant
from src.llm_class import DeepSeek, Llama, Qwen
import os
import PyPDF2
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI(
    title="Enterprise Search API",
    description="API for enterprise search and document analysis",
    version="1.0.0",
    openapi_version="3.0.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000" "http://10.10.100.181", "http://10.10.100.181:3000", "http://10.10.100.181:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

deepseek_model = DeepSeek()
llama_model = Llama()
qwen_model = Qwen()

QDRANT_URL = "http://10.10.100.121:6333"
QDRANT_API_KEY = "qdrantclientdocqakey"
COLLECTION_NAME = "resume"

try:
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=10.0  
    )
    print("Successfully connected to Qdrant")
except Exception as e:
    print(f"Error connecting to Qdrant: {str(e)}")
    raise

embed_model = SentenceTransformer(r"all-MiniLM-L6-v2")

#FastAPI model request
class QueryRequest(BaseModel):
    queries: List[str]
    model_choice: str  

class QdrantSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SearchRequest(BaseModel):
    query: str
    model: str
    docType: str

DOCUMENT_TYPES = {
    "resume": "resume",
    "policy": "policy_documents",
    "reports": "reports"
}

MODELS = {
    "deepseek": "DeepSeek",
    "llama": "Llama",
    "qwen": "Qwen",
    "compare": "Compare"
}

def fetch_similar_passage(query: str, top_k: int = 5) -> List[str]:
    query_vector = embed_model.encode(query).tolist()
    search_results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    if search_results:
        return [hit.payload["text"] for hit in search_results]
    return ["No relevant passage found."]

# Evaluate models
def evaluate_models(query: str, model_choice: str) -> Dict:
    retrieved_passages = fetch_similar_passage(query, top_k=5)

    if retrieved_passages[0] == "No relevant passage found.":
        return {"error": "No relevant passage found in Qdrant."}

    results = {}
    latencies = {}

    # Model selection
    models = {}
    if model_choice == "DeepSeek":
        models["DeepSeek"] = deepseek_model
    elif model_choice == "Llama":
        models["Llama"] = llama_model
    elif model_choice == "Qwen":
        models["Qwen"] = qwen_model
    else:  
        models = {
            "DeepSeek": deepseek_model,
            "Llama": llama_model,
            "Qwen": qwen_model
        }

    for model_name, model in models.items():
        start_time = time.time()
        passages_text = "\n\n".join([f"Resume {i+1}:\n{passage}" for i, passage in enumerate(retrieved_passages)])
        # model prompt
        prompt = f"""
You are an advanced resume analysis assistant designed for professional talent evaluation.

**Task**: Conduct a comprehensive analysis of the provided resume(s) to address the user's specific query. Extract relevant qualifications, professional experience, and technical competencies. When required, perform comparative evaluations across multiple candidates. All assessments must be strictly based on the resume data provided.

---

User Query:
{query}

---

Resume(s):
{passages_text}

---

Analysis Protocol:
1. First extract and categorize all professional qualifications and work experience.
2. For individual candidate inquiries, deliver a comprehensive assessment of their "core competencies and professional background."
3. For filtered candidate searches (e.g., by technology stack or years of experience), present "qualified candidates" with supporting evidence.
4. For comparative analysis (e.g., "show similar to Candidate X"), first establish the "primary professional competencies" of the reference candidate, then "identify other candidates with aligned skill profiles."
5. For role-specific evaluations (e.g., "Is Candidate X suitable for a frontend engineering position?"), assess against industry-standard role requirements.

---

Output Structure:

[Concise, evidence-based response to the query with professional formatting]

For multiple candidate matches:

Candidate Profile: [Full Name]  
- Core Competencies: [Skill1, Skill2, ...]  
- Professional Experience:  
  - [Position Title] at [Organization] — [Duration/Years]
  - [Key Responsibilities and Achievements]

Professional Assessment Summary:
[Provide a detailed evaluation of each candidate's professional profile, including:]
- Name of candidate
- Core competencies and skills
- Assessment of technical proficiency levels
- Analysis of industry and domain expertise
- Evaluation of professional trajectory and growth
- Suitability assessment for the specified role or requirements
- Distinctive qualifications or specialized experience

All assessments must be substantiated by information explicitly stated in the resume(s). Do not extrapolate, speculate, or include unverifiable information.
Only return information present in the resume(s). Do not guess or hallucinate.
"""


        try:
            response = model.query(prompt)
            if response and isinstance(response, str):
                results[model_name] = response
            else:
                results[model_name] = "No valid response received."
        except Exception as e:
            results[model_name] = f"Error: {str(e)}"

        end_time = time.time()
        latencies[model_name] = round(end_time - start_time, 2)

    return {
        "responses": results,
        "latencies": latencies
    }

def compare_models(query: str) -> Dict:
    result = evaluate_models(query, "Compare")
    if "error" in result:
        return result

    results = result["responses"]
    rouge = Rouge()
    comparison_results = []
    model_scores = {}

    model_names = list(results.keys())
    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            model_a, model_b = model_names[i], model_names[j]

            if "Error" not in results[model_a] and "Error" not in results[model_b]:
                try:
                    rouge_scores = rouge.get_scores(results[model_a], results[model_b])[0]
                    rouge_l = rouge_scores['rouge-l']['f']
                    bleu_score = sentence_bleu([results[model_a].split()], results[model_b].split())

                    comparison_results.append({
                        "Model 1": model_a,
                        "Model 2": model_b,
                        "BLEU Score": round(bleu_score, 3),
                        "ROUGE-L Score": round(rouge_l, 3)
                    })

                    if model_a not in model_scores:
                        model_scores[model_a] = []
                    if model_b not in model_scores:
                        model_scores[model_b] = []

                    model_scores[model_a].append((model_b, bleu_score, rouge_l))
                    model_scores[model_b].append((model_a, bleu_score, rouge_l))

                except Exception as e:
                    print(f"Error computing scores for {model_a} vs {model_b}: {str(e)}")
                    continue

    aggregated_scores = {}
    for model, scores in model_scores.items():
        if scores:
            avg_bleu = sum(score[1] for score in scores) / len(scores)
            avg_rouge = sum(score[2] for score in scores) / len(scores)
            aggregated_scores[model] = {
                "BLEU": round(avg_bleu, 3),
                "ROUGE-L": round(avg_rouge, 3)
            }

    return {
        "responses": results,
        "latencies": result["latencies"],
        "comparison_results": comparison_results,
        "model_scores": aggregated_scores
    }

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def split_text_into_chunks(text, chunk_size=1000, overlap=200):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

@app.get("/document-types")
def get_document_types():
    return {
        "documentTypes": [
            {"value": "resume", "label": "Resume"},
            {"value": "policy", "label": "Policy Document"},
            {"value": "reports", "label": "Reports"}
        ]
    }

@app.get("/models")
def get_models():
    return {
        "models": [
            {"value": "deepseek", "label": "DeepSeek"},
            {"value": "llama", "label": "LLaMA"},
            {"value": "qwen", "label": "Qwen"},
            {"value": "compare", "label": "Compare All"}
        ]
    }

@app.get("/documents/{doc_type}")
def get_documents_by_type(doc_type: str):
    if doc_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid document type")
    
    try:
        doc_path = os.path.join("data", DOCUMENT_TYPES[doc_type])
        if not os.path.exists(doc_path):
            os.makedirs(doc_path, exist_ok=True)
            return {"documents": []}
        
        documents = []
        for file in os.listdir(doc_path):
            if file.endswith('.pdf'):
                file_path = os.path.join(doc_path, file)
                file_stats = os.stat(file_path)
                documents.append({
                    "name": file,
                    "type": doc_type,
                    "size": f"{file_stats.st_size / 1024:.2f} KB",
                    "lastModified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                })
        
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

search_history = []
analytics_history = []

@app.post("/search")
def search(request: SearchRequest):
    try:
        if request.model not in MODELS:
            raise HTTPException(status_code=400, detail="Invalid model selection")
        if request.docType not in DOCUMENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        retrieved_passages = fetch_similar_passage(request.query, top_k=5)
        
        if retrieved_passages[0] == "No relevant passage found.":
            return {
                "error": "No relevant passage found in the documents.",
                "retrieved_passages": retrieved_passages
            }
        
        if request.model == "compare":
            result = compare_models(request.query)
            if "comparison_results" in result and "latencies" in result:
                analytics_history.append({
                    "comparison_results": result["comparison_results"],
                    "latencies": result["latencies"]
                })
        else:
            result = evaluate_models(request.query, MODELS[request.model])
        
        if "retrieved_passages" not in result:
            result["retrieved_passages"] = retrieved_passages

        # Store search history with results
        search_history.append({
            "query": request.query,
            "model": request.model,
            "docType": request.docType,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "results": result
        })

        # Streaming logic: stream the main model response (first model in responses)
        def generate_stream():
            if "responses" in result:
                for model, response in result["responses"].items():
                    yield f"## {model}\n\n"
                    for chunk in response.split("\n\n"):
                        yield chunk + "\n\n"
                        time.sleep(0.1)
            elif "response" in result:
                for chunk in result["response"].split("\n\n"):
                    yield chunk + "\n\n"
                    time.sleep(0.1)
            else:
                yield "No response."
        return StreamingResponse(generate_stream(), media_type="text/markdown")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing search: {str(e)}")

@app.get("/search-history")
def get_search_history():
    return {"history": list(reversed(search_history))}

@app.delete("/search-history")
def clear_search_history():
    search_history.clear()
    return {"message": "Search history cleared"}

@app.post("/query")
def query_models(request: QueryRequest):
    responses = {}
    for query in request.queries:
        responses[query] = evaluate_models(query, request.model_choice)
    return responses

@app.post("/compare")
def compare_models_endpoint(request: QueryRequest):
    try:
        comparisons = {}
        for query in request.queries:
            comparisons[query] = compare_models(query)
        return comparisons
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in comparison: {str(e)}")

@app.post("/search_qdrant")
def search_qdrant_endpoint(request: QdrantSearchRequest):
    try:
        chunks = search_qdrant(request.query, request.top_k)
        return {"chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching Qdrant: {str(e)}")

@app.get("/document_chunks")
def get_document_chunks(path: str):
    try:
        full_path = os.path.join("data", path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")
        
        text = extract_text_from_pdf(full_path)
        
        chunks = split_text_into_chunks(text)
        store_in_qdrant(chunks)        
        return {"chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/documents")
def get_all_documents():
    try:
        documents = []
        for doc_type, doc_dir in DOCUMENT_TYPES.items():
            doc_path = os.path.join("data", doc_dir)
            if not os.path.exists(doc_path):
                os.makedirs(doc_path, exist_ok=True)
                continue
            
            for file in os.listdir(doc_path):
                if file.endswith('.pdf'):
                    file_path = os.path.join(doc_path, file)
                    file_stats = os.stat(file_path)
                    documents.append({
                        "name": file,
                        "type": doc_type,
                        "size": f"{file_stats.st_size / 1024:.2f} KB",
                        "lastModified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                    })
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")

@app.get("/analytics")
def get_analytics():
    try:
        bleu_scores = {}
        rouge_scores = {}
        latencies = {}

        for entry in analytics_history:
            for comp in entry.get("comparison_results", []):
                for model in [comp["Model 1"], comp["Model 2"]]:
                    bleu_scores.setdefault(model, []).append(comp["BLEU Score"])
                    rouge_scores.setdefault(model, []).append(comp["ROUGE-L Score"])
            for model, latency in entry.get("latencies", {}).items():
                latencies.setdefault(model, []).append(latency)

        bleu = [{"model": m, "score": round(sum(v)/len(v), 3)} for m, v in bleu_scores.items() if v]
        rouge = [{"model": m, "score": round(sum(v)/len(v), 3)} for m, v in rouge_scores.items() if v]
        latency = [{"model": m, "latency": round(sum(v)/len(v), 2)} for m, v in latencies.items() if v]

        return {
            "bleuScores": bleu,
            "rougeScores": rouge,
            "latencies": latency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

@app.post("/upload-documents")
async def upload_documents(
    files: List[UploadFile] = File(...),
    docType: Optional[str] = Form('resume')
):
    try:
        if len(files) > 20:
            raise HTTPException(status_code=400, detail="You can only upload up to 20 files at a time.")
        doc_type_map = {
            'resume': 'resume',
            'policy': 'policy_documents',
            'reports': 'reports'
        }
        folder = doc_type_map.get(docType, 'resume')
        save_dir = Path('data') / folder
        save_dir.mkdir(parents=True, exist_ok=True)
        uploaded_files = []
        for file in files:
            if file.filename.endswith('.pdf'):
                file_path = save_dir / file.filename
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                uploaded_files.append(file.filename)
        return {"message": f"Successfully uploaded {len(uploaded_files)} documents", "files": uploaded_files}
    except Exception as e:
        print(f"Error in upload_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-document/{doc_type}/{filename}")
async def download_document(doc_type: str, filename: str):
    try:
        if doc_type not in DOCUMENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        file_path = os.path.join("data", DOCUMENT_TYPES[doc_type], filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")

@app.delete("/documents/{doc_type}/{filename}")
async def delete_document(doc_type: str, filename: str):
    try:
        if doc_type not in DOCUMENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        file_path = os.path.join("data", DOCUMENT_TYPES[doc_type], filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        os.remove(file_path)
        return {"message": f"Document {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.post("/chatbot-query")
async def chatbot_query(query: str = Form(...), model: str = Form("deepseek")):
    try:
        retrieved_passages = fetch_similar_passage(query, top_k=5)
        
        if retrieved_passages[0] == "No relevant passage found.":
            return {
                "response": "I couldn't find any relevant information in the uploaded resumes. Please try a different query or upload more resumes."
            }
        
        if model == "compare":
            responses = {}
            latencies = {}
            
            models = {
                "DeepSeek": deepseek_model,
                "LLaMA": llama_model,
                "Qwen": qwen_model
            }
            
            for model_name, model_instance in models.items():
                start_time = time.time()
                prompt = f"Based on the resume uploaded, answer this question: {query}\n\nResume content: {retrieved_passages[0]}"
                response = model_instance.query(prompt)
                end_time = time.time()
                
                responses[model_name] = response
                latencies[model_name] = round(end_time - start_time, 2)
            
            formatted_response = "Here are responses from all models:\n\n"
            for model_name, response in responses.items():
                formatted_response += f"**{model_name}** (took {latencies[model_name]}s):\n{response}\n\n"
            
            return {
                "response": formatted_response,
                "retrieved_passages": retrieved_passages,
                "model_responses": responses,
                "latencies": latencies
            }
        else:
            model_map = {
                "deepseek": deepseek_model,
                "llama": llama_model,
                "qwen": qwen_model
            }
            
            selected_model = model_map.get(model, deepseek_model)
            prompt = f"Based on the uploaded resume, answer this question: {query}\n\nResume content: {retrieved_passages[0]}"
            response = selected_model.query(prompt)
            
            return {
                "response": response,
                "retrieved_passages": retrieved_passages
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
