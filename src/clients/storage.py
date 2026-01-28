"""Supabase storage client for video uploads."""
import logging
import mimetypes
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from supabase import create_client, Client

from config.settings import settings


@dataclass
class UploadResult:
    """Result of file upload."""
    path: str  # Path in bucket (e.g., "outputs/video.mp4")
    public_url: str  # Public URL for access
    size_bytes: int
    upload_method: str  # "standard" or "tus"


class SupabaseClient:
    """Client for Supabase Storage uploads.

    Handles:
    - Standard uploads for small files (<6MB)
    - TUS resumable uploads for large files (>6MB)
    - Public URL generation
    - Correct MIME type setting

    Requires:
    - SUPABASE_URL and SUPABASE_KEY in environment
    - Storage bucket must exist and be public for URL access
    """

    # Files larger than this use TUS resumable upload
    TUS_THRESHOLD_BYTES = 6 * 1024 * 1024  # 6MB

    # Default bucket for video uploads
    DEFAULT_BUCKET = "videos"

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        bucket: Optional[str] = None
    ):
        """Initialize Supabase client.

        Args:
            url: Supabase project URL (defaults to settings.SUPABASE_URL)
            key: Supabase service role key (defaults to settings.SUPABASE_KEY)
            bucket: Storage bucket name (defaults to 'videos')
        """
        self.url = url or settings.SUPABASE_URL
        self.key = key or settings.SUPABASE_KEY

        if not self.url:
            raise ValueError("SUPABASE_URL not configured")
        if not self.key:
            raise ValueError("SUPABASE_KEY not configured")

        self.bucket = bucket or self.DEFAULT_BUCKET
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client: Client = create_client(self.url, self.key)

    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file.

        Args:
            file_path: Path to file

        Returns:
            MIME type string (e.g., 'video/mp4')
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"

    def _upload_standard(
        self,
        file_path: Path,
        destination: str,
        mime_type: str
    ) -> UploadResult:
        """Upload file using standard method.

        For files <6MB.
        """
        start = time.time()

        with open(file_path, "rb") as f:
            response = self.client.storage.from_(self.bucket).upload(
                path=destination,
                file=f,
                file_options={
                    "content-type": mime_type,
                    "upsert": "true"  # Overwrite if exists
                }
            )

        duration = time.time() - start
        file_size = file_path.stat().st_size

        # Get public URL
        public_url = self.client.storage.from_(self.bucket).get_public_url(destination)

        self.logger.info(
            f"Uploaded {destination} ({file_size / (1024*1024):.1f}MB) via standard",
            extra={
                "duration_ms": round(duration * 1000, 2),
                "size_bytes": file_size,
                "bucket": self.bucket,
                "method": "standard"
            }
        )

        return UploadResult(
            path=destination,
            public_url=public_url,
            size_bytes=file_size,
            upload_method="standard"
        )

    def _upload_tus(
        self,
        file_path: Path,
        destination: str,
        mime_type: str
    ) -> UploadResult:
        """Upload file using TUS resumable protocol.

        For files >=6MB. Supports automatic resume on failure.
        """
        from tusclient import client as tus_client

        start = time.time()
        file_size = file_path.stat().st_size

        # Extract project ID from URL
        # URL format: https://<project_id>.supabase.co
        project_id = self.url.split("//")[1].split(".")[0]
        tus_endpoint = f"https://{project_id}.supabase.co/storage/v1/upload/resumable"

        # TUS client setup
        client = tus_client.TusClient(
            tus_endpoint,
            headers={
                "Authorization": f"Bearer {self.key}",
                "x-upsert": "true"
            }
        )

        # Upload metadata includes bucket and path
        metadata = {
            "bucketName": self.bucket,
            "objectName": destination,
            "contentType": mime_type
        }

        # Create uploader with 5MB chunks (recommended)
        uploader = client.uploader(
            str(file_path),
            chunk_size=5 * 1024 * 1024,
            metadata=metadata
        )

        # Upload with progress logging
        last_logged = 0
        while uploader.offset < file_size:
            uploader.upload_chunk()

            # Log progress every 10%
            progress = (uploader.offset / file_size) * 100
            if progress - last_logged >= 10:
                self.logger.debug(
                    f"TUS upload progress: {progress:.0f}%",
                    extra={"progress": progress}
                )
                last_logged = progress

        duration = time.time() - start

        # Get public URL
        public_url = self.client.storage.from_(self.bucket).get_public_url(destination)

        self.logger.info(
            f"Uploaded {destination} ({file_size / (1024*1024):.1f}MB) via TUS",
            extra={
                "duration_ms": round(duration * 1000, 2),
                "size_bytes": file_size,
                "bucket": self.bucket,
                "method": "tus"
            }
        )

        return UploadResult(
            path=destination,
            public_url=public_url,
            size_bytes=file_size,
            upload_method="tus"
        )

    def upload(
        self,
        file_path: Path,
        destination: Optional[str] = None,
        force_tus: bool = False
    ) -> UploadResult:
        """Upload file to storage.

        Automatically chooses standard or TUS based on file size.

        Args:
            file_path: Path to file to upload
            destination: Destination path in bucket (defaults to filename)
            force_tus: Force TUS upload regardless of file size

        Returns:
            UploadResult with public URL

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If credentials not configured
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        destination = destination or file_path.name
        mime_type = self._get_mime_type(file_path)
        file_size = file_path.stat().st_size

        # Choose upload method
        use_tus = force_tus or file_size >= self.TUS_THRESHOLD_BYTES

        if use_tus:
            return self._upload_tus(file_path, destination, mime_type)
        else:
            return self._upload_standard(file_path, destination, mime_type)

    def delete(self, path: str) -> bool:
        """Delete file from storage.

        Args:
            path: Path in bucket to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            self.client.storage.from_(self.bucket).remove([path])
            self.logger.info(f"Deleted {path} from {self.bucket}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete {path}: {e}")
            return False

    def get_public_url(self, path: str) -> str:
        """Get public URL for file.

        Args:
            path: Path in bucket

        Returns:
            Public URL string
        """
        return self.client.storage.from_(self.bucket).get_public_url(path)
