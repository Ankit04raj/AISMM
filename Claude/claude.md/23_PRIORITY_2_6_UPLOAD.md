---
name: priority-2.6-media-upload-pipeline
description: Pipeline spec for direct file upload — SSRF-conscious, applies same HTTPS/host-allowlist validation to any stored URL
metadata:
  type: project
---

# Priority 2.6 — Media Upload Pipeline (Design Spec)

**Assessment (direct):**
- `post_service.py` lines 85-104 enforce HTTPS + host-allowlist (`MEDIA_ALLOWED_HOSTS`) + private-IP block — SSRF mitigated for URL-based media
- `core/schemas/post.py` `MediaItem` only has `url` — no `file` / `UploadFile` field
- No backend endpoint accepts `multipart/form-data`; no S3/minio/local-store configured; no frontend upload component
- User asked specifically: implement "if local upload is in scope"

**Decision:** Not in scope for this phase — no infrastructure to receive/store files. Document pipeline so it can be implemented when storage + endpoint exist.

**Pipeline spec (same SSRF validation applied to stored URL):**

1. **Receive:** `POST /api/v1/posts/media/upload` (multipart, `file: UploadFile`, `post_id` optional)
2. **Validate file:** check extension (`jpg`, `png`, `mp4`, `mov`), size cap (e.g., 50MB), content-type match
3. **Store:** write to storage (S3 / local `/uploads/{user_id}/{filename}`) → get stored URL
4. **SSRF validation (same as post_service):** stored URL must be `https://`, hostname in `MEDIA_ALLOWED_HOSTS`, no private IP, no `localhost`
5. **Record:** create `PostMedia` with `url = validated_stored_url`, or return URL to client for use in `PostPublication.media`
6. **Duplicate guard:** if same file hash already exists for user, return existing URL

**Status:** Not implemented — out of phase scope. Pipeline documented for future build.
