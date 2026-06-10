import chromadb

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(path="./database/chroma_db")

collection = client.get_collection(
    name="biomedical_papers"
)

question = "What is phosphorylated tau?"

print(f"\nQuestion: {question}")

results = collection.query(
    query_texts=[question],
    n_results=3
)

print("\nTop Results:\n")

for i, doc in enumerate(results["documents"][0], start=1):
    print(f"--- Result {i} ---")
    print(doc[:500])
    print()