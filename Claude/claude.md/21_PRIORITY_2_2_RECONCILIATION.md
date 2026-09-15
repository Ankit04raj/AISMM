---
name: priority-2.2-scheduler-reconciliation
description: Reconciliation design for ambiguous scheduler failures (timeout/network drop) — query upstream before marking failed, avoid false negatives and duplicate posts
metadata:
  type: project
---

# Priority 2.2 — Scheduler Network-Failure Reconciliation (Design)

**Gap:** `scheduling_service.execute_due_schedules` catches all exceptions (line 158–161), sets `publication.status = 'failed'`, and never checks whether the upstream post actually succeeded before the network drop/timeout. This creates false negatives (post exists on platform but locally marked failed) and allows duplicate retries.

**Reconciliation design (no adapter changes needed for v1):**

1. **Distinguish ambiguous vs. certain failure** at exception site (line 158):
   - `TimeoutError`, `ConnectionDrop`, `ConnectionRefused`, `OSError` with `errno.ETIMEOUT` / `ECONNRESET` / `EPIPE` → ambiguous (request may have reached platform)
   - `HTTPException` 4xx, validation errors, provider explicit "failed" → certain (no upstream success)

2. **Reconciliation query (only for ambiguous)** — run inside the existing `except` block before setting `status='failed'`:
   - Try `adapter.get_post(...)` if adapter exposes a lookup by platform_post_id or by content/text/time window
   - Since `get_post` requires `post_id`, add a lightweight `search_recent_posts(text, since)` on adapter base, or use `adapter.get_post` when `platform_post_id` was assigned (it won't be — that's the failure case). **Alternative:** query the platform using adapter's internal client for recent posts matching the caption/text + approximate time window.
   - If a matching post is found → set `publication.status = 'published'`, set `platform_post_id = found.id`, mark success, skip failure.
   - If no match found after reconciliation → mark `failed` as before.

3. **Duplicate guard:** Before any retry (whether automatic or operator-triggered), always check `platform_post_id` — if already set to an upstream ID, do NOT call `adapter.publish_post` again.

4. **Implementation note:** Base adapter (`base.py:203`) has `get_post(post_id)` — needs an upstream-search method or we wrap adapter client directly in the reconcile step. The reconciliation is best kept inside `execute_due_schedules`, not in adapter contract, to avoid modifying every adapter.

**Status:** Design complete; requires adapter-side `search_recent` or direct client query before implementation.
