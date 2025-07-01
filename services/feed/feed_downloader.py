import requests
from .exceptions import FeedDownloadError
import time
import logging

logger = logging.getLogger(__name__)


class FeedDownloader:
    def __init__(self, url: str, retries: int = 3, timeout: int = 30):
        self.url = url
        self.retries = retries
        self.timeout = timeout

    def download(self) -> str:
        last_error = None

        for attempt in range(self.retries):
            try:
                return self._perform_download()
            except (requests.RequestException, FeedDownloadError) as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1} of {self.retries} to download feed from {self.url} failed: {e}"
                )
                if attempt < self.retries - 1:
                    time.sleep(2**attempt)

        raise FeedDownloadError(
            f"Failed to download feed after {self.retries} attempts: {str(last_error)}"
        )

    def _perform_download(self) -> str:
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").lower()
            content = response.content.decode(response.apparent_encoding)

            if "xml" not in content_type and not content.strip().startswith("<?xml"):
                raise FeedDownloadError(f"Invalid content type: {content_type}")

            if not content.strip():
                raise FeedDownloadError("Empty response received")

            return content

        except requests.RequestException as e:
            raise FeedDownloadError(f"Connection error: {str(e)}")
