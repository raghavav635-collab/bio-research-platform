import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
collection = chroma_client.get_collection(name="biomedical_papers")

question = "What is phosphorylated tau and why is it important in Alzheimer's disease?"

print(f"\nQuestion: {question}")

results = collection.query(
    query_texts=[question],
    n_results=3
)

context = "\n\n".join(results["documents"][0])

prompt = f"""
You are a biomedical research assistant.

Answer the question using ONLY the context below.
If the answer is not in the context, say: "The provided paper context does not contain enough information."

Question:
{question}

Context:
{context}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print("\nAnswer:\n")
print(response.choices[0].message.content)