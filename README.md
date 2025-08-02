LLMQuery - AI-powered Document Q&A Engine

LLMQuery is a FastAPI-powered backend that lets users upload documents (PDF, DOCX, Emails) and ask questions in natural language. The system semantically searches the document using FAISS vector database and responds with an LLM-generated answer that includes:

- Final Answer  
-  Supporting Clauses  
-  Explanation  

Perfect for legal docs, research papers, resumes, or any structured content.


 Features

- Semantic Search: Finds the most relevant content from uploaded files using Sentence Transformers.
- Reasoning with LLM: Uses OpenAI’s GPT to provide clear, structured answers.
- Multi-file Support: Handles PDF, DOCX, and email (`.msg`) files.
- FastAPI Backend: Lightweight and fast REST API.
- Hackathon-Ready: Easily testable via frontend or webhooks like `ngrok`.


 Tech Stack

| Layer       | Technology        |
|-------------|-------------------|
| Backend     | FastAPI           |
| LLM         | OpenAI GPT-3.5-turbo (via API) |
| Embeddings  | Sentence Transformers |
| Vector DB   | FAISS             |
| File Parsing| PyPDF2, python-docx, extract-msg |
| Frontend    | React (form-based query input) |
| Hosting     | Render (backend), Vercel (frontend) |
| Dev Tools   | Ngrok, Git, .env config |



 How It Works

1. Upload a document via UI or API.
2. It gets chunked and embedded using sentence-transformers.
3. FAISS searches the vector store for context.
4. LLM (GPT-3.5) generates structured, natural-language answers.
5. Output includes:
   -  Final Answer  
   - Supporting Clauses  
   - Explanation  

---

 Installation (Local)

```bash
git clone https://github.com/imannaswini/LLMQuery
cd LLMQuery
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
