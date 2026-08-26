def _split_long(text, chunk_size, overlap):
    """Hard-split text with no usable paragraph breaks (typical for PDF
    extraction, which yields single newlines) at word boundaries, keeping
    a little overlap so facts on a boundary are never lost."""

    words = text.split()

    pieces = []
    piece = ""

    for word in words:
        if piece and len(piece) + len(word) + 1 > chunk_size:
            pieces.append(piece)

            if overlap > 0:
                tail = piece[-overlap:]
                cut = tail.find(" ")
                piece = tail[cut + 1:] if cut != -1 else ""
            else:
                piece = ""

        piece = f"{piece} {word}".strip()

    if piece:
        pieces.append(piece)

    return pieces


def chunk_text(text, chunk_size=700, overlap=100):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if len(paragraph) >= chunk_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""

            chunks.extend(_split_long(paragraph, chunk_size, overlap))

        elif len(current_chunk) + len(paragraph) < chunk_size:
            current_chunk += paragraph + "\n\n"

        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            current_chunk = paragraph + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
