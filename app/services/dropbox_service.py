from datetime import datetime

import dropbox
from dropbox.files import WriteMode

from app.config import settings
from app.utils.retry import retry


class DropboxService:
    def __init__(self) -> None:
        if not settings.dropbox_access_token:
            raise ValueError("DROPBOX_ACCESS_TOKEN is not configured.")
        self.client = dropbox.Dropbox(settings.dropbox_access_token)
        self.base_path = settings.dropbox_base_path.rstrip("/")

    @staticmethod
    def _role_folder(role: str) -> str:
        return "Battery_Expert" if role == "Battery Expert" else "Sales_Marketing"

    def upload_and_share(self, filename: str, content: bytes, role: str, date_applied: datetime) -> str:
        folder = f"{self.base_path}/{self._role_folder(role)}/{date_applied.date().isoformat()}"
        path = f"{folder}/{filename}"

        def _upload() -> str:
            self.client.files_create_folder_v2(folder, autorename=False)
            return ""

        try:
            retry(_upload, attempts=1)
        except Exception:
            pass

        def _store() -> str:
            self.client.files_upload(content, path, mode=WriteMode("overwrite"))
            try:
                link = self.client.sharing_create_shared_link_with_settings(path)
                return link.url.replace("?dl=0", "?dl=1")
            except Exception:
                links = self.client.sharing_list_shared_links(path=path, direct_only=True).links
                if not links:
                    raise
                return links[0].url.replace("?dl=0", "?dl=1")

        return retry(_store, attempts=3, wait_seconds=2)
