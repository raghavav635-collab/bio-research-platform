import chromadb

print("Creating ChromaDB client...")

client = chromadb.PersistentClient(path="./database/chroma_db")

collection = client.get_or_create_collection(
    name="biomedical_papers"
)

print("Collection created successfully!")

collection.add(
    documents=[
        "Phosphorylated tau accumulation is a key pathological feature of Alzheimer's disease."
    ],
    ids=["doc1"]
)

print("Document stored successfully!")

results = collection.query(
    query_texts=["What causes Alzheimer's disease?"],
    n_results=1
)

print("\nSearch Results:")
print(results["documents"])