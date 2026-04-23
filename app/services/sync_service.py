import email.utils
import logging

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Applicant
from app.services.applicant_service import applicant_exists, get_state, set_state
from app.services.attachment_service import extract_plain_text_body, extract_supported_attachments, parse_email_bytes
from app.services.classifier import classify_role
from app.services.cv_parser import extract_text_from_cv
from app.services.dropbox_service import DropboxService
from app.services.imap_service import IMAPService
from app.services.name_extractor import choose_best_name
from app.utils.helpers import parse_email_date

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self) -> None:
        self.imap_service = IMAPService()
        self.dropbox_service = DropboxService()
        logger.info("Sync service initialized")

    def run(self) -> None:
        with SessionLocal() as db:
            first_run = get_state(db, "initial_backfill_complete") != "true"

        messages = self.imap_service.fetch_messages(first_run=first_run)
        logger.info("Fetched %s messages; first_run=%s", len(messages), first_run)

        for fetched in messages:
            try:
                self._process_message(fetched.uid, fetched.raw)
                self.imap_service.mark_seen(fetched.uid)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed processing uid=%s: %s", fetched.uid, exc)

        if first_run:
            with SessionLocal() as db:
                set_state(db, "initial_backfill_complete", "true")
                db.commit()

    def _process_message(self, uid: str, raw_message: bytes) -> None:
        msg = parse_email_bytes(raw_message)
        sender = email.utils.parseaddr(msg.get("From", ""))[1]
        subject = msg.get("Subject", "")
        message_id = msg.get("Message-ID", f"uid-{uid}")
        date_applied = parse_email_date(msg.get("Date", ""))
        body = extract_plain_text_body(msg)
        role = classify_role(subject, body)

        if not role:
            logger.info("Skipping uid=%s due to missing role classification", uid)
            return

        attachments = extract_supported_attachments(msg)
        logger.info("Processing uid=%s message_id=%s role=%s attachments=%s", uid, message_id, role, len(attachments))
        if not attachments:
            logger.info("Skipping uid=%s: no supported attachments", uid)
            return

        with SessionLocal() as db:
            for attachment in attachments:
                if applicant_exists(db, message_id, attachment.filename):
                    logger.info("Duplicate skipped uid=%s file=%s", uid, attachment.filename)
                    continue

                cv_text = extract_text_from_cv(attachment.filename, attachment.content)
                name_result = choose_best_name(body=body, email_address=sender, cv_text=cv_text)
                dropbox_link = self.dropbox_service.upload_and_share(
                    filename=attachment.filename,
                    content=attachment.content,
                    role=role,
                    date_applied=date_applied,
                )

                applicant = Applicant(
                    message_id=message_id,
                    full_name=name_result.name,
                    name_confidence=name_result.confidence,
                    email=sender,
                    role=role,
                    cv_file_name=attachment.filename,
                    dropbox_link=dropbox_link,
                    date_applied=date_applied,
                    processed=True,
                )
                db.add(applicant)
                try:
                    db.commit()
                    logger.info("Saved applicant %s (%s)", applicant.full_name, applicant.role)
                except IntegrityError:
                    db.rollback()
                    logger.info("Duplicate constraint triggered for %s", attachment.filename)
