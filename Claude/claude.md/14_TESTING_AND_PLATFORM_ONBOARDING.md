# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **52. TESTING STRATEGY**  
   
 Every module must have tests.  
 **Unit Tests**  
   
 Test:  
- adapters  
- normalization  
- feature engineering  
- sentiment  
- scheduler  
- recommendation  
- analytics  
 **Integration Tests**  
   
 Test:  
   
 Frontend  
   
  ↓  
   
  Backend  
   
  ↓  
   
  Database  
   
  ↓  
   
  AI Engine  
   
  ↓  
   
  Platform Adapter  
   
    
   
    
 **End-to-End Test**  
   
 Test:  
   
 Create Post  
   
  ↓  
   
  AI Optimize  
   
  ↓  
   
  Sentiment  
   
  ↓  
   
  Schedule  
   
  ↓  
   
  Publish  
   
  ↓  
   
  Fetch Comment  
   
  ↓  
   
  Analyze Sentiment  
   
  ↓  
   
  Auto Reply  
   
  ↓  
   
  Update Analytics  
   
  ↓  
   
  Growth Prediction  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj5fFDpwwIgHRiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AOH4Becqws1iAAAAAElFTkSuQmCC)  
 **53. MOCK PLATFORM TESTING**  
   
 Do NOT depend on real social-media APIs for every test.  
   
 Create:  
   
 MockPlatformAdapter  
   
    
   
    
   
 It should simulate:  
- publishing  
- comments  
- analytics  
- errors  
- rate limits  
- authentication  
- unsupported features  
   
 This allows the entire AISMM system to be tested without external API availability.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwAQ20PcjJhnxgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseS2IEK0DSwRkAAAAASUVORK5CYII=)  
 **54. NEW PLATFORM ONBOARDING PROCESS**  
   
 When adding a new social platform, Claude must follow:  
 **Step 1**  
   
 Research the official platform API.  
 **Step 2**  
   
 Identify:  
- authentication  
- publishing  
- media support  
- scheduling  
- comments  
- replies  
- analytics  
- rate limits  
- webhooks  
- restrictions  
 **Step 3**  
   
 Create adapter.  
 **Step 4**  
   
 Create capability definition.  
 **Step 5**  
   
 Create data mapper.  
 **Step 6**  
   
 Create API client.  
 **Step 7**  
   
 Create tests.  
 **Step 8**  
   
 Connect to platform registry.  
 **Step 9**  
   
 Connect to frontend dynamically.  
 **Step 10**  
   
 Run integration tests.  
   
 Only then mark the platform:  
   
 IMPLEMENTED  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OUQmAABBAsSfYxZqXS2xiAAsYwAr+ibAl2DIzW3UEAMBfnGt1V/vXEwAAXrsep8IF2UErR/MAAAAASUVORK5CYII=)  
 **55. IMPORTANT PLATFORM RULE**  
   
 Never assume that "all social media platforms work the same."  
   
 Every platform has differences.  
   
 Therefore:  
   
 COMMON CORE  
   
  +  
   
  PLATFORM-SPECIFIC ADAPTER  
   
    
   
    
   
 is mandatory.  
   
 Do not force platforms into an identical feature set.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsad4FDMY9dewnkms4E2ELcGWmTmrKwAA/uLeqrU6vp4AAPDa/gDzVgM9ibrhygAAAABJRU5ErkJggg==)  
