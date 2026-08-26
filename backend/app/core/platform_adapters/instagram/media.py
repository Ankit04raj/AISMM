"""Instagram Media Upload Handler - Resumable/Chunked Upload."""

import os
import httpx
from typing import Optional, BinaryIO, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MediaUploadResult:
    """Result of media upload."""
    media_id: str
    media_url: str
    expires_at: Optional[str] = None


@dataclass
class UploadSession:
    """Resumable upload session state."""
    upload_session_id: str
    upload_url: str
    chunk_size: int
    total_bytes: int
    uploaded_bytes: int = 0


class InstagramMediaUploader:
    """Handles media upload to Instagram Graph API."""

    # Facebook/Instagram supports resumable upload for large files
    CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks
    MAX_SINGLE_UPLOAD = 100 * 1024 * 1024  # 100MB direct upload limit

    def __init__(self, access_token: str, ig_user_id: str, base_url: str = "https://graph.facebook.com/v19.0"):
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=120.0,
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
        return self._client

    async def upload_media(
        self,
        file_path: str,
        media_type: str = "IMAGE",
        mime_type: Optional[str] = None
    ) -> MediaUploadResult:
        """
        Upload media file. Uses direct upload for small files,
        resumable upload for large files.
        """
        file_size = os.path.getsize(file_path)

        if file_size <= self.MAX_SINGLE_UPLOAD:
            return await self._direct_upload(file_path, media_type, mime_type)
        else:
            return await self._resumable_upload(file_path, media_type, mime_type, file_size)

    async def _direct_upload(
        self,
        file_path: str,
        media_type: str,
        mime_type: Optional[str]
    ) -> MediaUploadResult:
        """Direct media upload for files <= 100MB."""
        client = await self._get_client()

        # Determine media type parameter
        media_type_param = "IMAGE" if media_type.upper() in ("IMAGE", "CAROUSEL") else "VIDEO"

        with open(file_path, "rb") as f:
            files = {
                "source": (os.path.basename(file_path), f, mime_type or "application/octet-stream")
            }
            data = {
                "media_type": media_type_param,
            }

            response = await client.post(
                f"/{self.ig_user_id}/media",
                files=files,
                data=data
            )

        if response.status_code != 200:
            raise MediaUploadError(
                f"Direct upload failed: {response.text}",
                status_code=response.status_code
            )

        result = response.json()
        return MediaUploadResult(
            media_id=result["id"],
            media_url=f"{self.base_url}/{result['id']}",
        )

    async def _resumable_upload(
        self,
        file_path: str,
        media_type: str,
        mime_type: Optional[str],
        file_size: int
    ) -> MediaUploadResult:
        """Resumable upload for large files (>100MB)."""
        client = await self._get_client()

        # Step 1: Create upload session
        session = await self._create_upload_session(file_size, media_type, mime_type)

        # Step 2: Upload chunks
        with open(file_path, "rb") as f:
            while session.uploaded_bytes < session.total_bytes:
                chunk = f.read(session.chunk_size)
                if not chunk:
                    break

                await self._upload_chunk(session, chunk)
                session.uploaded_bytes += len(chunk)

        # Step 3: Finalize upload
        return await self._finalize_upload(session)

    async def _create_upload_session(
        self,
        file_size: int,
        media_type: str,
        mime_type: Optional[str]
    ) -> UploadSession:
        """Create a resumable upload session."""
        client = await self._get_client()

        media_type_param = "VIDEO" if media_type.upper() in ("VIDEO", "REELS") else "IMAGE"

        response = await client.post(
            f"/{self.ig_user_id}/media_upload",
            json={
                "media_type": media_type_param,
                "file_size": file_size,
                "mime_type": mime_type or "video/mp4" if media_type_param == "VIDEO" else "image/jpeg",
            }
        )

        if response.status_code != 200:
            raise MediaUploadError(
                f"Create upload session failed: {response.text}",
                status_code=response.status_code
            )

        data = response.json()
        return UploadSession(
            upload_session_id=data["upload_session_id"],
            upload_url=data["upload_url"],
            chunk_size=data.get("chunk_size", self.CHUNK_SIZE),
            total_bytes=file_size,
        )

    async def _upload_chunk(self, session: UploadSession, chunk: bytes):
        """Upload a single chunk."""
        client = await self._get_client()

        headers = {
            "Content-Range": f"bytes {session.uploaded_bytes}-{session.uploaded_bytes + len(chunk) - 1}/{session.total_bytes}",
            "Content-Type": "application/octet-stream",
        }

        response = await client.post(
            session.upload_url,
            content=chunk,
            headers=headers
        )

        if response.status_code not in (200, 308):  # 308 = resume incomplete
            raise MediaUploadError(
                f"Chunk upload failed: {response.text}",
                status_code=response.status_code
            )

    async def _finalize_upload(self, session: UploadSession) -> MediaUploadResult:
        """Finalize the upload session and get media ID."""
        client = await self._get_client()

        response = await client.post(
            session.upload_url,
            headers={
                "Content-Range": f"bytes */{session.total_bytes}",
                "Content-Type": "application/octet-stream",
            },
            content=b""
        )

        if response.status_code != 200:
            raise MediaUploadError(
                f"Finalize upload failed: {response.text}",
                status_code=response.status_code
            )

        data = response.json()
        return MediaUploadResult(
            media_id=data["media_id"],
            media_url=f"{self.base_url}/{data['media_id']}",
        )

    async def create_carousel_container(
        self,
        child_media_ids: list,
        caption: Optional[str] = None,
        scheduled_at: Optional[str] = None
    ) -> str:
        """Create a carousel container from child media IDs."""
        client = await self._get_client()

        data = {
            "media_type": "CAROUSEL",
            "children": ",".join(child_media_ids),
        }

        if caption:
            data["caption"] = caption

        if scheduled_at:
            data["scheduled_publish_time"] = scheduled_at

        response = await client.post(f"/{self.ig_user_id}/media", data=data)

        if response.status_code != 200:
            raise MediaUploadError(
                f"Carousel container creation failed: {response.text}",
                status_code=response.status_code
            )

        return response.json()["id"]

    async def check_upload_status(self, container_id: str) -> Dict[str, Any]:
        """Check status of media container (for async processing)."""
        client = await self._get_client()
        response = await client.get(f"/{container_id}", params={"fields": "status_code,status"})
        return response.json()

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class MediaUploadError(Exception):
    """Media upload error."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code