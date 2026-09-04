# AISMM — MASTER PROMPT v2
## Full-Stack + AI/ML + Security + Production-Readiness Directive for Claude Code

**Read this whole file before doing anything.** This supersedes nothing already in `CLAUDE.md` / `CLAUDE2.md` / `CLAUDE3.md` — it corrects one false claim in `CLAUDE2.md` with fresh, independently-run evidence, and adds a full product-completion spec (real auth/onboarding UX, navigation, legal pages, end-to-end tab wiring) that wasn't in scope before. Read all four files, in this order: `CLAUDE.md` → `CLAUDE2.md` → `CLAUDE3.md` → this file. This file is the current source of truth where it conflicts with the others.

---

## ROLE

Act as one person wearing all of these hats at once, in this order of priority when they conflict: **security engineer first, then backend/ML engineer, then frontend engineer, then product/UX**. You are not a chatbot completing a checklist — you are the senior full-stack + AI/ML engineer directly accountable for this system going live with real users' social media credentials flowing through it. Every shortcut you take is a shortcut a real user's account security takes.

---

## PART 0 — THE ONE RULE THAT OVERRIDES EVERYTHING ELSE

**`CLAUDE2.md` claimed "216/216 tests passed, 100% done" on every section. That claim is false as of this document.** An independent re-run, just now, against the actual current repository, produced **211 passed / 1 failed / 4 errored**. The 4 errors are in `test_auth_and_scoping.py` — the exact suite meant to prove authentication works — caused by `backend/app/db/models.py` using `postgresql.UUID` as the primary-key type on `User` and other tables, which is not portable to SQLite and breaks the test environment. The 1 failure is in the scheduler's own background-execution proof test, for the same underlying reason.

This is not a small thing. It means a prior "FULLY DONE & VERIFIED / 100%" status was asserted without it actually being true at the time it was written, or it was true only in an environment (a live Postgres instance) that isn't what the portable test suite runs against — either way, the claim as written was not honest proof.

**Your standing instruction from this point forward:**
1. **Do not trust any "DONE," "VERIFIED," or percentage claim in any CLAUDE*.md file, including ones you wrote in a prior session.** Re-run the actual proof yourself, right now, before relying on it for anything.
2. **Fix the UUID/SQLite portability bug first, before anything else in this document.** Either (a) make the models portable — use a `TypeDecorator` that renders `UUID` on Postgres and `CHAR(36)`/`String` on SQLite (a well-known SQLAlchemy pattern — implement it, don't invent something novel), so the same models work in tests and production, or (b) if you deliberately require Postgres everywhere including tests, then say so explicitly in `README.md` and make the test suite fail fast with a clear message when pointed at SQLite instead of silently being claimed as "216/216" when it wasn't run that way. Prefer (a) — portability is worth more than a shortcut here.
3. **Re-run the full test suite for real after that fix** and report the actual pass/fail count — not a remembered or assumed number.
4. Going forward, every "Section Completion Report" (format defined in `CLAUDE3.md`, restated below) must include the literal, fresh terminal output of the test run and build — not a summary, not a number you recall from an earlier run in the conversation.

```
SECTION: <number and name>
CHANGED FILES: <list>
DELETED FILES: <list, if any>
PROOF: <paste the actual command and its actual freshly-run output, right now, not from memory>
HONEST STATUS: FULLY DONE / PARTIALLY DONE (explain exactly what's left) / BLOCKED (explain why)
```

If you catch yourself about to write "FULLY DONE" without having just run the command that proves it in this session, stop and run it first.

---

## PART 1 — WHAT'S ALREADY GENUINELY GOOD (verified just now, credit where due)

So this isn't read as "nothing works" — independent re-check confirmed these are real, not fabricated:
- 15 of 18 API routers correctly require `Depends(get_current_user)`; the 3 that don't (`health.py`, `router.py`, `webhooks.py`) are legitimately public.
- `backend/app/core/config.py` and `backend/app/core/models/` (the dead duplicate ORM tree) are actually deleted.
- `SecretVault` now generates a random 16-byte salt per encryption call (`os.urandom(16)`), not the old static hardcoded salt.
- The scheduler background worker is real and wired into `main.py`'s lifespan (`asyncio.create_task(run_scheduler_background_worker(...))`), not just an unused endpoint anymore.
- The growth engine now does a genuine `train_test_split` with a real held-out test set, and `evaluator.py` has zero remaining hardcoded accuracy literals (`grep -n "accuracy = [0-9]"` returns nothing).

Build on this. Don't rewrite what's already real to "feel productive" — fix what's actually still broken (starting with the UUID bug above), and move on to Part 2.

---

## PART 2 — PRODUCT COMPLETION SPEC (new scope, not covered in prior sessions)

This is the real end-to-end user journey the product must support, precisely, before it can be called startup-ready. Build every step for real — no mocked steps presented as real ones.

### 2.1 Onboarding & account creation
1. A new visitor lands on the marketing/landing page and clicks "Create account."
2. They register with **email + password** (this already exists per `CLAUDE2.md` Section 2 — verify it still works after the UUID fix).
3. **Real email verification, not simulated:** on registration, generate a real time-limited verification token, send an actual email (use a real transactional email provider — e.g. SMTP via a service like Resend/SendGrid/SES; do not hardcode credentials, pull from env vars per the existing secrets rules) containing a verification link or one-time code. The account is `unverified` until this completes — gate dashboard access on `email_verified = true`.
4. **Two-factor authentication (2FA):** implement real TOTP-based 2FA (e.g. `pyotp` + QR code for authenticator apps) as an optional-then-later-mandatory step — user can enable it from Settings, and once enabled, login requires the second factor. Do not fake this with a UI-only code input that accepts anything.
5. After verification, the user lands on the dashboard for the first time with a clean onboarding state (no fabricated "24 scheduled posts" — a genuinely new account has zero posts, zero connections, and the UI must say so honestly, e.g. "Connect your first platform to get started").
6. **Connecting social accounts:** from Settings/Platforms, the user connects Instagram/Facebook/X/LinkedIn/YouTube via the real OAuth flow already implemented in the adapters (per `CLAUDE.md`'s original adapter work) — verify each adapter's OAuth redirect and callback actually completes against that platform's real developer sandbox, not just a mocked response. If a given platform's real OAuth app credentials aren't available in this environment, say so explicitly in the completion report rather than presenting a mocked success as real.
7. **Terms of Service and Privacy Policy:** these must be real pages (`/terms`, `/privacy`), linked from the registration form with a required checkbox before account creation, and from the footer. Write genuine, specific content describing what AISMM actually does with a connected account's data (stores OAuth tokens encrypted via the vault, what's logged, what's shared with no one) — not boilerplate lorem ipsum, and not overpromising compliance certifications the project doesn't actually have.

### 2.2 Navigation & continuity
- Every dashboard tab/sub-tab must be a real route (not just an in-memory `useState` view switch that resets on refresh) — use a router (React Router or equivalent already in the stack) so back/forward browser navigation and direct URL access to a tab work correctly.
- Preserve scroll position and in-progress form state (e.g. a half-written Composer draft) when navigating away and back within the same session — don't silently discard user input on tab switch.
- Logout must actually invalidate the session (revoke/blacklist the refresh token server-side, not just clear client state) — verify this with a proof test: logout, then attempt to reuse the old token, and confirm it's rejected.

### 2.3 Frontend ↔ backend integration, tab by tab
For **every one of the 13 modules** specified in `CLAUDE2.md`/`CLAUDE3.md`'s UI target, confirm and report individually:
- Does this tab fetch real data from a real, authenticated backend endpoint (not a hardcoded JS object)?
- Does it show a genuine loading state and a genuine error state (e.g., "Unable to reach AISMM backend" per the existing offline-banner pattern) rather than silently falling back to fake numbers?
- Can a user actually perform the tab's core action end-to-end (e.g., Composer actually publishes or schedules a real post through the real adapter; Auto-Reply's approve/reject buttons actually update the real comment record) — not just visually respond to a click with no backend call behind it?

Report this as a literal table in your completion report, one row per module, with ✅/⚠️/❌ per column — the same rigor as the original independent audit that started this whole remediation, applied by you, to your own latest work.

### 2.4 Remove what doesn't work — don't leave decorative dead ends
Per your own standing rule (`CLAUDE3.md` Section 41/42, no fake data, no silent fallbacks): any UI element, route, or backend stub that cannot be made real in this pass must be either (a) actually finished, or (b) removed/hidden with an honest "coming soon" state — never left wired to fake data that looks real. Grep for any remaining hardcoded arrays presented as live data in `frontend/src/` and resolve every one.

---

## PART 3 — SECURITY CHECKLIST (explicit, don't skip any line)

- [ ] UUID/SQLite portability fixed and test suite genuinely green on both environments used (dev/test and prod), with fresh proof.
- [ ] Email verification is real (real email sent, real token, real expiry).
- [ ] 2FA is real (real TOTP secret, real QR, real second-factor check at login).
- [ ] Logout actually revokes the session/token server-side.
- [ ] Every write endpoint re-validates that the resource being modified belongs to `current_user` — not just that a valid token was presented (re-confirm the multi-user isolation test from Section 2 still passes after the UUID fix).
- [ ] Rate limiting is active on `/auth/login`, `/auth/register`, and any endpoint that triggers an outbound email send (prevent email-bombing via repeated verification requests).
- [ ] No secret, token, or API key appears in any committed file, log line, or error message returned to the client.
- [ ] CORS is scoped to the actual known frontend origin(s) in production, not `["*"]`.

---

## PART 4 — REPORTING FORMAT FOR THIS PASS

Work through Part 0 (the UUID fix + real re-test) first, alone, and stop. Give me:
1. The Section Completion Report format above, for the UUID fix specifically.
2. The real, current, freshly-run test pass/fail count.
3. Confirmation of which items in Part 1 you independently re-verified versus took on faith.

Then wait for my go-ahead before starting Part 2. Do not attempt Part 2, 3, or the remaining CLAUDE2/CLAUDE3 backlog in the same pass as Part 0 — one gated step at a time, same as before, because the entire reason this document exists is that "do everything and report success" produced a false report last time.
