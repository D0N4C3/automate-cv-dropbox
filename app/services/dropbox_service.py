from datetime import datetime
import logging

import dropbox
from dropbox.files import WriteMode

from app.config import settings
from app.utils.retry import retry

logger = logging.getLogger(__name__)


class DropboxService:
    def __init__(self) -> None:
        if settings.dropbox_app_key and settings.dropbox_app_secret:
            if settings.dropbox_refresh_token:
                self.client = dropbox.Dropbox(
                    oauth2_refresh_token=settings.dropbox_refresh_token,
                    app_key=settings.dropbox_app_key,
                    app_secret=settings.dropbox_app_secret,
                )
            elif settings.dropbox_access_token:
                self.client = dropbox.Dropbox(
                    oauth2_access_token=settings.dropbox_access_token,
                    app_key=settings.dropbox_app_key,
                    app_secret=settings.dropbox_app_secret,
                )
            else:
                raise ValueError(
                    "DROPBOX_APP_KEY and DROPBOX_APP_SECRET are set, but neither "
                    "DROPBOX_REFRESH_TOKEN nor DROPBOX_ACCESS_TOKEN is configured."
                )
        elif settings.dropbox_access_token:
            self.client = dropbox.Dropbox(settings.dropbox_access_token)
        else:
            raise ValueError(
                "Configure Dropbox auth using DROPBOX_APP_KEY + DROPBOX_APP_SECRET "
                "(with DROPBOX_REFRESH_TOKEN or DROPBOX_ACCESS_TOKEN), or provide "
                "DROPBOX_ACCESS_TOKEN."
            )
        self.base_path = settings.dropbox_base_path.rstrip("/")
        logger.info("Dropbox service initialized base_path=%s", self.base_path)

    @staticmethod
    def _role_folder(role: str) -> str:
        return "Battery_Expert" if role == "Battery Expert" else "Sales_Marketing"

    def upload_and_share(self, filename: str, content: bytes, role: str, date_applied: datetime) -> str:
        folder = f"{self.base_path}/{self._role_folder(role)}/{date_applied.date().isoformat()}"
        path = f"{folder}/{filename}"
        logger.info("Uploading file to Dropbox path=%s", path)

        def _upload() -> str:
            self.client.files_create_folder_v2(folder, autorename=False)
            return ""

        try:
            retry(_upload, attempts=1)
        except Exception as exc:  # noqa: BLE001
            logger.info("Dropbox folder create skipped/failed for %s: %s", folder, exc)

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

        shared_url = retry(_store, attempts=3, wait_seconds=2)
        logger.info("Dropbox upload complete path=%s", path)
        return shared_url
