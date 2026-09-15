# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **67. NO FAKE IMPLEMENTATION**  
   
 Never use fake functionality to claim completion.  
   
 Avoid:  
   
 TODO  
   
  pass  
   
  return fake data  
   
  mock response in production  
   
  hard-coded analytics  
   
  fake prediction  
   
  fake API success  
   
    
   
    
   
 Mocks are allowed ONLY inside tests/development environments.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsSeYxKS/i8VMIZ7ECt5E2BJsmZmt2gMA4C+Otbqr8+sJAACvXQ85RgYXbDJ3DwAAAABJRU5ErkJggg==)  
 **68. NO FABRICATED API SUPPORT**  
   
 If an API capability is unavailable:  
   
 Say:  
   
 NOT SUPPORTED BY PLATFORM  
   
    
   
    
   
 Do not pretend it works.  
   
 If API credentials are missing:  
   
 Say:  
   
 IMPLEMENTED BUT NOT CONNECTED  
   
    
   
    
   
 If integration is untested:  
   
 Say:  
   
 IMPLEMENTED — NOT VERIFIED  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/jzVsYQKvNrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4D+Bc7pl4pfAAAAAElFTkSuQmCC)  
 **69. STATUS SYSTEM**  
   
 Every feature should have one of:  
   
 PLANNED  
   
  IN DEVELOPMENT  
   
  IMPLEMENTED  
   
  TESTED  
   
  VERIFIED  
   
  BLOCKED  
   
  NOT SUPPORTED  
   
    
   
    
   
 This status must be visible in the checkpoint.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsSeYxKS/i8VMIZ7ECt5E2BJsmZmt2gMA4C+Otbqr8+sJAACvXQ85RgYXbDJ3DwAAAABJRU5ErkJggg==)  
 **70. FINAL FEATURE MATRIX**  
   
 At the end create:  
   
 | |  
   
 |-|  
   
 | **FeatureStatusPlatform SupportAI ModelTestsNotes** |  
   
    
   
 Example:  
   
 | Intelligent Scheduling | VERIFIED | Multi-platform | RF + XGB | PASS | Platform-aware |  
   
    
   
  | Sentiment | VERIFIED | Multi-platform | VADER + kNN | PASS | Dual phase |  
   
    
   
  | Auto Reply | TESTED | Platform dependent | TF-IDF + LR | PASS | Human fallback |  
   
    
   
  | Growth | VERIFIED | Platform-specific | RF Regressor | PASS | R² tracked |  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNSEPcTKpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaI0EMPwDEBYAAAAASUVORK5CYII=)  
 **71. IMPORTANT DISTINCTION**  
   
 Always distinguish:  
 **Research result**  
   
 What the paper reported.  
 **Current implementation result**  
   
 What the code actually produces.  
 **Target result**  
   
 What we want to achieve.  
   
 Never use a research-paper accuracy as proof that the current implementation has achieved that accuracy.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBCzpfFRoQwYwEZiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AMTNBeIRF+XQAAAAAElFTkSuQmCC)  
 **72. FINAL ARCHITECTURAL TARGET**  
   
 The final AISMM system should look conceptually like:  
   
                          USER  
   
                            |  
   
                            ↓  
   
                    AISMM WEB DASHBOARD  
   
                            |  
   
            ┌───────────────┴────────────────┐  
   
            │                                │  
   
     CONTENT MANAGEMENT                ANALYTICS  
   
            │                                │  
   
            ↓                                ↓  
   
     AI CONTENT ENGINE              ANALYTICS ENGINE  
   
            │                                │  
   
            ├── Caption                    │  
   
            ├── Hashtag                    │  
   
            └── Sentiment                  │  
   
                                             
   
                            ↓  
   
                     AI INTELLIGENCE  
   
                            |  
   
          ┌─────────────────┼─────────────────┐  
   
          │                 │                 │  
   
     Scheduling        Sentiment          Prediction  
   
          │                 │                 │  
   
          ├──────────── Auto Reply ──────────┤  
   
          │                                   │  
   
          └──────── Recommendation ───────────┘  
   
                            |  
   
                            ↓  
   
                    PLATFORM REGISTRY  
   
                            |  
   
        ┌──────────┬────────┼────────┬──────────┐  
   
        ↓          ↓        ↓        ↓          ↓  
   
   Instagram   Facebook     X     LinkedIn   YouTube  
   
   Adapter      Adapter   Adapter  Adapter    Adapter  
   
        │          │        │        │          │  
   
        └──────────┴────────┴────────┴──────────┘  
   
                            |  
   
                            ↓  
   
                     EXTERNAL APIs  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCzrfFis6mJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrsexOUF3zlnnqsAAAAASUVORK5CYII=)  
 **73. THE GOLDEN RULE**  
   
 Always remember:  
 ***AISMM Core should contain intelligence. Platform adapters should contain platform-specific complexity.***  
   
 If Instagram changes its API:  
   
 Modify Instagram Adapter.  
   
    
   
    
   
 If LinkedIn changes its API:  
   
 Modify LinkedIn Adapter.  
   
    
   
    
   
 If a new platform is added:  
   
 Create New Adapter.  
   
    
   
    
   
 If the sentiment model changes:  
   
 Replace Sentiment Engine implementation.  
   
    
   
    
   
 If the scheduling model changes:  
   
 Replace Scheduling Model.  
   
    
   
    
   
 The rest of the application should continue working.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nBTGImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLm0GyCiM1ycAAAAASUVORK5CYII=)  
 **74. FINAL DEVELOPMENT LOOP**  
   
 For every feature, follow exactly:  
1. UNDERSTAND  
   
         ↓  
   
  2. INSPECT  
   
         ↓  
   
  3. PLAN  
   
         ↓  
   
  4. DESIGN  
   
         ↓  
   
  5. IMPLEMENT  
   
         ↓  
   
  6. TEST  
   
         ↓  
   
  7. DEBUG  
   
         ↓  
   
  8. VERIFY  
   
         ↓  
   
  9. UPDATE CLAUDE.md  
   
         ↓  
   
  10. COMMIT  
   
         ↓  
   
  11. PUSH TO GITHUB  
   
         ↓  
   
  12. VERIFY PUSH  
   
         ↓  
   
  13. MOVE TO NEXT STEP  
   
    
   
    
   
 Never skip:  
   
 TEST  
   
  VERIFY  
   
  UPDATE CLAUDE.md  
   
  COMMIT  
   
  PUSH TO GITHUB  
   
  VERIFY PUSH  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNhRgDScML2OlGADCywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AKKbBEPB3vbSAAAAAElFTkSuQmCC)  
 **75. FIRST COMMAND**  
   
 When this master prompt is provided to you, DO NOT start coding immediately.  
   
 Your first task is ONLY:  
 **AISMM PROJECT AUDIT**  
   
 Perform:  
2. Inspect repository.  
   
  2. Inspect backend.  
   
  3. Inspect frontend.  
   
  4. Inspect database.  
   
  5. Inspect ML modules.  
   
  6. Inspect datasets.  
   
  7. Inspect APIs.  
   
  8. Inspect authentication.  
   
  9. Inspect tests.  
   
  10. Inspect configuration.  
   
  11. Inspect documentation.  
   
  12. Read CLAUDE.md if present.  
   
  13. Check git status.  
   
    
   
    
   
 Then produce:  
 **AISMM CURRENT STATE REPORT**  
   
 with:  
   
 A. Architecture  
   
  B. Existing Features  
   
  C. Platform Integrations  
   
  D. AI/ML Modules  
   
  E. Database  
   
  F. Frontend  
   
  G. Backend  
   
  H. APIs  
   
  I. Testing  
   
  J. Missing Features  
   
  K. Broken Features  
   
  L. Technical Debt  
   
  M. Security Issues  
   
  N. Platform Extensibility Problems  
   
  O. Recommended Phase Order  
   
    
   
    
   
 DO NOT make major code changes during the audit.  
   
 After the audit, update CLAUDE.md with the current project state, then:  
3. Run tests that are applicable to the audit.  
4. Run git status.  
5. Review the diff.  
6. Commit the audit/state update.  
7. Push the commit to GitHub.  
8. Verify the push.  
9. Present the plan.  
   
 Then stop and wait for the next instruction before beginning the next major phase.  
   
 Wait for the next instruction before beginning the next major phase.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCUZfDq7YGVDAgAU2QtIq6DIzW7UHAMBfHGt1V+fXEwAAXrseHCgGBJWaMWkAAAAASUVORK5CYII=)  
