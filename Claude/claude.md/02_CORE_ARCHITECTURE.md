# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

 **3. CORE ARCHITECTURE PRINCIPLE**  
   
 NEVER build the system around a single platform.  
   
 DO NOT create architecture like:  
   
 InstagramService  
   
  FacebookService  
   
  TwitterService  
   
    
   
    
   
 with duplicated business logic.  
   
 Instead build:  
   
                     AISMM CORE  
   
                         |  
   
          --------------------------------  
   
          |              |               |  
   
   Content Engine   AI Engine       Analytics Engine  
   
          |              |               |  
   
          --------------------------------  
   
                         |  
   
                  Platform Interface  
   
                         |  
   
       --------------------------------------------  
   
       |          |         |        |             |  
   
   Instagram   Facebook     X      LinkedIn     YouTube  
   
   Adapter     Adapter    Adapter   Adapter      Adapter  
   
    
   
    
   
 The core AISMM system should know about:  
- Post  
- Media  
- Caption  
- Hashtag  
- Comment  
- Engagement  
- Audience  
- Schedule  
- Sentiment  
- Prediction  
- Recommendation  
   
 It should NOT depend directly on Instagram/Facebook/X-specific implementation details.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4MoNpTPbBmp7NYQVvImwJtszMXp0BAPAX91pt1fH1BACA164HaHUEM3WR604AAAAASUVORK5CYII=)  
 **4. PLATFORM-AGNOSTIC DESIGN**  
   
 Create a standard platform abstraction.  
   
 Conceptually:  
   
 PlatformAdapter  
   
    
   
    
   
 Every platform adapter must implement the capabilities that the platform actually supports.  
   
 Possible capabilities:  
   
 authenticate()  
   
  refresh_token()  
   
  disconnect()  
   
    
   
  create_post()  
   
  publish_post()  
   
  schedule_post()  
   
  update_post()  
   
  delete_post()  
   
    
   
  upload_media()  
   
  upload_image()  
   
  upload_video()  
   
    
   
  fetch_posts()  
   
  fetch_comments()  
   
  fetch_replies()  
   
    
   
  reply_to_comment()  
   
    
   
  fetch_engagement()  
   
  fetch_account_metrics()  
   
    
   
  fetch_post_analytics()  
   
    
   
  register_webhook()  
   
  handle_webhook()  
   
    
   
  validate_content()  
   
    
   
    
   
 BUT:  
   
 Do not assume every platform supports every operation.  
   
 The adapter must expose capabilities dynamically.  
   
 Example:  
   
 supports("video_upload")  
   
  supports("scheduled_post")  
   
  supports("comments")  
   
  supports("analytics")  
   
  supports("auto_reply")  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/kR2sYQKvNrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4DuBdDaS4drAAAAAElFTkSuQmCC)  
 **5. CAPABILITY-BASED PLATFORM SYSTEM**  
   
 Every platform must have a capability definition.  
   
 Example:  
   
 PlatformCapabilities  
   
    
   
  publishing  
   
  scheduling  
   
  text_post  
   
  image_post  
   
  video_post  
   
  carousel_post  
   
  stories  
   
  short_video  
   
  comments  
   
  replies  
   
  analytics  
   
  audience_metrics  
   
  webhooks  
   
  direct_messages  
   
  hashtags  
   
  mentions  
   
    
   
    
   
 The frontend should automatically adapt according to the capabilities.  
   
 For example:  
   
 If a platform does not support:  
   
 scheduled_post  
   
    
   
    
   
 do not display the scheduling button.  
   
 If a platform supports:  
   
 video  
   
    
   
    
   
 display video upload.  
   
 If a platform does not provide:  
   
 share_count  
   
    
   
    
   
 the analytics layer must represent that metric as unavailable rather than inventing a value.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCj5fE1LYGfHAiAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse4egF6Y2RmtoAAAAASUVORK5CYII=)  
