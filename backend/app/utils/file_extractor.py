"""
Utility to extract raw text content from PDF, DOCX, and TXT files.
Ensures zero invention of content—only returns what was actually decoded.
"""

from pathlib import Path
from io import BytesIO
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using pypdf."""
    text_chunks: list[str] = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text.strip())
        logger.info(f"Extracted text from {len(reader.pages)} PDF pages.")
    except Exception as e:
        logger.error(f"Failed to read PDF with pypdf: {e}")
        raise ValueError(f"Could not parse PDF content: {str(e)}")

    return "\n\n".join(text_chunks)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract raw text from DOCX bytes using python-docx."""
    text_chunks: list[str] = []
    try:
        from docx import Document
        doc = Document(BytesIO(file_bytes))
        for p in doc.paragraphs:
            if p.text and p.text.strip():
                text_chunks.append(p.text.strip())
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    text_chunks.append(" | ".join(row_cells))
        logger.info(f"Extracted {len(text_chunks)} text segments from DOCX.")
    except Exception as e:
        logger.error(f"Failed to read DOCX: {e}")
        raise ValueError(f"Could not parse DOCX content: {str(e)}")

    return "\n".join(text_chunks)


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from plain text file."""
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="ignore")


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Route file to correct extractor based on extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_bytes)
    elif ext in [".txt", ".text", ".md"]:
        return extract_text_from_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Supported: .pdf, .docx, .txt")
