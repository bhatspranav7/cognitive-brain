from backend.ingest_pdf import extract_text_from_pdf
from backend.utils.chunker import chunk_text
from backend.utils.embeddings import get_embedding

print("DEBUG STARTED")

text = extract_text_from_pdf(
    "documents/PranavFinalVelocity.pdf"
)

print("PDF TEXT LENGTH:", len(text))

chunks = chunk_text(text)

print("TOTAL CHUNKS:", len(chunks))

for i, chunk in enumerate(chunks):

    print("\n====================")
    print("CHUNK:", i)
    print("LENGTH:", len(chunk))
    print("PREVIEW:")
    print(chunk[:300])

    embedding = get_embedding(chunk)

    print("EMBEDDING TYPE:", type(embedding))

    if embedding:
        print("EMBEDDING LENGTH:", len(embedding))
    else:
        print("EMBEDDING IS EMPTY")