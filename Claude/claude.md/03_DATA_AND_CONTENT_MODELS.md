# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **6. UNIVERSAL DATA MODEL**  
   
 Create platform-neutral internal entities.  
 **User**  
   
 id  
   
  name  
   
  email  
   
  created_at  
   
  updated_at  
   
    
   
    
 **SocialAccount**  
   
 id  
   
  user_id  
   
  platform_id  
   
  platform_account_id  
   
  account_name  
   
  account_username  
   
  access_token_reference  
   
  refresh_token_reference  
   
  status  
   
  capabilities  
   
  created_at  
   
  updated_at  
   
    
   
    
   
 NEVER store raw secrets in normal database fields unless absolutely required.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nA0lImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLo0GxEjjf40AAAAASUVORK5CYII=)  
 **7. UNIVERSAL POST MODEL**  
   
 The central Post model must not contain platform-specific fields everywhere.  
   
 Use:  
   
 Post  
   
    
   
    
   
 with:  
   
 id  
   
  user_id  
   
  content  
   
  caption  
   
  status  
   
  created_at  
   
  scheduled_at  
   
  published_at  
   
  media  
   
  metadata  
   
    
   
    
   
 Then maintain platform-specific publication records.  
   
 Example:  
   
 Post  
   
     |  
   
     +---- PostPublication  
   
               |  
   
               +---- Instagram  
   
               +---- Facebook  
   
               +---- X  
   
               +---- LinkedIn  
   
               +---- YouTube  
   
    
   
    
   
 This allows one piece of content to be published to multiple platforms.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NoCx7CP8nCYwhhW8ibAl2DIze3UGAMBf3Gu1VcfXEwAAXrseorsEP/A3VNIAAAAASUVORK5CYII=)  
 **8. CROSS-PLATFORM POSTING**  
   
 Support:  
   
 Create once  
   
  → Customize  
   
  → Publish to selected platforms  
   
    
   
    
   
 Example:  
   
 User creates:  
   
 Caption  
   
  Image  
   
  Hashtags  
   
    
   
    
   
 Then selects:  
   
 Instagram ✓  
   
  Facebook ✓  
   
  LinkedIn ✓  
   
  X ✓  
   
    
   
    
   
 AISMM should generate platform-specific variants where necessary.  
   
 Example:  
   
 Original Content  
   
        |  
   
        +--> Instagram version  
   
        |  
   
        +--> Facebook version  
   
        |  
   
        +--> LinkedIn version  
   
        |  
   
        +--> X version  
   
    
   
    
   
 Do not blindly duplicate the same content if platform-specific optimization is required.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NoCpTCQ/pwmMYQVvImwJtszMXp0BAPAX91pt1fH1BACA164HosMEPiBLnfkAAAAASUVORK5CYII=)  
 **9. UNIVERSAL CONTENT NORMALIZATION**  
   
 Create a common internal content representation:  
   
 UniversalContent  
   
    
   
    
   
 It may contain:  
   
 text  
   
  caption  
   
  title  
   
  media  
   
  hashtags  
   
  mentions  
   
  links  
   
  location  
   
  language  
   
  content_type  
   
  metadata  
   
    
   
    
   
 Each adapter converts:  
   
 UniversalContent  
   
    
   
    
   
 into:  
   
 PlatformSpecificPayload  
   
    
   
    
   
 This is one of the most important architectural components.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd40BA2MOQvYEx7WMGbCFuCLTNzVFcAAPzFvVZbdX49AQDgtf0BSrYDUhfMN7UAAAAASUVORK5CYII=)  
 **10. PLATFORM ADAPTER CONTRACT**  
   
 Every new platform must follow the same contract.  
   
 Example:  
   
 BasePlatformAdapter  
   
    
   
    
   
 Responsibilities:  
 **Authentication**  
- connect  
- disconnect  
- refresh credentials  
- validate credentials  
 **Publishing**  
- validate content  
- upload media  
- publish  
- schedule if supported  
 **Content**  
- fetch posts  
- update posts  
- delete posts  
 **Engagement**  
- fetch comments  
- fetch replies  
- reply  
- fetch reactions where supported  
 **Analytics**  
- account analytics  
- post analytics  
- audience metrics  
- engagement metrics  
 **Events**  
- webhook registration  
- webhook handling  
 **Capability reporting**  
   
 Return exactly what the platform supports.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNhRgDScML2OlGADCywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AKKbBEPB3vbSAAAAAElFTkSuQmCC)  
 **11. PLUGIN / ADAPTER DIRECTORY**  
   
 Use an architecture similar to:  
   
 platforms/  
   
      base/  
   
          adapter.py  
   
          capabilities.py  
   
          models.py  
   
    
   
      instagram/  
   
          adapter.py  
   
          auth.py  
   
          publisher.py  
   
          analytics.py  
   
          comments.py  
   
          mapper.py  
   
    
   
      facebook/  
   
          adapter.py  
   
          auth.py  
   
          publisher.py  
   
          analytics.py  
   
          comments.py  
   
          mapper.py  
   
    
   
      x/  
   
          adapter.py  
   
          auth.py  
   
          publisher.py  
   
          analytics.py  
   
          comments.py  
   
          mapper.py  
   
    
   
      linkedin/  
   
          adapter.py  
   
          auth.py  
   
          publisher.py  
   
          analytics.py  
   
          comments.py  
   
          mapper.py  
   
    
   
      youtube/  
   
          adapter.py  
   
          auth.py  
   
          publisher.py  
   
          analytics.py  
   
          comments.py  
   
          mapper.py  
   
    
   
    
   
 If a platform is not yet implemented:  
   
 adapter exists  
   
  status = planned  
   
    
   
    
   
 Do not create fake API functionality.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj5fFSLwwIgHRiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AOIIBeU3YHe1AAAAAElFTkSuQmCC)  
 **12. PLATFORM REGISTRY**  
   
 Create a central platform registry.  
   
 Example:  
   
 PlatformRegistry  
   
    
   
    
   
 Responsibilities:  
- Register adapters.  
- Discover available platforms.  
- Load platform capabilities.  
- Return the correct adapter.  
- Validate platform support.  
- Provide platform metadata.  
   
 Conceptually:  
   
 PlatformRegistry.get("instagram")  
   
  PlatformRegistry.get("linkedin")  
   
  PlatformRegistry.get("youtube")  
   
    
   
    
   
 Adding a new platform should require:  
1. New adapter.  
2. Capability declaration.  
3. Platform configuration.  
4. API integration.  
5. Tests.  
   
 It should NOT require rewriting:  
- scheduler  
- sentiment engine  
- growth engine  
- analytics engine  
- recommendation engine  
- dashboard architecture  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCzpfFxNCmJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fHEQAA3rsexO0F3jmX9Q8AAAAASUVORK5CYII=)  
