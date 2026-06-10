import pdfplumber
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


print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

pdf_path = "docs/sample_paper.pdf"

print("Extracting text...")
text = extract_text_from_pdf(pdf_path)

print("Creating chunks...")
chunks = chunk_text(text)

print(f"Total chunks: {len(chunks)}")

embeddings = model.encode(chunks)

print(f"Embeddings created: {len(embeddings)}")

for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk[:200])
    print(f"Embedding length: {len(embeddings[i])}")