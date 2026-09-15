# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **56. GRACEFUL DEGRADATION**  
   
 If a platform does not support a feature:  
   
 Example:  
   
 Platform does not support scheduled posting.  
   
    
   
    
   
 AISMM should show:  
 *"Native scheduling is unavailable for this platform."*  
   
 It may optionally offer an AISMM-side scheduling mechanism only if technically and legally appropriate.  
   
 Never fake native platform functionality.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nA0lImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLo0GxEjjf40AAAAASUVORK5CYII=)  
 **57. CONFIGURATION-DRIVEN SYSTEM**  
   
 Avoid hard-coded platform assumptions.  
   
 Use configuration:  
   
 platform_config  
   
  model_config  
   
  feature_config  
   
  scheduler_config  
   
  sentiment_config  
   
  notification_config  
   
    
   
    
   
 Example:  
   
 platform:  
   
      name  
   
      capabilities  
   
      limits  
   
      supported_media  
   
      api_version  
   
    
   
    
   
 This allows future platforms to be added with minimal core changes.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUfyNbBi9VRgEA3sWGAjJK2CbjNzVGcAAPzFtapV7V9PAAB47X4AEXIELdGZ+p4AAAAASUVORK5CYII=)  
 **58. PLUGIN ARCHITECTURE**  
   
 Eventually the architecture should support:  
   
 Install Platform Plugin  
   
  ↓  
   
  Register Adapter  
   
  ↓  
   
  Register Capabilities  
   
  ↓  
   
  Register API  
   
  ↓  
   
  Platform appears automatically  
   
    
   
    
   
 The core AISMM engine remains unchanged.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nA0lImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLo0GxEjjf40AAAAASUVORK5CYII=)  
 **59. NO HARDCODED PLATFORM LOGIC**  
   
 Avoid code such as:  
   
 if platform == "instagram":  
   
      ...  
   
  elif platform == "facebook":  
   
      ...  
   
  elif platform == "twitter":  
   
      ...  
   
    
   
    
   
 inside the core business logic.  
   
 Instead:  
   
 adapter = platform_registry.get(platform)  
   
  adapter.publish(...)  
   
    
   
    
   
 Platform-specific conditions belong inside the adapter.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwZKQ+sBphWAOJywYYCIkd9OP36pqRMQMAAB+sfqJfLoBAMCN3NYsAzBtPw8YAAAAAElFTkSuQmCC)  
 **60. SEPARATION OF CONCERNS**  
   
 Maintain clear layers:  
   
 Frontend  
   
      ↓  
   
  API  
   
      ↓  
   
  Application Services  
   
      ↓  
   
  Domain/Core  
   
      ↓  
   
  AI Engine  
   
      ↓  
   
  Platform Adapter  
   
      ↓  
   
  External Platform  
   
    
   
    
   
 Do not allow:  
   
 Frontend → Instagram API directly  
   
    
   
    
   
 or:  
   
 ML model → Instagram-specific code  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCzrfFis6mJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrsexOUF3zlnnqsAAAAASUVORK5CYII=)  
