import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer


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

    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="./database/chroma_db")

collection = client.get_or_create_collection(
    name="biomedical_papers"
)

pdf_path = "docs/sample_paper.pdf"

print("Reading PDF...")
text = extract_text_from_pdf(pdf_path)

print("Creating chunks...")
chunks = chunk_text(text)

print(f"Chunks created: {len(chunks)}")

print("Generating embeddings...")
embeddings = model.encode(chunks)

print("Storing in ChromaDB...")

for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    collection.add(
        documents=[chunk],
        embeddings=[embedding.tolist()],
        ids=[f"chunk_{i}"]
    )

print("Done!")
print(f"Stored {len(chunks)} chunks.")