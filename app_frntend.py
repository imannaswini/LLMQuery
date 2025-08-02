import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("📄 PDF Q&A Demo")

# Step 1: Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("📤 Uploading and indexing PDF..."):
        parse_res = requests.post(
            f"{BACKEND_URL}/parse-pdf",
            files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        )

        if parse_res.status_code == 200:
            st.success("✅ PDF parsed and indexed successfully!")
        else:
            st.error(f"❌ Failed to parse PDF: {parse_res.text}")

# Step 2: Ask a question
st.markdown("---")
question = st.text_input("❓ Ask a question from the uploaded document")

if st.button("Submit Question"):
    if not question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("🔎 Searching and reasoning..."):
            res = requests.post(
                f"{BACKEND_URL}/intelligent-query",
                json={"query": question, "top_k": 3}
            )
        if res.status_code == 200:
            result = res.json()["final_reasoning"]
            st.markdown("### ✅ **Answer**")
            st.write(result["answer"])
            st.markdown("### 📌 **Supporting Clauses**")
            for clause in result["supporting_clauses"]:
                st.write("-", clause)
            st.markdown("### 💡 **Explanation**")
            st.write(result["explanation"])
        else:
            st.error(f"❌ Error: {res.text}")
