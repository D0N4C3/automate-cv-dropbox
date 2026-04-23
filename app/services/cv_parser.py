import io
import re

import fitz
import pdfplumber
from docx import Document


def extract_text_from_cv(filename: str, content: bytes) -> str:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        return _extract_pdf(content)
    if lowered.endswith(".docx"):
        return _extract_docx(content)
    if lowered.endswith(".doc"):
        return ""
    return ""


def _extract_pdf(content: bytes) -> str:
    text_chunks: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages[:4]:
            text_chunks.append(page.extract_text() or "")
    text = "\n".join(text_chunks).strip()
    if text:
        return text

    with fitz.open(stream=content, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc[:4])


def _extract_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)


def candidate_name_from_cv_text(text: str) -> str | None:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in lines[:8]:
        if re.search(r"\d", line):
            continue
        words = [w for w in re.split(r"\s+", line) if w]
        if 2 <= len(words) <= 4:
            return line
    return None
