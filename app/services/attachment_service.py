import email
from email.message import Message
from typing import NamedTuple


class ExtractedAttachment(NamedTuple):
    filename: str
    content: bytes


ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


def extract_supported_attachments(msg: Message) -> list[ExtractedAttachment]:
    extracted: list[ExtractedAttachment] = []
    for part in msg.walk():
        if part.get_content_disposition() != "attachment":
            continue
        filename = part.get_filename() or ""
        ext = "." + filename.lower().split(".")[-1] if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            continue
        content = part.get_payload(decode=True)
        if content:
            extracted.append(ExtractedAttachment(filename=filename, content=content))
    return extracted


def extract_plain_text_body(msg: Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")).lower():
                payload = part.get_payload(decode=True) or b""
                return payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
    payload = msg.get_payload(decode=True) or b""
    return payload.decode("utf-8", errors="ignore")


def parse_email_bytes(raw_bytes: bytes) -> Message:
    return email.message_from_bytes(raw_bytes)
