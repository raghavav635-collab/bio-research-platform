import pdfplumber
from sentence_transformers import SentenceTransformer


def extract_text_from_pdf(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    return text


print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

pdf_path = "docs/sample_paper.pdf"

print("Reading PDF...")
text = extract_text_from_pdf(pdf_path)

print("PDF loaded successfully!")

# Take first 1000 characters for initial testing
sample_text = text[:1000]

embedding = model.encode(sample_text)

print("\nEmbedding created!")
print("Vector length:", len(embedding))
print("\nFirst 10 values:")
print(embedding[:10])