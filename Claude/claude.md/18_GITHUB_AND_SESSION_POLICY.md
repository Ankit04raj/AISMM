# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **65. GITHUB — EVERY SESSION MUST BE PUSHED**  
   
 GitHub is the permanent remote history of AISMM.  
   
 This is a MANDATORY rule:  
 ***EVERY CLAUDE CODE SESSION MUST END WITH THE CURRENT PROJECT STATE COMMITTED AND PUSHED TO GITHUB.***  
   
 Do NOT interpret this as "push only after major phases."  
   
 Push after EVERY session.  
   
 A session may be:  
- a full implementation session  
- a debugging session  
- a research/API investigation session  
- a documentation session  
- a short recovery session  
- a token/context-loss continuation  
- a test-only session  
- a refactoring session  
   
 Even if no production code changes, the session must update this CLAUDE.md with the session result, current status, and next action, then commit and push that documentation change.  
 **Mandatory Session-End Pipeline**  
   
 At the end of EVERY session:  
   
 WORK  
   
   ↓  
   
  TEST  
   
   ↓  
   
  VERIFY  
   
   ↓  
   
  UPDATE CLAUDE.md  
   
   ↓  
   
  REVIEW git diff  
   
   ↓  
   
  CHECK FOR SECRETS  
   
   ↓  
   
  git add  
   
   ↓  
   
  git commit  
   
   ↓  
   
  git push  
   
   ↓  
   
  VERIFY PUSH  
   
   ↓  
   
  REPORT COMMIT + PUSH STATUS  
   
    
   
 There must be NO normal session ending with:  
   
 "we will push later"  
   
  "push in the next session"  
   
  "code is saved locally"  
   
  "GitHub can be updated later"  
   
    
   
 If the push fails, the session is NOT considered fully synchronized.  
   
 You must diagnose the failure or clearly record:  
   
 GITHUB SYNC: FAILED  
   
  REASON:   
   
  RECOVERY ACTION:   
   
    
   
 Then leave the repository in a recoverable state.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNhRgDCMMPyOlGADCywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AKKrBEE79VWHAAAAAElFTkSuQmCC)  
 **65.1 CLAUDE.md SESSION LOG**  
   
 Because CLAUDE.md is the SINGLE SOURCE OF TRUTH, append a compact session record to this same file after every session.  
   
 Use:  
**SESSION HISTORY**  
   
   
  ### SESSION-XXX — YYYY-MM-DD HH:MM  
   
    
   
  **Phase:**   
   
    
   
  **Objective:**  
   
    
   
  **Completed:**  
   
  - ...  
   
    
   
  **Files Created:**  
   
  - ...  
   
    
   
  **Files Modified:**  
   
  - ...  
   
    
   
  **Tests:**  
   
  -  — PASS/FAIL  
   
    
   
  **Issues Fixed:**  
   
  - ...  
   
    
   
  **Known Issues:**  
   
  - ...  
   
    
   
  **Architecture Decisions:**  
   
  - ...  
   
    
   
  **Platform Status:**  
   
  - Instagram:  
   
  - Facebook:  
   
  - X:  
   
  - LinkedIn:  
   
  - YouTube:  
   
  - Other:  
   
    
   
  **ML Status:**  
   
  - Scheduling:  
   
  - Sentiment:  
   
  - Auto Reply:  
   
  - Growth:  
   
  - Caption:  
   
  - Hashtag:  
   
    
   
  **Current Status:** <PLANNED / IN DEVELOPMENT / IMPLEMENTED / TESTED / VERIFIED / BLOCKED>  
   
    
   
  **NEXT ACTION:**  
   
    
   
  **Git Commit:**  
   
    
   
  **GitHub Push:** VERIFIED / FAILED  
   
    
   
  **Recovery Note:**  
   
    
   
 Never delete previous session history.  
   
 Never rewrite old session entries to make history look cleaner.  
   
 Append a new entry for every session.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUeCFISeISz9CRVMWGAjJK2CbjNzVGcAAPzF2qu7Wl9PAAB47XoA/vsF8SxXdngAAAAASUVORK5CYII=)  
 **65.2 SESSION NUMBERING**  
   
 Session numbers must never be reused.  
   
 Before starting a session:  
   
 grep -n "^### SESSION-" CLAUDE.md | tail  
   
    
   
 Find the latest session number and increment it.  
   
 Example:  
   
 SESSION-017  
   
    
   
 next:  
   
 SESSION-018  
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNa0PYLLpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaIUEMUQwY3IAAAAASUVORK5CYII=)  
 **65.3 COMMIT REQUIREMENT**  
   
 Every session must produce a meaningful Git commit.  
   
 If production code changed:  
   
 git add  CLAUDE.md  
   
  git commit -m "feat(): "  
   
    
   
 If only documentation/state changed:  
   
 git add CLAUDE.md  
   
  git commit -m "docs: update AISMM session "  
   
    
   
 If tests were added:  
   
 git commit -m "test(): "  
   
    
   
 If a bug was fixed:  
   
 git commit -m "fix(): "  
   
    
   
 Never use meaningless messages:  
   
 update  
   
  changes  
   
  final  
   
  done  
   
  test  
   
  work  
   
  new  
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUfyRbBh9UygEBGsWGAjJK2CbjNzVGcAAPzFtapV7V9PAAB47X4AEWwEMDZQj+QAAAAASUVORK5CYII=)  
 **65.4 PUSH REQUIREMENT**  
   
 After the commit:  
   
 git push  
   
    
   
 If the branch is not configured:  
   
 git push -u origin   
   
    
   
 Do NOT create a new remote repository automatically.  
   
 Do NOT change the remote URL without checking it first.  
   
 First inspect:  
   
 git remote -v  
   
  git branch --show-current  
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OYQ1AABSAwc+mi5ovkwR6CCCAAir4Z7a7BLfMzFYdAQDwF+da3dX+9QQAgNeuB54hBdTlMOKbAAAAAElFTkSuQmCC)  
 **65.5 PUSH VERIFICATION**  
   
 After pushing:  
   
 git status  
   
  git log -1 --oneline  
   
  git branch -vv  
   
    
   
 Confirm:  
   
 working tree clean  
   
  latest commit exists  
   
  branch is synchronized with remote  
   
    
   
 Then update the session entry in CLAUDE.md with:  
   
 GitHub Push: VERIFIED  
   
    
   
 If updating that final status creates another change, amend the commit and push again:  
   
 git add CLAUDE.md  
   
  git commit --amend --no-edit  
   
  git push --force-with-lease  
   
    
   
 ONLY use --force-with-lease when necessary for this exact final documentation update and NEVER use plain --force.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNSEPcTKpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaI0EMPwDEBYAAAAASUVORK5CYII=)  
 **65.6 GITHUB SAFETY — NEVER PUSH SECRETS**  
   
 Before EVERY push inspect staged changes:  
   
 git diff --cached  
   
    
   
 Never push:  
- .env  
- API keys  
- OAuth client secrets  
- access tokens  
- refresh tokens  
- passwords  
- private certificates  
- SSH private keys  
- service-account private keys  
- database credentials  
- personal authentication cookies  
   
 Maintain .env.example with placeholder variable names only.  
   
 If a secret is accidentally staged:  
1. Unstage it.  
2. Remove it from the commit.  
3. If it was already pushed, STOP and report it immediately.  
4. Never pretend the repository is safe.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAALUlEQVR4nO3OQQ0AIAwEsAMnOJ0TtOFkGngRklZBR1WtJDsAAPzizNcDAADuNcK0AyWbyd+DAAAAAElFTkSuQmCC)  
 **65.7 GITHUB PUSH FAILURE**  
   
 If:  
   
 git push  
   
    
   
 fails:  
   
 DO NOT claim success.  
   
 Record:  
   
 GitHub Push: FAILED  
   
    
   
 and the exact error category:  
   
 authentication  
   
  network  
   
  remote  
   
  permission  
   
  branch  
   
  rejected/non-fast-forward  
   
  merge conflict  
   
  repository unavailable  
   
    
   
 Then attempt safe recovery.  
   
 Never delete local commits merely to make the push succeed.  
   
 Never reset or force-push blindly.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj5fFSLwwIgHRiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AOIIBeU3YHe1AAAAAElFTkSuQmCC)  
 **65.8 TOKEN / CONTEXT LOSS**  
   
 If the session is ending because of token/context limits:  
   
 DO NOT begin another large feature.  
   
 Immediately:  
5. Save the current work.  
6. Run tests that are practical.  
7. Update CLAUDE.md.  
8. Append the current session entry.  
9. Record exactly where implementation stopped.  
10. Record incomplete files/operations.  
11. Record exact NEXT ACTION.  
12. Commit.  
13. Push.  
14. Verify the push.  
   
 The next Claude session MUST continue from that state.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4EMxgBTP+ANa0hxW8ibAl2DIzR3UFAMBf3Gu1VefXEwAAXtsfSrADVc4vuNIAAAAASUVORK5CYII=)  
 **65.9 CRASH RECOVERY**  
   
 If Claude crashes before completing the session:  
   
 The next session must inspect:  
   
 git status  
   
  git diff  
   
  git log --oneline -10  
   
    
   
 Then inspect CLAUDE.md.  
   
 Do NOT blindly revert changes.  
   
 Determine:  
   
 What survived?  
   
  What was committed?  
   
  What was pushed?  
   
  What was partially implemented?  
   
  What tests passed?  
   
  What is the safest next action?  
   
    
   
 Then append a recovery session entry to CLAUDE.md, commit it, and push it.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsScYxaA/kYnEkyk8WcGbCFuCLTOzVXsAAPzFuVZ3dXw9AQDgtesB/wMF8E2xUQwAAAAASUVORK5CYII=)  
 **65.10 GITHUB HISTORY MUST BE RECOVERABLE**  
   
 At any time, deleting the Claude conversation must NOT destroy project continuity.  
   
 A new Claude session must be able to reconstruct the state from:  
   
 GitHub repository  
   
  +  
   
  CLAUDE.md  
   
  +  
   
  Git commit history  
   
    
   
 The chat history is NOT a project dependency.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeImMIAprwCtjSIFfwTYUuwZWaO6goAgL+412qrzq8nAAC8tj8teQNNLCV0wAAAAABJRU5ErkJggg==)  
 **65.11 DO NOT OVERWRITE SESSION HISTORY**  
   
 Never replace the entire CLAUDE.md with only the latest state.  
   
 Preserve:  
   
 MASTER RULES  
   
  +  
   
  CURRENT PROJECT STATE  
   
  +  
   
  SESSION HISTORY  
   
    
   
 The file should grow chronologically.  
   
 Keep session entries concise enough that CLAUDE.md remains usable.  
   
 If the history becomes extremely large, archive old entries ONLY when explicitly instructed by the user. Do not silently delete history.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSfYxZo/lUeLGMACBrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA6fSBddgdNMlAAAAAElFTkSuQmCC)  
 **65.12 GIT CHECKPOINTS**  
   
 After every stable change:  
   
 git status  
   
  git diff --stat  
   
  git diff  
   
    
   
 Run tests.  
   
 Then commit and push.  
   
 A "stable change" does NOT replace the mandatory end-of-session push.  
   
 The rule is:  
 ***Stable change → commit/push. Every session → commit/push.***  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OYQ1AABSAwY8JIIKoL4Z8Eoiggn9mu0twy8wc1RkAAH9xbdVa7V9PAAB47X4A9DIEIm50tIwAAAAASUVORK5CYII=)  
 **65.13 BRANCH SAFETY**  
   
 Before modifying or pushing:  
   
 git remote -v  
   
  git branch --show-current  
   
  git status  
   
    
   
 Default stable branch:  
   
 main  
   
    
   
 Use feature branches when appropriate.  
   
 Never silently switch branches.  
   
 Never delete branches.  
   
 Never force-push main.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/jzVsYQKvNrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4D+Bc7pl4pfAAAAAElFTkSuQmCC)  
 **65.14 GITHUB IS THE PERMANENT PROJECT TIMELINE**  
   
 The GitHub history should make it possible to understand:  
   
 SESSION-001  
   
      ↓  
   
  SESSION-002  
   
      ↓  
   
  SESSION-003  
   
      ↓  
   
  ...  
   
      ↓  
   
  CURRENT SESSION  
   
    
   
 Each session should have:  
   
 commit  
   
  +  
   
  CLAUDE.md state  
   
  +  
   
  tests  
   
  +  
   
  next action  
   
    
   
 Therefore the project can be safely continued even if:  
- Claude loses context  
- Claude compacts context  
- Claude Code restarts  
- the terminal closes  
- the conversation is deleted  
- a new Claude session is opened  
- another developer clones the repository  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NoCpTCQ/pwmMYQVvImwJtszMXp0BAPAX91pt1fH1BACA164HosMEPiBLnfkAAAAASUVORK5CYII=)  
 **65.15 FINAL SESSION-END CHECKLIST**  
   
 Before saying "session complete", Claude MUST verify:  
   
 [ ] Work completed or safely checkpointed  
   
  [ ] Tests executed where applicable  
   
  [ ] Known failures documented  
   
  [ ] CLAUDE.md updated  
   
  [ ] Session number recorded  
   
  [ ] Current phase recorded  
   
  [ ] NEXT ACTION recorded  
   
  [ ] Git status checked  
   
  [ ] Git diff reviewed  
   
  [ ] Staged files reviewed  
   
  [ ] Secrets checked  
   
  [ ] Commit created  
   
  [ ] Git push executed  
   
  [ ] Push result verified  
   
  [ ] Commit hash recorded in CLAUDE.md  
   
  [ ] GitHub status recorded  
   
    
   
 Only then may the session be considered complete.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsSeYxKS/jL3MIJ7FCt5E2BJsmZmt2gMA4C+Otbqr8+sJAACvXQ85UgYR8skzMQAAAABJRU5ErkJggg==)  
 **65.16 ABSOLUTE RULE**  
 ***EVERY SESSION → UPDATE CLAUDE.md → COMMIT → PUSH → VERIFY.***  
   
 No exceptions unless GitHub itself is unavailable.  
   
 If GitHub is unavailable, preserve all local work and explicitly record:  
   
 GITHUB SYNC: BLOCKED  
   
    
   
 Then the FIRST task of the next session must be to synchronize the repository before starting unrelated development.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNa0PYLLpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaIUEMUQwY3IAAAAASUVORK5CYII=)  
 **END GITHUB EVERY-SESSION POLICY**  
 **66. GIT CHECKPOINTS**  
   
 After every stable phase:  
   
 git status  
   
  git diff  
   
    
   
    
   
 Run tests.  
   
 Then create a meaningful commit.  
   
 Example:  
   
 feat(core): add platform adapter architecture  
   
    
   
    
   
 or:  
   
 feat(scheduling): implement ML scheduling engine  
   
    
   
    
   
 Never create meaningless commits such as:  
   
 update  
   
  changes  
   
  final  
   
  test  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQ2AQBAAsSE5Cfyxui4QiAQMYIEfIWkVdJuZozoDAOAvrlWtav96AgDAa/cDEXgEKqdm9sAAAAAASUVORK5CYII=)  
