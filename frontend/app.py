import os
import chromadb
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
collection = chroma_client.get_collection(name="biomedical_papers")

st.set_page_config(page_title="Biomedical Research Assistant", layout="wide")

st.title("Biomedical Research Assistant")
st.write("Ask questions about the uploaded Alzheimer's research paper.")

question = st.text_input("Ask a research question:")

if st.button("Get Answer"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching paper and generating answer..."):
            results = collection.query(
                query_texts=[question],
                n_results=3
            )

            context = "\n\n".join(results["documents"][0])

            prompt = f"""
You are a biomedical research assistant.

Answer the question using ONLY the context below.
If the answer is not in the context, say:
"The provided paper context does not contain enough information."

Question:
{question}

Context:
{context}
"""

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            answer = response.choices[0].message.content

        st.subheader("Answer")
        st.write(answer)

        st.subheader("Retrieved Evidence")
        for i, doc in enumerate(results["documents"][0], start=1):
            st.markdown(f"**Source Chunk {i}:**")
            st.write(doc[:800])
            st.divider()