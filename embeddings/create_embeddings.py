from sentence_transformers import SentenceTransformer

print("Loading model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

text = """
Accumulation of phosphorylated tau is a key pathological feature of Alzheimer's disease.
"""

embedding = model.encode(text)

print("\nEmbedding created successfully!")
print("Vector Length:", len(embedding))

print("\nFirst 10 values:")
print(embedding[:10])