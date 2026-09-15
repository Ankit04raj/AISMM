# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **41. FRONTEND ARCHITECTURE**  
   
 The frontend must also be platform-agnostic.  
   
 Do NOT create:  
   
 InstagramDashboard.jsx  
   
  FacebookDashboard.jsx  
   
  TwitterDashboard.jsx  
   
    
   
    
   
 for every common feature.  
   
 Instead create reusable components:  
   
 PlatformSelector  
   
  PostComposer  
   
  MediaUploader  
   
  CaptionEditor  
   
  HashtagSelector  
   
  SchedulePicker  
   
  SentimentPanel  
   
  AnalyticsPanel  
   
  CommentPanel  
   
  ReplyPanel  
   
  GrowthChart  
   
  RecommendationPanel  
   
  PlatformStatus  
   
    
   
    
   
 Platform-specific behavior should come from capability/configuration data.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4MoNpTPbBmp7NYQVvImwJtszMXp0BAPAX91pt1fH1BACA164HaHUEM3WR604AAAAASUVORK5CYII=)  
 **42. DYNAMIC UI**  
   
 The UI should ask the backend:  
   
 What can this platform do?  
   
    
   
    
   
 Then render accordingly.  
   
 Example:  
   
 Platform = X  
   
    
   
  Capabilities:  
   
  text ✓  
   
  image ✓  
   
  video ✓  
   
  carousel ?  
   
  stories ✗  
   
  scheduled ✓  
   
  comments ✓  
   
  analytics ✓  
   
    
   
    
   
 The UI adapts automatically.  
   
 This makes the system future-proof.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3KsQ0AIRAEsUW6Ruj0GvnivhMSYmKQ7GiCGd09k3wBAOAVf+2o4wYAwE1qAdYyAy2Ap4pWAAAAAElFTkSuQmCC)  
 **43. DASHBOARD STRUCTURE**  
   
 Recommended:  
   
 Dashboard  
   
  │  
   
  ├── Overview  
   
  ├── Platforms  
   
  ├── Create Post  
   
  ├── AI Optimize  
   
  ├── Calendar  
   
  ├── Scheduled Posts  
   
  ├── Published Posts  
   
  ├── Comments  
   
  ├── Auto Reply  
   
  ├── Sentiment  
   
  ├── Analytics  
   
  ├── Growth Prediction  
   
  ├── AI Recommendations  
   
  ├── Notifications  
   
  ├── Models  
   
  └── Settings  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/jzVsYQKvNrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4D+Bc7pl4pfAAAAAElFTkSuQmCC)  
 **44. PLATFORM CONNECTION PAGE**  
   
 Users should see:  
   
 Instagram       Connected  
   
  Facebook        Connected  
   
  X               Connected  
   
  LinkedIn        Not Connected  
   
  YouTube         Connected  
   
    
   
    
   
 Each platform should display:  
- Connection status  
- Account name  
- Permissions  
- Token status  
- Supported capabilities  
- Last synchronization  
- Disconnect option  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OYQ1AABSAwY9JIIGor4V+Ikiggn9mu0twy8wc1RkAAH9xbdVa7V9PAAB47X4A9CwEJcXSxLAAAAAASUVORK5CYII=)  
 **45. DATA SYNCHRONIZATION**  
   
 Each platform adapter should support synchronization.  
   
 Example:  
   
 Sync Account  
   
  ↓  
   
  Fetch Posts  
   
  ↓  
   
  Fetch Comments  
   
  ↓  
   
  Fetch Analytics  
   
  ↓  
   
  Normalize  
   
  ↓  
   
  Store  
   
  ↓  
   
  AI Processing  
   
  ↓  
   
  Dashboard  
   
    
   
    
   
 Allow:  
- Manual sync.  
- Scheduled sync.  
- Event-driven sync.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj7fFC6wwIgHRiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AOIABebqJIqXAAAAAElFTkSuQmCC)  
 **46. DATA STORAGE PRINCIPLE**  
   
 Store both:  
 **Raw platform data**  
   
 for debugging/auditing.  
   
 AND:  
 **Normalized AISMM data**  
   
 for AI/analytics.  
   
 Architecture:  
   
 RawPlatformData  
   
          ↓  
   
  Normalizer  
   
          ↓  
   
  AISMMNormalizedData  
   
          ↓  
   
  AI / Analytics  
   
    
   
    
   
 Do not throw away important platform-specific fields during normalization.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQ2AQBAAsSHhiQMcoWp9ngBsYIEfIWkVdJuZs5oAAPiLe6+O6vp6AgDAa+sBhZgEOcyZTEcAAAAASUVORK5CYII=)  
