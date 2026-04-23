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

    def _connect(self) -> imaplib.IMAP4_SSL:
        conn = imaplib.IMAP4_SSL(self.server, self.port)
        conn.login(self.user, self.password)
        conn.select("INBOX")
        return conn

    def fetch_messages(self, first_run: bool) -> list[FetchedEmail]:
        def _op() -> list[FetchedEmail]:
            conn = self._connect()
            try:
                criteria = '(SINCE "01-Jan-2026")' if first_run else "(UNSEEN)"
                status, data = conn.uid("search", None, criteria)
                if status != "OK":
                    logger.error("IMAP search failed: %s", status)
                    return []
                uids = data[0].decode().split() if data and data[0] else []
                messages: list[FetchedEmail] = []
                for uid in uids:
                    fetch_status, msg_data = conn.uid("fetch", uid, "(RFC822)")
                    if fetch_status != "OK" or not msg_data or not msg_data[0]:
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
