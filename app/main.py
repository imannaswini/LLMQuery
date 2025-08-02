from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
import faiss
import os
from sentence_transformers import SentenceTransformer
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
documents = []
index = None
model = SentenceTransformer('all-MiniLM-L6-v2')
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pydantic models
class Query(BaseModel):
    query: str
    top_k: int = 3

class HackRxRequest(BaseModel):
    documents: list[str]
    questions: list[str] = []

# Utility functions
def extract_text_from_pdf(uploaded_file) -> str:
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

def build_faiss_index(texts: list[str]):
    global index, documents
    documents = texts
    embeddings = model.encode(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

def search_index(query: str, top_k: int = 3):
    if index is None:
        raise HTTPException(status_code=400, detail="Index not built yet.")
    query_vec = model.encode([query])
    D, I = index.search(query_vec, top_k)
    return [documents[i] for i in I[0]]

def ask_openai(query: str, context: str):
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}\n\nAnswer:"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception:
        return None  # fallback to clause-based answer

# Routes

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    text = extract_text_from_pdf(file.file)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found in PDF.")

    # Break into clauses
    clauses = [c.strip() for c in text.split("\n") if len(c.strip()) > 30]
    if not clauses:
        raise HTTPException(status_code=400, detail="No meaningful clauses found.")

    build_faiss_index(clauses)

    return {
        "message": "PDF parsed and indexed successfully.",
        "clauses_indexed": len(clauses),
        "extracted_text": "\n".join(clauses)  # 🧠 added for frontend to send to /hackrx/run
    }

@app.post("/hackrx/run")
async def hackrx_run(req: HackRxRequest):
    if not req.documents:
        raise HTTPException(status_code=400, detail="Field 'documents' is required.")
    build_faiss_index(req.documents)
    return {"message": f"Indexed {len(req.documents)} documents successfully."}

@app.post("/intelligent-query")
def intelligent_query(query_input: Query):
    try:
        clauses = search_index(query_input.query, query_input.top_k)
        context = "\n".join(clauses)
        answer = ask_openai(query_input.query, context)

        if answer:
            return {
                "final_reasoning": {
                    "answer": answer,
                    "supporting_clauses": clauses,
                    "explanation": f"Based on top {query_input.top_k} clauses from the document."
                }
            }
        else:
            return {
                "final_reasoning": {
                    "answer": "⚠️ OpenAI API failed (quota exceeded or error). Showing relevant PDF text instead.",
                    "supporting_clauses": clauses,
                    "explanation": "These are the top-matching clauses from the indexed PDF."
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
