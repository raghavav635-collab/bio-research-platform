import os
import tempfile
import pdfplumber
import chromadb
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
collection = chroma_client.get_or_create_collection(name="biomedical_papers")

st.set_page_config(page_title="Biomedical Research Assistant", layout="wide")

st.title("Biomedical Research Assistant")
st.write("Upload multiple biomedical PDFs, process them, and ask research questions.")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

uploaded_files = st.file_uploader(
    "Upload biomedical research PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} PDF(s) uploaded.")

    if st.button("Process PDFs"):
        total_chunks = 0

        with st.spinner("Processing PDFs..."):
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(uploaded_file.read())
                    temp_path = temp_file.name

                text = extract_text_from_pdf(temp_path)
                chunks = chunk_text(text)
                embeddings = embedding_model.encode(chunks)

                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    collection.add(
                        documents=[chunk],
                        embeddings=[embedding.tolist()],
                        ids=[f"{uploaded_file.name}_chunk_{i}"],
                        metadatas=[{
                            "source": uploaded_file.name,
                            "chunk": i
                        }]
                    )

                total_chunks += len(chunks)

        st.success(f"Processed {len(uploaded_files)} PDF(s) and stored {total_chunks} chunks.")

st.divider()

question = st.text_input("Ask a research question:")

if st.button("Get Answer"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching across uploaded PDFs and generating answer..."):
            results = collection.query(
                query_texts=[question],
                n_results=5
            )

            context = "\n\n".join(results["documents"][0])

            prompt = f"""
You are a biomedical research assistant.

Answer the question using ONLY the context below.
If the answer is not in the context, say:
"If the context partially answers the question, answer only from the available context and clearly say what is not provided."

Question:
{question}

Context:
{context}
"""

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            answer = response.choices[0].message.content

        st.subheader("Answer")
        st.write(answer)

        st.subheader("Retrieved Evidence")
        for i, doc in enumerate(results["documents"][0], start=1):
            metadata = results["metadatas"][0][i - 1]

            st.markdown(f"**Source Chunk {i}**")
            st.write(f"Source: {metadata.get('source', 'Unknown')}")
            st.write(f"Chunk: {metadata.get('chunk', 'Unknown')}")
            st.write(doc[:900])
            st.divider()