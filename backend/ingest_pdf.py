import fitz
import os

from backend.utils.chunker import chunk_text
from backend.memory.vector_store import add_document


PDF_FOLDER = "documents"


def extract_text_from_pdf(pdf_path):
    """
    Extract raw text from PDF
    """

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text


def ingest_pdfs():
    """
    Ingest all PDFs from documents folder
    """

    pdf_files = [
        f for f in os.listdir(PDF_FOLDER)
        if f.endswith(".pdf")
    ]

    doc_id = 0

    for pdf_file in pdf_files:

        pdf_path = os.path.join(PDF_FOLDER, pdf_file)

        print(f"\n📄 Processing: {pdf_file}")

        # Extract text
        text = extract_text_from_pdf(pdf_path)

        # Chunk text
        chunks = chunk_text(text)

        print(f"Generated {len(chunks)} chunks")

        # Store chunks
        for chunk_index, chunk in enumerate(chunks):

            metadata = {
                "source": pdf_file,
                "chunk": chunk_index
            }

            add_document(
                doc_id=str(doc_id),
                text=chunk,
                metadata=metadata
            )

            print(
                f"Stored chunk {chunk_index} "
                f"from {pdf_file}"
            )

            doc_id += 1

    print("\n✅ PDF ingestion complete!")


if __name__ == "__main__":
    ingest_pdfs()