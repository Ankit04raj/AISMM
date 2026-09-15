# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **61. DEVELOPMENT PROCESS — ABSOLUTE RULE**  
   
 You MUST work phase-by-phase.  
   
 Do not jump directly to implementation.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeYxKTXxlomEBOIFfwTYUuwZWa2ag8AgL841uquzq8nAAC8dj05XgYLDGrT0AAAAABJRU5ErkJggg==)  
 **PHASE 0 — PROJECT DISCOVERY**  
   
 First inspect the entire repository.  
   
 Inspect:  
- directories  
- files  
- backend  
- frontend  
- database  
- ML  
- datasets  
- configuration  
- environment  
- APIs  
- tests  
- documentation  
   
 Do not modify code.  
   
 At the end produce:  
   
 PROJECT AUDIT  
   
    
   
    
   
 with:  
1. Existing architecture.  
2. Existing features.  
3. Existing APIs.  
4. Existing ML models.  
5. Existing database.  
6. Existing frontend.  
7. Existing platform integrations.  
8. Missing modules.  
9. Broken modules.  
10. Technical debt.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCj5fE1LYGfHAiAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse4egF6Y2RmtoAAAAASUVORK5CYII=)  
 **PHASE 1 — REQUIREMENT MAPPING**  
   
 Create:  
   
 AISMM REQUIREMENT MATRIX  
   
    
   
    
   
 Columns:  
   
 | |  
   
 |-|  
   
 | **RequirementResearchExistingTargetStatus** |  
   
    
   
 Status:  
   
 NOT STARTED  
   
  PARTIAL  
   
  IMPLEMENTED  
   
  TESTED  
   
  VERIFIED  
   
    
   
    
   
 Do not modify code yet.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNSEPcTKpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaI0EMPwDEBYAAAAASUVORK5CYII=)  
 **PHASE 2 — ARCHITECTURE DESIGN**  
   
 Design:  
- Core architecture  
- Platform adapter architecture  
- AI architecture  
- Database architecture  
- Event architecture  
- API architecture  
- Frontend architecture  
- Model architecture  
- Security architecture  
   
 Produce architecture diagrams in text/Markdown.  
   
 WAIT FOR APPROVAL BEFORE MAJOR IMPLEMENTATION.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBCzpfFRoQwYwEZiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AMTNBeIRF+XQAAAAAElFTkSuQmCC)  
 **PHASE 3 — CORE FOUNDATION**  
   
 Implement:  
- configuration  
- database  
- authentication  
- logging  
- error system  
- platform registry  
- base adapter  
- capability system  
- normalized data models  
   
 Run tests.  
   
 Do not implement every platform yet.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeIMcSol8GM5hAr+CfClmDLzOzVGQAAf3Gt1VYdH0cAAHjvfgAulwQ+/PA0twAAAABJRU5ErkJggg==)  
 **PHASE 4 — FIRST PLATFORM**  
   
 Choose the strongest/currently available platform integration as the reference implementation.  
   
 Implement it completely through the adapter architecture.  
   
 Use it to validate:  
   
 BaseAdapter  
   
  ↓  
   
  PlatformAdapter  
   
  ↓  
   
  Registry  
   
  ↓  
   
  API  
   
  ↓  
   
  Database  
   
  ↓  
   
  Frontend  
   
    
   
    
   
 Do not special-case the platform inside core logic.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCzrfFis6mJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrsexOUF3zlnnqsAAAAASUVORK5CYII=)  
 **PHASE 5 — SECOND PLATFORM**  
   
 Add another platform.  
   
 The purpose is architectural validation.  
   
 If adding the second platform requires modifying large amounts of core AISMM code, STOP.  
   
 Refactor the architecture.  
   
 The goal is:  
 *Adding a platform should primarily require adding an adapter, not rewriting the application.*  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsad4FDMY9dewnkms4E2ELcGWmTmrKwAA/uLeqrU6vp4AAPDa/gDzVgM9ibrhygAAAABJRU5ErkJggg==)  
 **PHASE 6 — CONTENT MANAGEMENT**  
   
 Implement:  
- Create post  
- Edit  
- Delete  
- Upload media  
- Multi-platform selection  
- Platform-specific customization  
- Preview  
- Publishing  
- Post history  
   
 Test across available adapters.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBACveMML2NpGACyywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AL/WBEZbSwtAAAAAAElFTkSuQmCC)  
 **PHASE 7 — AI CONTENT ENGINE**  
   
 Implement:  
- Caption analysis  
- Caption recommendation  
- Hashtag recommendation  
- Platform-specific content adaptation  
- Pre-post sentiment  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBCzpfFRoQwYwEZiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AMTNBeIRF+XQAAAAAElFTkSuQmCC)  
 **PHASE 8 — SCHEDULING ENGINE**  
   
 Implement:  
- Feature engineering  
- Historical data  
- Engagement calculation  
- Model training  
- Prediction  
- Best-time recommendation  
- Schedule creation  
- Notifications  
   
 Research baseline:  
   
 Random Forest + optional XGBoost + hard voting.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAUBBAwSf8GIJVt4MRjeHFCt5EmEkw28wc1RkAAH9xrWpV+9cTAABeux8RYAQ2VTY9QwAAAABJRU5ErkJggg==)  
 **PHASE 9 — POST-POSTING INTELLIGENCE**  
   
 Implement:  
- Comment synchronization  
- Sentiment analysis  
- Temporal sentiment  
- Engagement updates  
- Alerts  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NoCx7CP8nCYwhhW8ibAl2DIze3UGAMBf3Gu1VcfXEwAAXrseorsEP/A3VNIAAAAASUVORK5CYII=)  
 **PHASE 10 — AUTO-REPLY**  
   
 Implement:  
- Comment classification  
- TF-IDF  
- Logistic Regression  
- Confidence  
- Human approval  
- Automatic reply  
- Platform adapter response  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBCzpfFgKQwYwEZiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AMTdBeB3gt3MAAAAAElFTkSuQmCC)  
 **PHASE 11 — GROWTH PREDICTION**  
   
 Implement:  
- Platform-specific growth models  
- Random Forest regression  
- R²  
- RMSE  
- Actual vs predicted visualization  
- Future engagement prediction  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAALUlEQVR4nO3OQQ0AIAwEsAMnOJ0TtOFkGngRklZBR1WtJDsAAPzizNcDAADuNcK0AyWbyd+DAAAAAElFTkSuQmCC)  
 **PHASE 12 — ANALYTICS**  
   
 Implement:  
- Overview dashboard  
- Platform comparison  
- Content analytics  
- Engagement analytics  
- Sentiment analytics  
- Temporal analytics  
- Growth analytics  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNa0PYLLpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaIUEMUQwY3IAAAAASUVORK5CYII=)  
 **PHASE 13 — AI STRATEGY ENGINE**  
   
 Combine all models.  
   
 Produce:  
   
 AI Recommendation  
   
    
   
    
   
 based on:  
- What to post.  
- Where to post.  
- When to post.  
- How to write it.  
- Which hashtags to use.  
- Expected engagement.  
- Audience sentiment.  
- What to improve.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCkLfEX4YmFDBhAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse/wsF7z5P1NkAAAAASUVORK5CYII=)  
 **PHASE 14 — MULTI-PLATFORM EXPANSION**  
   
 Add platforms one at a time.  
   
 For EVERY new platform:  
   
 Official API research  
   
  ↓  
   
  Capabilities  
   
  ↓  
   
  Authentication  
   
  ↓  
   
  Adapter  
   
  ↓  
   
  Mapper  
   
  ↓  
   
  Publisher  
   
  ↓  
   
  Analytics  
   
  ↓  
   
  Comments  
   
  ↓  
   
  Webhooks  
   
  ↓  
   
  Tests  
   
  ↓  
   
  Frontend  
   
  ↓  
   
  Integration  
   
    
   
    
   
 Do not implement a platform using unofficial APIs unless explicitly approved.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nBTGImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLm0GyCiM1ycAAAAASUVORK5CYII=)  
 **PHASE 15 — MODEL IMPROVEMENT**  
   
 After the complete pipeline works:  
   
 Evaluate:  
- Model performance  
- Data quality  
- Class imbalance  
- Feature importance  
- Drift  
- Latency  
- False positives  
- False negatives  
   
 Only then optimize models.  
   
 Do not optimize models before the basic system works end-to-end.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwZJgBKeVgjWMNCwYYCIkd9OP3zJzRMQMAAB+sfqJeroBAMCN2pTaBSQLg92+AAAAAElFTkSuQmCC)  
 **PHASE 16 — PRODUCTION HARDENING**  
   
 Implement:  
- Authentication security  
- Authorization  
- Secret management  
- Rate limiting  
- API retries  
- Error handling  
- Logging  
- Monitoring  
- Database backups  
- Model versioning  
- Audit logs  
- Health checks  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NoCx7CP8nCYwhhW8ibAl2DIze3UGAMBf3Gu1VcfXEwAAXrseorsEP/A3VNIAAAAASUVORK5CYII=)  
 **PHASE 17 — FINAL VERIFICATION**  
   
 Run complete end-to-end tests.  
   
 Verify:  
   
 Authentication ✓  
   
  Platform connection ✓  
   
  Content creation ✓  
   
  Media upload ✓  
   
  AI optimization ✓  
   
  Sentiment ✓  
   
  Scheduling ✓  
   
  Publishing ✓  
   
  Comments ✓  
   
  Auto reply ✓  
   
  Analytics ✓  
   
  Growth prediction ✓  
   
  Notifications ✓  
   
  Cross-platform workflow ✓  
   
    
   
    
   
 Only after actual tests pass may you mark the project:  
 **VERIFIED**  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3KsQ0AIRAEsUW6Ruj0GvnivhMSYmKQ7GiCGd09k3wBAOAVf+2o4wYAwE1qAdYyAy2Ap4pWAAAAAElFTkSuQmCC)  
