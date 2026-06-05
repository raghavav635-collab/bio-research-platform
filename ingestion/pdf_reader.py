import pdfplumber
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {i+1} ---\n"
                text += page_text

    return text


if __name__ == "__main__":
    path = "docs/sample_paper.pdf"
    result = extract_text_from_pdf(path)

    print("\n===== EXTRACTED TEXT =====\n")
    print(result[:2000])