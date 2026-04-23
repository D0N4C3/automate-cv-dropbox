import imaplib
import logging
from dataclasses import dataclass

from app.config import settings
from app.utils.retry import retry

logger = logging.getLogger(__name__)


@dataclass
class FetchedEmail:
    uid: str
    raw: bytes


class IMAPService:
    def __init__(self) -> None:
        self.server = settings.imap_server
        self.port = settings.imap_port
        self.user = settings.email_user
        self.password = settings.email_pass
        logger.info("IMAP service initialized server=%s port=%s user=%s", self.server, self.port, self.user)

    def _connect(self) -> imaplib.IMAP4_SSL:
        if not self.server or not self.user or not self.password:
            raise ValueError("IMAP credentials are not configured. Check IMAP_SERVER, EMAIL_USER, EMAIL_PASS.")
        logger.info("Connecting to IMAP server=%s port=%s", self.server, self.port)
        conn = imaplib.IMAP4_SSL(self.server, self.port)
        conn.login(self.user, self.password)
        conn.select("INBOX")
        logger.info("Connected to IMAP mailbox INBOX")
        return conn

    def fetch_messages(self, first_run: bool) -> list[FetchedEmail]:
        def _op() -> list[FetchedEmail]:
            conn = self._connect()
            try:
                since = settings.initial_backfill_date.strftime("%d-%b-%Y")
                criteria = f'(SINCE "{since}")' if first_run else "(UNSEEN)"
                status, data = conn.uid("search", None, criteria)
                logger.info("IMAP search criteria=%s status=%s", criteria, status)
                if status != "OK":
                    logger.error("IMAP search failed: %s", status)
                    return []
                uids = data[0].decode().split() if data and data[0] else []
                logger.info("IMAP search returned %s UID(s)", len(uids))
                messages: list[FetchedEmail] = []
                for uid in uids:
                    fetch_status, msg_data = conn.uid("fetch", uid, "(RFC822)")
                    if fetch_status != "OK" or not msg_data or not msg_data[0]:
                        logger.warning("IMAP fetch failed uid=%s status=%s", uid, fetch_status)
                        continue
                    raw = msg_data[0][1]
                    messages.append(FetchedEmail(uid=uid, raw=raw))
                return messages
            finally:
                conn.logout()

        return retry(_op, attempts=3, wait_seconds=2)

    def mark_seen(self, uid: str) -> None:
        def _op() -> None:
            conn = self._connect()
            try:
                conn.uid("store", uid, "+FLAGS", "(\\Seen)")
            finally:
                conn.logout()

        retry(_op, attempts=3, wait_seconds=1)
