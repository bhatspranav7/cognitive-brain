import fitz

from backend import config
from backend.utils.chunker import chunk_text
from backend.memory.vector_store import add_document


def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file on disk."""

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return text


def ingest_file(path, source_name=None):
    """Chunk one PDF/TXT file and upsert its chunks into the vector store.

    Chunk ids are '{filename}::{index}', so re-ingesting the same file
    updates it in place instead of creating duplicates.
    """

    path = str(path)
    source_name = source_name or path.replace("\\", "/").split("/")[-1]

    if path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(path)
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    chunks = chunk_text(text)

    stored = 0

    for chunk_index, chunk in enumerate(chunks):
        ok = add_document(
            doc_id=f"{source_name}::{chunk_index}",
            text=chunk,
            metadata={"source": source_name, "chunk": chunk_index},
        )
        if ok:
            stored += 1

    return stored


def ingest_pdfs():
    """Ingest every PDF in the documents folder."""

    pdf_files = [
        f for f in sorted(p.name for p in config.DOCS_DIR.iterdir() if p.is_file())
        if f.lower().endswith(".pdf")
    ]

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file}")

        stored = ingest_file(config.DOCS_DIR / pdf_file, source_name=pdf_file)

        print(f"Stored {stored} chunks from {pdf_file}")

    print("\nPDF ingestion complete!")


if __name__ == "__main__":
    ingest_pdfs()
