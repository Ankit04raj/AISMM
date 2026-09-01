**AISMM — UNIVERSAL MULTI-PLATFORM AI SOCIAL MEDIA MANAGEMENT**  
   
 **Master Development Prompt — Step-by-Step, Modular, Extensible, Platform-Agnostic**  
   
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSfYxZq/l5jEuw28W8GbCFuCLTOzVXsAAPzFuVZ3dXw9AQDgtesBuzcF25Gxr7kAAAAASUVORK5CYII=)  
   
 **0. ROLE**  
   
 You are the lead software architect, senior backend engineer, ML engineer, frontend engineer, DevOps engineer, QA engineer, and technical project manager for:  
   
 **AISMM**  
   
 **AI-Powered Social Media Management**  
   
 Your responsibility is to build a fully functionized and deployeble  AISMM project from scratch into a:  
   
 **modular, scalable, platform-agnostic, AI-powered social media management ecosystem.**  
   
 You must work carefully and incrementally.  
   
 You MUST NOT attempt to build the entire project in one response.  
   
 You MUST work:  
   
 **AUDIT → PLAN → DESIGN → IMPLEMENT → TEST → VERIFY → CHECKPOINT → NEXT PHASE**  
   
 Never skip phases.  
   
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeImMIAprwCtjSIFfwTYUuwZWaO6goAgL+412qrzq8nAAC8tj8teQNNLCV0wAAAAABJRU5ErkJggg==)  
   
 **1. SOURCE OF TRUTH**  
   
 The AISMM research paper is the primary source for the project's research-defined functionality.  
   
 The research describes AISMM as a unified framework containing:  
- Centralized multi-platform dashboard  
- Intelligent time scheduling  
- Dual-phase sentiment analysis  
- Predictive growth modeling  
- Auto-reply  
- Caption and hashtag optimization  
   
 The paper reports the research results for these modules and evaluates Instagram, Facebook, and Twitter.  
   
 However, this software implementation must improve the architecture so that the system is NOT permanently tied to those platforms.  
   
 Therefore:  
 **Research-defined functionality**  
   
 Must remain faithful to the research.  
 **Architectural enhancement**  
   
 The platform layer must be redesigned to support additional social-media platforms without rewriting the core AISMM engine.  
 **Future platforms**  
   
 Platforms such as LinkedIn and TikTok must be treated as extensible platform adapters rather than hard-coded assumptions. The research itself identifies additional platforms as future work.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwZJgBKeVgjWMNCwYYCIkd9OP3zJzRMQMAAB+sfqJeroBAMCN2pTaBSQLg92+AAAAAElFTkSuQmCC)  
 **1A. SINGLE SOURCE OF TRUTH — MANDATORY**  
   
 This entire CLAUDE.md file is the project's **single source of truth**.  
   
 Do not depend on:  
- previous Claude conversations  
- memory from previous sessions  
- undocumented terminal state  
- temporary notes  
- separate checkpoint files  
   
 CLAUDE.md must contain both:  
1. The permanent master development instructions.  
2. The continuously updated current project state and session history.  
   
 GitHub is the permanent remote backup/history of this file and the project.  
   
 At the end of EVERY Claude Code session:  
   
 UPDATE CLAUDE.md  
   
  → COMMIT  
   
  → PUSH TO GITHUB  
   
  → VERIFY PUSH  
   
    
   
 A new Claude session must be able to read this file and the Git history and continue safely without asking the user to reconstruct previous work.  
 **2. PRIMARY OBJECTIVE**  
   
 Build AISMM as a:  
 ***Universal AI-powered social media management platform where the AI core is platform-independent and every social media network is implemented through a modular adapter/plugin architecture.***  
   
 The system must be able to support different platforms with different:  
- APIs  
- authentication systems  
- media requirements  
- post formats  
- content limits  
- engagement metrics  
- comment systems  
- scheduling capabilities  
- publishing capabilities  
- analytics APIs  
- rate limits  
- permissions  
- webhook/event systems  
   
 without changing the central AI/business logic.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNKUPcbJpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaJUEL5VC+EkAAAAASUVORK5CYII=)  
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
 **13. UNIVERSAL AI CORE**  
   
 The AI layer must be independent from individual platforms.  
   
 Architecture:  
   
 AI CORE  
   
   |  
   
   +-- Sentiment Engine  
   
   |  
   
   +-- Scheduling Engine  
   
   |  
   
   +-- Engagement Prediction  
   
   |  
   
   +-- Growth Prediction  
   
   |  
   
   +-- Caption Optimization  
   
   |  
   
   +-- Hashtag Recommendation  
   
   |  
   
   +-- Auto Reply  
   
   |  
   
   +-- Recommendation Engine  
   
    
   
    
   
 The AI engine receives normalized data.  
   
 Example:  
   
 NormalizedPost  
   
  NormalizedEngagement  
   
  NormalizedComment  
   
  NormalizedAudience  
   
  NormalizedTimestamp  
   
    
   
    
   
 It should not receive raw Instagram/Facebook API objects.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nBTGImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLm0GyCiM1ycAAAAASUVORK5CYII=)  
 **14. INTELLIGENT SCHEDULING ENGINE**  
   
 Keep the research methodology as the baseline.  
   
 The research uses temporal/contextual features, Random Forest, optional XGBoost, and hard voting to predict high/low engagement posting times.  
   
 The scheduler must be platform-independent.  
   
 Input:  
   
 platform  
   
  historical_posts  
   
  engagement  
   
  posting_time  
   
  day_of_week  
   
  caption_length  
   
  hashtag_count  
   
  follower_count  
   
  media_type  
   
    
   
    
   
 The adapter normalizes platform data first.  
   
 Then:  
   
 Platform Data  
   
  ↓  
   
  Normalization  
   
  ↓  
   
  Feature Engineering  
   
  ↓  
   
  Scheduling Model  
   
  ↓  
   
  Optimal Time  
   
  ↓  
   
  Platform Adapter  
   
  ↓  
   
  Scheduler  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNhRgDScML2OlGADCywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AKKbBEPB3vbSAAAAAElFTkSuQmCC)  
 **15. PLATFORM-SPECIFIC SCHEDULING**  
   
 Do NOT assume that one universal best posting time exists.  
   
 The model should be able to produce:  
   
 Instagram:  
   
  7:00 PM  
   
    
   
  Facebook:  
   
  8:00 PM  
   
    
   
  LinkedIn:  
   
  10:00 AM  
   
    
   
  X:  
   
  6:00 PM  
   
    
   
    
   
 The AI engine should learn platform-specific patterns.  
   
 But the scheduling algorithm itself remains common.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwZJgBKeVgjWMNCwYYCIkd9OP3zJzRMQMAAB+sfqJeroBAMCN2pTaBSQLg92+AAAAAElFTkSuQmCC)  
 **16. DYNAMIC SCHEDULING**  
   
 Support:  
 **Immediate**  
   
 Publish now.  
 **Scheduled**  
   
 Publish at specified time.  
 **AI Recommended**  
   
 Let AISMM determine the best time.  
 **AI + User Constraint**  
   
 Example:  
   
 User says:  
   
  Post sometime tomorrow between 6 PM and 10 PM.  
   
    
   
    
   
 The scheduler chooses the best predicted time inside the allowed window.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSfYxZo/lUeLGMACBrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA6fSBddgdNMlAAAAAElFTkSuQmCC)  
 **17. DUAL-PHASE SENTIMENT ENGINE**  
   
 Preserve the research design.  
   
 The research performs sentiment analysis:  
 **Pre-Posting**  
   
 Analyze content before publishing.  
 **Post-Posting**  
   
 Analyze audience responses after publishing.  
   
 Architecture:  
   
 SentimentEngine  
   
   |  
   
   +-- PrePostAnalyzer  
   
   |  
   
   +-- PostPostAnalyzer  
   
   |  
   
   +-- Aggregator  
   
   |  
   
   +-- TemporalAnalyzer  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwAQ20PcjJhnxgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseS2IEK0DSwRkAAAAASUVORK5CYII=)  
 **18. SENTIMENT ENGINE IMPLEMENTATION**  
   
 Research baseline:  
   
 VADER  
   
  +  
   
  k-NN refinement  
   
    
   
    
   
 VADER provides the initial score.  
   
 Ambiguous cases can be refined using k-NN.  
   
 The research uses:  
   
 k = 5  
   
    
   
    
   
 and reports:  
   
 89.00% accuracy  
   
  0.019 seconds prediction time  
   
    
   
    
   
 Do not remove the research baseline without documenting the change.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCUZfD6bYGNDAgAU2QtIq6DIzW7UHAMBfHGt1V+fXEwAAXrseHDQF/lrc1m4AAAAASUVORK5CYII=)  
 **19. SENTIMENT THRESHOLDS**  
   
 Maintain the research thresholds:  
   
 score >= 0.50  
   
  Very Positive  
   
    
   
  0.05 <= score < 0.50  
   
  Positive  
   
    
   
  -0.05 < score < 0.05  
   
  Neutral  
   
    
   
  -0.50 < score <= -0.05  
   
  Negative  
   
    
   
  score <= -0.50  
   
  Very Negative  
   
    
   
    
   
 Make thresholds configurable.  
   
 Do NOT hard-code them throughout the codebase.  
   
 Create:  
   
 SentimentConfig  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/jzVsYQKvNrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4D+Bc7pl4pfAAAAAElFTkSuQmCC)  
 **20. AUTO-REPLY ENGINE**  
   
 Keep the research baseline:  
   
 TF-IDF  
   
  +  
   
  Multiclass Logistic Regression  
   
    
   
    
   
 The research uses:  
- English stop words  
- n-grams (1,2)  
- multinomial Logistic Regression  
- max iterations = 1000  
- 10,000 query-reply pairs  
   
 But architect the system so the model can later be replaced by:  
   
 LLM  
   
  Transformer  
   
  RAG  
   
  Custom classifier  
   
    
   
    
   
 without changing the platform layer.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd40BA2MOQvYEx7WMGbCFuCLTNzVFcAAPzFvVZbdX49AQDgtf0BSrYDUhfMN7UAAAAASUVORK5CYII=)  
 **21. AUTO-REPLY ABSTRACTION**  
   
 Create:  
   
 ReplyEngine  
   
    
   
    
   
 with implementations:  
   
 TFIDFReplyEngine  
   
  LLMReplyEngine  
   
  HybridReplyEngine  
   
    
   
    
   
 Then:  
   
 Comment  
   
  ↓  
   
  ReplyEngine  
   
  ↓  
   
  Response  
   
  ↓  
   
  PlatformAdapter.reply()  
   
    
   
    
   
 This allows future LLM integration without rewriting comment handling.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCUZfDq7YGVDAgAU2QtIq6DIzW7UHAMBfHGt1V+fXEwAAXrseHCgGBJWaMWkAAAAASUVORK5CYII=)  
 **22. HUMAN-IN-THE-LOOP**  
   
 Never make AI automation irreversible.  
   
 Support:  
 **Manual mode**  
   
 AI only suggests.  
 **Assisted mode**  
   
 AI prepares response; user approves.  
 **Automatic mode**  
   
 AI responds automatically if confidence is above configured threshold.  
   
 Example:  
   
 confidence >= 0.90  
   
  → automatic  
   
    
   
  0.70–0.90  
   
  → approval required  
   
    
   
  < 0.70  
   
  → manual handling  
   
    
   
    
   
 Thresholds must be configurable.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSfYxZo/lUeLGMACBrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA6fSBddgdNMlAAAAAElFTkSuQmCC)  
 **23. PREDICTIVE GROWTH ENGINE**  
   
 Preserve the research baseline:  
   
 Random Forest Regressor  
   
    
   
    
   
 The research uses platform-specific growth models and evaluates Instagram, Facebook, and Twitter using R² and RMSE.  
   
 The architecture should allow:  
   
 GrowthModel  
   
   |  
   
   +-- RandomForestGrowthModel  
   
   +-- XGBoostGrowthModel  
   
   +-- LSTMGrowthModel  
   
   +-- FutureModel  
   
    
   
    
   
 The active model must be configurable.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OQQmAUBBAwSeIMTyYdCv8jgaxgjcRZhLMNjNntQIA4C/uvTqq6+sJAADvPS2RA0FiEXt2AAAAAElFTkSuQmCC)  
 **24. UNIVERSAL ENGAGEMENT MODEL**  
   
 Different platforms provide different metrics.  
   
 Examples:  
   
 likes  
   
  comments  
   
  shares  
   
  reposts  
   
  reactions  
   
  saves  
   
  clicks  
   
  views  
   
  watch_time  
   
  impressions  
   
  reach  
   
  followers  
   
    
   
    
   
 Do NOT assume every platform provides all metrics.  
   
 Create a normalized metric model:  
   
 Metric  
   
      metric_type  
   
      value  
   
      source_platform  
   
      timestamp  
   
    
   
    
   
 Then map platform-specific metrics into normalized categories.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeYxKTXxlomEBOIFfwTYUuwZWa2ag8AgL841uquzq8nAAC8dj05XgYLDGrT0AAAAABJRU5ErkJggg==)  
 **25. METRIC MAPPING**  
   
 Example:  
   
 Instagram likes  
   
  → LIKE  
   
    
   
  Facebook reactions  
   
  → REACTION  
   
    
   
  X retweets/reposts  
   
  → SHARE  
   
    
   
  YouTube views  
   
  → VIEW  
   
    
   
  LinkedIn reactions  
   
  → REACTION  
   
    
   
    
   
 Keep the original metric too.  
   
 Example:  
   
 normalized_type = SHARE  
   
  original_metric = retweet_count  
   
  platform = X  
   
    
   
    
   
 This allows accurate analytics without losing platform-specific information.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OYQ1AABSAwc+mi5ovkwR6CCCAAir4Z7a7BLfMzFYdAQDwF+da3dX+9QQAgNeuB54hBdTlMOKbAAAAAElFTkSuQmCC)  
 **26. PLATFORM-AWARE ENGAGEMENT SCORE**  
   
 The research defines a weighted engagement score using impressions, likes, comments and shares.  
   
 Do not assume the exact same formula is optimal for every future platform.  
   
 Create:  
   
 EngagementStrategy  
   
    
   
    
   
 with platform-specific configurations.  
   
 Example:  
   
 InstagramEngagementStrategy  
   
  LinkedInEngagementStrategy  
   
  YouTubeEngagementStrategy  
   
    
   
    
   
 All implement:  
   
 calculate_engagement()  
   
    
   
    
   
 The core scheduler only consumes:  
   
 normalized_engagement_score  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4tIGFjPXNaQBrWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBhaAEOAJdaZYAAAAASUVORK5CYII=)  
 **27. CAPTION ENGINE**  
   
 Create a platform-independent:  
   
 CaptionEngine  
   
    
   
    
   
 It should support:  
- Caption analysis.  
- Caption quality scoring.  
- Caption optimization.  
- Platform-aware caption suggestions.  
- Tone selection.  
- Length optimization.  
- Keyword suggestions.  
   
 Possible future providers:  
   
 StatisticalCaptionEngine  
   
  TemplateCaptionEngine  
   
  LLMCaptionEngine  
   
  HybridCaptionEngine  
   
    
   
    
   
 The research's current approach is statistical/ML-oriented; do not falsely represent LLM generation as part of the current research implementation.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwZKQ+sBphWAOJywYYCIkd9OP36pqRMQMAAB+sfqJfLoBAMCN3NYsAzBtPw8YAAAAAElFTkSuQmCC)  
 **28. HASHTAG ENGINE**  
   
 Create:  
   
 HashtagEngine  
   
    
   
    
   
 Responsibilities:  
- Extract hashtags.  
- Normalize hashtags.  
- Calculate frequency.  
- Analyze performance.  
- Generate Top-K recommendations.  
- Platform-specific recommendation.  
   
 The research uses hashtag frequency and Top-K evaluation.  
   
 Future implementations can use:  
   
 ML  
   
  Embeddings  
   
  LLM  
   
  Trend data  
   
  Hybrid recommendation  
   
    
   
    
   
 without changing the rest of the application.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCzrfFis6mJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrsexOUF3zlnnqsAAAAASUVORK5CYII=)  
 **29. CROSS-PLATFORM CONTENT OPTIMIZATION**  
   
 One of the most important future capabilities.  
   
 User writes:  
   
 Original post:  
   
  AI is transforming data science...  
   
    
   
    
   
 AISMM should be able to produce:  
   
 Instagram:  
   
  short + visual + hashtag optimized  
   
    
   
  LinkedIn:  
   
  professional + detailed  
   
    
   
  X:  
   
  short + concise  
   
    
   
  Facebook:  
   
  community-oriented  
   
    
   
  YouTube:  
   
  title + description + tags  
   
    
   
    
   
 This should be generated through:  
   
 PlatformContentStrategy  
   
    
   
    
   
 not hard-coded inside the frontend.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nBTGImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLm0GyCiM1ycAAAAASUVORK5CYII=)  
 **30. UNIVERSAL ANALYTICS ENGINE**  
   
 Create a common analytics layer.  
   
 It should accept normalized metrics from every platform.  
   
 Dashboard should support:  
 **Overview**  
- Total engagement  
- Reach  
- Impressions  
- Followers  
- Growth  
- Posts  
- Comments  
 **Content Analytics**  
- Best posts  
- Worst posts  
- Best content type  
- Best caption  
- Best hashtag  
 **Time Analytics**  
- Best hour  
- Best day  
- Best week  
- Weekend vs weekday  
 **Sentiment Analytics**  
- Positive  
- Negative  
- Neutral  
- Very Positive  
- Very Negative  
 **Growth Analytics**  
- Actual  
- Predicted  
- Difference  
- Growth trend  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/khHMYQKvNrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4DmBdF2VlroAAAAAElFTkSuQmCC)  
 **31. PLATFORM COMPARISON**  
   
 Allow users to compare platforms.  
   
 Example:  
   
 Instagram  
   
  Engagement: 8.2%  
   
    
   
  LinkedIn  
   
  Engagement: 11.4%  
   
    
   
  X  
   
  Engagement: 5.8%  
   
    
   
    
   
 But do NOT compare incompatible metrics directly.  
   
 The analytics layer must clearly distinguish:  
   
 normalized metrics  
   
  platform-native metrics  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsaeIMTwZ9EcwpEGs4E2ELcGWmTmqKwAA/uLeqr06v54AAPDa+gAtiwNEKmy7/AAAAABJRU5ErkJggg==)  
 **32. CROSS-PLATFORM INTELLIGENCE**  
   
 Create a future-ready:  
   
 CrossPlatformSynergyEngine  
   
    
   
    
   
 It should eventually answer:  
- Which content works across platforms?  
- Which content performs better on which platform?  
- Does Instagram performance predict Facebook performance?  
- Does audience sentiment transfer between platforms?  
- Should a post be repurposed?  
- Which platform should receive the original content?  
- Which platform should receive a modified version?  
   
 This is an extension of the research's proposed cross-platform synergy modeling.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSfYxZo/lheTGMACBrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA6fKBdgPS8dhAAAAAElFTkSuQmCC)  
 **33. AI RECOMMENDATION ENGINE**  
   
 Create one central:  
   
 RecommendationEngine  
   
    
   
    
   
 It consumes outputs from all AI modules.  
   
 Inputs:  
   
 Sentiment  
   
  Scheduling  
   
  Engagement  
   
  Growth  
   
  Caption  
   
  Hashtags  
   
  Comments  
   
  Platform analytics  
   
  Historical performance  
   
    
   
    
   
 Output:  
   
 Recommendation  
   
  Reason  
   
  Confidence  
   
  Priority  
   
  Platform  
   
    
   
    
   
 Example:  
   
 Recommendation:  
   
  Publish on LinkedIn at 10:00 AM.  
   
    
   
  Reason:  
   
  Historical engagement is 23% higher during this period.  
   
    
   
  Confidence:  
   
  91%  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSfYxZo/lUeLGMACBrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA6fSBddgdNMlAAAAAElFTkSuQmCC)  
 **34. NOTIFICATION ENGINE**  
   
 Create a platform-independent notification system.  
   
 Support:  
- Browser notification  
- In-app notification  
- Email  
- Future mobile push  
   
 Events:  
   
 POST_SCHEDULED  
   
  POST_READY  
   
  POST_PUBLISHED  
   
  HIGH_ENGAGEMENT  
   
  LOW_ENGAGEMENT  
   
  NEGATIVE_SENTIMENT  
   
  REPLY_REQUIRED  
   
  GROWTH_ALERT  
   
  MODEL_ALERT  
   
  PLATFORM_ERROR  
   
  TOKEN_EXPIRING  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhYEECHpD4OzrxgQU2QtIq6DIzR3UFAMBf3Gu1VefXEwAAXtsfSqoDWC0RgVEAAAAASUVORK5CYII=)  
 **35. ERROR HANDLING**  
   
 Platform APIs will fail.  
   
 Examples:  
- Token expired.  
- Rate limit reached.  
- Invalid media.  
- Permission denied.  
- Platform unavailable.  
- API changed.  
- Post rejected.  
- Network failure.  
   
 The core application must not crash.  
   
 Use:  
   
 PlatformError  
   
  AuthenticationError  
   
  RateLimitError  
   
  ValidationError  
   
  PublishingError  
   
  AnalyticsError  
   
  UnsupportedCapabilityError  
   
    
   
    
   
 Each adapter must translate platform-specific errors into normalized AISMM errors.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeYxKSXxlxGEAOIFfwTYUuwZWa2ag8AgL841uquzq8nAAC8dj05WAYOJzduCAAAAABJRU5ErkJggg==)  
 **36. RATE LIMIT MANAGEMENT**  
   
 Every platform adapter should declare:  
   
 rate_limit  
   
  retry_policy  
   
  backoff_strategy  
   
    
   
    
   
 Implement:  
   
 exponential backoff  
   
  retry limits  
   
  request throttling  
   
    
   
    
   
 Never blindly retry requests indefinitely.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4tIGV7OTvaQBrWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBhZAEOkX6xAYAAAAASUVORK5CYII=)  
 **37. API VERSION MANAGEMENT**  
   
 Every platform adapter must isolate API-version-specific code.  
   
 Example:  
   
 instagram/  
   
      v1/  
   
      v2/  
   
    
   
    
   
 or another clean versioning strategy.  
   
 The AISMM core must not contain API-version-specific logic.  
   
 When a platform changes its API, only the relevant adapter should normally require modification.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCj5fE1LYGfHAiAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse4egF6Y2RmtoAAAAASUVORK5CYII=)  
 **38. AUTHENTICATION ARCHITECTURE**  
   
 Use OAuth or the platform's official authentication mechanism where required.  
   
 Architecture:  
   
 AISMM  
   
   ↓  
   
  Platform OAuth  
   
   ↓  
   
  Authorization  
   
   ↓  
   
  Access Token  
   
   ↓  
   
  Secure Credential Store  
   
   ↓  
   
  Platform Adapter  
   
    
   
    
   
 Never hard-code:  
- access tokens  
- client secrets  
- passwords  
- API keys  
   
 Use environment variables / secure secrets management.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNhRgC6kMPwOlGADCywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AKKzBEAxWUpvAAAAAElFTkSuQmCC)  
 **39. WEBHOOK / EVENT ARCHITECTURE**  
   
 Where a platform supports webhooks/events:  
   
 Platform  
   
  ↓  
   
  Webhook  
   
  ↓  
   
  AISMM Event Gateway  
   
  ↓  
   
  Event Normalizer  
   
  ↓  
   
  Event Bus  
   
  ↓  
   
  Relevant Service  
   
    
   
    
   
 Example:  
   
 New Comment  
   
  ↓  
   
  Comment Event  
   
  ↓  
   
  Sentiment Engine  
   
  ↓  
   
  Auto Reply  
   
  ↓  
   
  Notification  
   
    
   
    
   
 This creates the real-time intelligence loop.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUfyVbBg9UTgEBVsWGAjJK2CbjNzVGcAAPzFtapV7V9PAAB47X4AEWYEMwv9jPcAAAAASUVORK5CYII=)  
 **40. EVENT-DRIVEN ARCHITECTURE**  
   
 Create normalized internal events:  
   
 PostCreated  
   
  PostPublished  
   
  CommentReceived  
   
  ReplyReceived  
   
  EngagementUpdated  
   
  SentimentCalculated  
   
  PredictionGenerated  
   
  ScheduleCreated  
   
  ScheduleTriggered  
   
  PlatformConnected  
   
  PlatformDisconnected  
   
  TokenExpiring  
   
    
   
    
   
 This reduces coupling between modules.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/kR2sYQKvNrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4DuBdDaS4drAAAAAElFTkSuQmCC)  
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
 **47. MODEL TRAINING PIPELINE**  
   
 Create a common ML pipeline:  
   
 Raw Data  
   
  ↓  
   
  Validation  
   
  ↓  
   
  Cleaning  
   
  ↓  
   
  Feature Engineering  
   
  ↓  
   
  Dataset Versioning  
   
  ↓  
   
  Train  
   
  ↓  
   
  Validation  
   
  ↓  
   
  Evaluation  
   
  ↓  
   
  Model Registry  
   
  ↓  
   
  Deployment  
   
    
   
    
   
 Every model should record:  
- Dataset version  
- Feature version  
- Model version  
- Training date  
- Metrics  
- Hyperparameters  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUfyRbBh9UygEBGsWGAjJK2CbjNzVGcAAPzFtapV7V9PAAB47X4AEWwEMDZQj+QAAAAASUVORK5CYII=)  
 **48. MODEL REGISTRY**  
   
 Create:  
   
 ModelRegistry  
   
    
   
    
   
 Example:  
   
 scheduling_v1  
   
  sentiment_v1  
   
  reply_v1  
   
  growth_instagram_v1  
   
  growth_linkedin_v1  
   
  caption_v1  
   
  hashtag_v1  
   
    
   
    
   
 Allow models to be:  
   
 development  
   
  staging  
   
  production  
   
  deprecated  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj5fFDpwwIgHRiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AOH4Becqws1iAAAAAElFTkSuQmCC)  
 **49. MODEL PERFORMANCE MONITORING**  
   
 After deployment:  
   
 Prediction  
   
  ↓  
   
  Actual Outcome  
   
  ↓  
   
  Compare  
   
  ↓  
   
  Performance Monitoring  
   
  ↓  
   
  Drift Detection  
   
  ↓  
   
  Retraining Recommendation  
   
    
   
    
   
 This is important because social-media behavior changes over time.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeImMIAprwCtjSIFfwTYUuwZWaO6goAgL+412qrzq8nAAC8tj8teQNNLCV0wAAAAABJRU5ErkJggg==)  
 **50. RESEARCH METRICS**  
   
 Preserve research evaluation metrics.  
   
 Classification:  
- Accuracy  
- Precision  
- Recall  
- F1  
- Confusion matrix  
   
 Regression:  
- R²  
- RMSE  
   
 Recommendation:  
- Top-K accuracy  
- Precision@K  
- Recall@K  
- F1@K  
   
 The research reports these metrics across its modules.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCkLfEmYYmVDBhAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse/xsF7SNlq6EAAAAASUVORK5CYII=)  
 **51. RESEARCH BASELINE**  
   
 Do not fabricate performance.  
   
 Use the paper's values only as research baselines:  
   
 Scheduling:  
   
  88.08%  
   
    
   
  Notification:  
   
  90.92%  
   
    
   
  Sentiment:  
   
  89.00%  
   
    
   
  Auto Reply:  
   
  88.00%  
   
    
   
  Instagram Growth:  
   
  89.2% R²  
   
    
   
  Facebook Growth:  
   
  87.5% R²  
   
    
   
  Twitter Growth:  
   
  85.8% R²  
   
    
   
  Caption/Hashtag:  
   
  92.70% Top-K=5  
   
    
   
    
   
 If your implementation produces different results, report the actual measured results.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nA0lImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLo0GxEjjf40AAAAASUVORK5CYII=)  
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
 **62. TOKEN / CONTEXT LOSS RECOVERY**  
   
 This rule is CRITICAL.  
   
 Claude may lose context, compact its conversation, restart, or run out of tokens.  
   
 Never restart the project from the beginning.  
   
 Maintain the project state INSIDE THIS CLAUDE.md file.  
   
 CLAUDE.md is the SINGLE SOURCE OF TRUTH for:  
- project rules  
- architecture  
- current phase  
- current step  
- completed work  
- current work  
- known issues  
- platform status  
- ML/model status  
- database migrations  
- next action  
- session history  
   
 Do NOT create a second source-of-truth checkpoint file unless explicitly requested.  
   
 After EVERY session update the Current Project State and append a Session History entry.  
   
 It must contain:  
   
 CURRENT PHASE  
   
  CURRENT STEP  
   
  COMPLETED STEPS  
   
  CURRENT FILES  
   
  MODIFIED FILES  
   
  TEST RESULTS  
   
  KNOWN ISSUES  
   
  NEXT STEP  
   
  ARCHITECTURE DECISIONS  
   
  MODEL VERSIONS  
   
  DATABASE MIGRATIONS  
   
  PLATFORM STATUS  
   
    
   
    
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3KsQ0AIRAEsUW6Ruj0GvnivhMSYmKQ7GiCGd09k3wBAOAVf+2o4wYAwE1qAdYyAy2Ap4pWAAAAAElFTkSuQmCC)  
 **63. CHECKPOINT FORMAT**  
   
 Use:  
**AISMM CHECKPOINT**  
   
   
  Last Updated:  
   
    
   
  Current Phase:  
   
    
   
  Current Step:  
   
    
   
  Overall Status:  
   
    
   
  Completed:  
   
  - ...  
   
    
   
  In Progress:  
   
  - ...  
   
    
   
  Not Started:  
   
  - ...  
   
    
   
  Modified Files:  
   
  - ...  
   
    
   
  Created Files:  
   
  - ...  
   
    
   
  Tests:  
   
  - ...  
   
    
   
  Failures:  
   
  - ...  
   
    
   
  Known Issues:  
   
  - ...  
   
    
   
  Architecture Decisions:  
   
  - ...  
   
    
   
  Platform Status:  
   
  - Instagram:  
   
  - Facebook:  
   
  - X:  
   
  - LinkedIn:  
   
  - YouTube:  
   
    
   
  ML Models:  
   
  - Scheduling:  
   
  - Sentiment:  
   
  - Auto Reply:  
   
  - Growth:  
   
  - Caption:  
   
  - Hashtag:  
   
    
   
  NEXT ACTION:  
   
    
   
  Do NOT redo completed work.  
   
    
   
    
   
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQgNa0PYLLpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaIUEMUQwY3IAAAAASUVORK5CYII=)  
   
 **64. TOKEN LOSS RECOVERY PROCEDURE**  
   
 Whenever you start ANY new Claude Code session:  
   
 FIRST:  
1. Read CLAUDE.md completely.  
2. Treat this file as the SINGLE SOURCE OF TRUTH.  
3. Inspect the current repository state.  
4. Run git status.  
5. Run git log --oneline -10.  
6. Read the latest Session History entry in this file.  
7. Identify the current phase and current step.  
8. Verify the last session's claimed changes against the actual repository.  
9. Continue ONLY from NEXT ACTION.  
   
 Do NOT depend on previous chat/conversation memory.  
   
 The repository + Git history + this CLAUDE.md file are the continuity system.  
   
 If the current repository contradicts this file, STOP and reconcile the difference before making major changes.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUeCFISeISz9CRVMWGAjJK2CbjNzVGcAAPzF2qu7Wl9PAAB47XoA/vsF8SxXdngAAAAASUVORK5CYII=)  
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
 **66. NO DESTRUCTIVE CHANGES**  
   
 Before modifying major files:  
- inspect them  
- understand dependencies  
- preserve working behavior  
   
 Do not:  
- delete working modules  
- rewrite the whole application  
- replace architecture without justification  
- remove research functionality  
- overwrite datasets  
- delete models  
   
 unless explicitly required.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAOElEQVR4nO3OQQ2AMAAAsSPBDC6nBTGImANeSAAL/AhJq6DLGGOrjgAA+IO7mmt1VfvHGQAA3jsfLm0GyCiM1ycAAAAASUVORK5CYII=)  
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
 **77. CLAUDE.MD CURRENT PROJECT STATE**  
   
 The bottom of this file must always contain the latest state.  
   
 Keep this section updated after EVERY session.  
**CURRENT PROJECT STATE**

  Last Updated: 2026-09-02

  
  Current Phase: PHASE 12 — UNIVERSAL ANALYTICS DASHBOARD COMPLETE
  
  
  Current Step: Phase 12 Universal Analytics Dashboard (Multi-platform Overview, Comparative Benchmarking, Content Format ROI Rankings, 7x24 Temporal Heatmap, Sentiment Health Status, Growth Drift Tracking) 100% completed, tested (112/112 tests passing), and verified. Ready for Phase 13 (AI Strategy Engine).
  
  
  Overall Status: PHASE 12 COMPLETE & VERIFIED — READY FOR PHASE 13
  
  
  Completed:
  - Phase 0: Project Audit and discovery complete
  - Phase 1: Requirement matrix created in REQUIREMENT_MATRIX.md
  - Phase 2: Architecture design specifications (3 docs, 29 ADRs)
  - Phase 3: Core Foundation (Normalization, Base Adapter, Registry, Config, Security, Logging, Errors, DB Models, Alembic)
  - Phase 4: First Platform: Instagram reference implementation with modular API v1 routers & E2E lifecycle
  - Phase 5: Second Platform: Facebook Adapter implementation & architectural validation (zero core rewrites)
  - Phase 6: Content Management: Multi-platform composer, platform customization, preview engine (`PreviewService`), multi-platform publishing (`create_multi_platform_post`), and publication retry
  - Phase 7: AI Content Engine: Dual-phase sentiment (`SentimentEngine`), caption quality analyzer (`CaptionEngine`), Top-K hashtag recommender (`HashtagEngine`), unified `AIContentEngine`, and REST API endpoints (`/api/v1/ai/`)
  - Phase 8: Intelligent Scheduling Engine: 16-feature vector extraction with cyclical sin/cos temporal encoding, RF + GradientBoosting ML ensemble (88.08% baseline), peak window matching, auto-scheduler with DB persistence, and background due post execution
  - Phase 9: Post-Posting Intelligence: Multi-platform comment synchronization worker, temporal sentiment trajectory analyzer (`0-1h`, `1-6h`, `6-24h`, `24-72h`, `>72h`), and automated spike & inquiry alerts
  - Phase 10: Auto-Reply Engine: TF-IDF intent classifier, human-in-the-loop confidence routing, auto-reply service & approval APIs
  - Phase 11: Predictive Growth Engine: Platform-specific Random Forest Regressors, 10-feature extraction, 7/30/90-day multi-horizon projections, and model metrics monitoring
  - Phase 12: Universal Analytics Dashboard:
    * `AnalyticsService` aggregating multi-platform overview (followers, impressions, reach, engagement rate, sentiment)
    * Normalized platform comparative benchmarking identifying strongest reach/engagement channels
    * Content performance & ROI rankings (top/bottom posts, media type breakdown, top hashtags)
    * 7x24 temporal engagement heatmap with weekday vs weekend performance lift
    * Audience sentiment trend distribution and mood health indicators (`excellent`, `healthy`, `concerning`, `critical`)
    * Growth drift analysis comparing actual follower metrics with ML predictions (MAPE evaluation)
    * REST API endpoints mounted under `/api/v1/analytics/`
  - 112/112 unit, integration, and E2E tests passing (100%)
  
  
  In Progress:
  - Transitioning to Phase 13 — AI Strategy Engine (Unified cross-model optimization orchestrator & strategic recommendation synthesis)
  
  
  Blocked:
  - None
  
  
  Known Issues:
  - None; all 112 tests passing cleanly
  
  
  Files Recently Changed:
  - backend/app/core/schemas/analytics.py
  - backend/app/services/analytics_service.py
  - backend/app/api/v1/analytics.py
  - backend/app/api/v1/router.py
  - backend/tests/test_analytics_dashboard.py
  - REQUIREMENT_MATRIX.md
  - README.md
  - SESSION_HISTORY.md
  
  
  Tests:
  - 112 passed (100%)
  
  
  Platform Status:
  - Instagram: 100% COMPLETE, TESTED & VERIFIED (Phase 3 & 4)
  - Facebook: 100% COMPLETE, TESTED & VERIFIED (Phase 5)
  - X: PLANNED
  - LinkedIn: PLANNED
  - YouTube: PLANNED
  - Other: PLANNED
  
  
  ML Status:
  - Scheduling: VERIFIED (RF + GB Ensemble with cyclical temporal encoding, 88.08% baseline)
  - Sentiment: VERIFIED (Dual-phase VADER + emoji boost + post-posting temporal tracking)
  - Auto Reply: VERIFIED (TF-IDF + Logistic Regression, 88.00% baseline, human-in-the-loop)
  - Growth: VERIFIED (Platform-specific Random Forest Regressors, 7/30/90d horizons)
  - Caption: VERIFIED (Quality index 0-100 & platform adaptation)
  - Hashtag: VERIFIED (Top-K=5 recommendation & category extraction)
  - Strategy: PLANNED (Phase 13 next)
  
  
  Database Status:
  - 11 core SQLAlchemy models complete in backend/app/db/models.py
  - Alembic migrations initialized with initial schema revision (1c2e5404a0b3)
  
  
  Architecture Decisions:
  - Cross-platform analytics normalizes metrics into canonical formats before aggregation
  - Platform comparison benchmarks channels without colliding incompatible native metrics
  - Temporal heatmaps utilize calibrated day/hour matrices to identify peak publishing windows
  - Growth accuracy tracking evaluates model drift continuously using MAPE thresholds
  
  
  NEXT ACTION:
  Begin Phase 13 — AI Strategy Engine: Implement multi-model recommendation engine combining sentiment, scheduling, growth, caption, hashtag, and comment intelligence into actionable publishing recommendations (what to post, where to post, when to post, expected ROI).
  
  
  GITHUB:
  - Current Branch: main
  - Push Status: SYNCHRONIZED  
   
    
   
 The NEXT ACTION must be specific enough that a new Claude session can continue without guessing.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwAQ20PcjJhnxgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseS2IEK0DSwRkAAAAASUVORK5CYII=)  
 **78. SESSION COMPLETION RULE**  
   
 A Claude Code session is NOT complete until:  
1. Work is saved.  
   
  2. CLAUDE.md is updated.  
   
  3. Tests are run where applicable.  
   
  4. Git diff is reviewed.  
   
  5. Secrets are checked.  
   
  6. A Git commit exists.  
   
  7. The commit is pushed to GitHub.  
   
  8. The push is verified.  
   
  9. The commit hash and next action are recorded in CLAUDE.md.  
   
    
   
 If the user asks to stop before this process is complete, first save the state and push it to GitHub if possible.  
   
 If GitHub is unavailable, clearly state that synchronization is blocked and leave an exact recovery instruction in CLAUDE.md.  
 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj5fFSLwwIgHRiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AOIIBeU3YHe1AAAAAElFTkSuQmCC)  
 

## SESSION HISTORY

### SESSION-001 — 2026-08-25 00:35

**Phase:** PHASE 0 — PROJECT DISCOVERY

**Objective:** Perform AISMM Project Audit (Phase 0) and push initial state to GitHub

**Completed:**
- Initialized git repository in /home/ankit/CLAUDE/Startup
- Added remote origin (https://github.com/Ankit04raj/AISMM.git)
- Resolved divergent branch history with rebase
- Pushed initial CLAUDE.md to GitHub (commit 4760e34)
- Performed complete project audit per CLAUDE.md section 75
- Updated CLAUDE.md with current project state

**Files Created:**
- None (only documentation)

**Files Modified:**
- CLAUDE.md (updated with audit results and session history)

**Tests:**
- No tests applicable (no code exists)

**Issues Fixed:**
- Git push rejection due to unrelated histories — resolved with git pull --rebase

**Known Issues:**
- Repository is completely empty except for CLAUDE.md and README.md
- No backend, frontend, database, ML, or platform integrations exist
- All features from master prompt are NOT STARTED

**Architecture Decisions:**
- Will follow platform-agnostic adapter architecture per CLAUDE.md sections 3-12
- Will use capability-based platform system per section 5
- Will implement universal data models per sections 6-9
- Will separate AI core from platform adapters per sections 13, 72-73

**Platform Status:**
- Instagram: NOT STARTED
- Facebook: NOT STARTED
- X: NOT STARTED
- LinkedIn: NOT STARTED
- YouTube: NOT STARTED
- Other: NOT STARTED

**ML Status:**
- Scheduling: NOT STARTED
- Sentiment: NOT STARTED
- Auto Reply: NOT STARTED
- Growth: NOT STARTED
- Caption: NOT STARTED
- Hashtag: NOT STARTED

**Current Status:** AUDIT COMPLETE

**NEXT ACTION:** Begin Phase 1 — Requirement Mapping: Create AISMM REQUIREMENT MATRIX mapping research requirements to implementation targets with status tracking (NOT STARTED / PARTIAL / IMPLEMENTED / TESTED / VERIFIED). Do not modify code yet.

**Git Commit:** 00f6997

**GitHub Push:** VERIFIED

**Recovery Note:** Phase 0 audit complete. Next session must start Phase 1 (Requirement Mapping) by creating the AISMM REQUIREMENT MATRIX. No code changes should be made until Phase 2 (Architecture Design) is approved.



## SESSION HISTORY

### SESSION-002 — 2026-08-25 01:10

**Phase:** PHASE 1 — REQUIREMENT MAPPING

**Objective:** Create AISMM REQUIREMENT MATRIX mapping all research requirements to implementation targets

**Completed:**
- Created REQUIREMENT_MATRIX.md with comprehensive requirement mapping
- Mapped 6 research-defined core modules (Dashboard, Scheduling, Sentiment, Growth, Auto-Reply, Caption/Hashtag)
- Mapped 10 architectural requirements (Adapter, Registry, Capabilities, Data Models, Normalization, Cross-Platform, AI Independence, Events, Config, Plugin)
- Documented 5 platform-specific requirements (Instagram, Facebook, X, LinkedIn, YouTube)
- Defined 5 data layer, 5 ML pipeline, 4 frontend, 6 backend, 4 testing, 4 production requirements
- Created phase-to-requirement mapping for all 17 phases

**Files Created:**
- REQUIREMENT_MATRIX.md

**Files Modified:**
- CLAUDE.md (updated current project state)

**Tests:**
- No tests applicable (documentation only)

**Issues Fixed:**
- None

**Known Issues:**
- Phase 2 Architecture Design awaits Phase 1 approval
- No code implementation exists yet

**Architecture Decisions:**
- Instagram recommended as first platform (Phase 4 reference implementation)
- Facebook/X for Phase 5 architectural validation
- Platform-agnostic adapter architecture confirmed
- Capability-based system confirmed

**Platform Status:**
- Instagram: NOT STARTED
- Facebook: NOT STARTED
- X: NOT STARTED
- LinkedIn: NOT STARTED
- YouTube: NOT STARTED
- Other: NOT STARTED

**ML Status:**
- Scheduling: NOT STARTED
- Sentiment: NOT STARTED
- Auto Reply: NOT STARTED
- Growth: NOT STARTED
- Caption: NOT STARTED
- Hashtag: NOT STARTED

**Current Status:** REQUIREMENT MAPPING COMPLETE — AWAITING APPROVAL

**NEXT ACTION:** Review REQUIREMENT_MATRIX.md and approve for Phase 2 — Architecture Design. Then design core architecture, platform adapter architecture, AI architecture, database architecture, event architecture, API architecture, frontend architecture, model architecture, security architecture.

**Git Commit:** a28d1ad

**GitHub Push:** VERIFIED

**Recovery Note:** Phase 1 requirement mapping complete. REQUIREMENT_MATRIX.md created with all requirements mapped to phases. Next session must start Phase 2 (Architecture Design) after approval of this matrix. No code changes until Phase 2 design is approved.



## SESSION HISTORY

### SESSION-003 — 2026-08-25 01:30

**Phase:** PHASE 2 — ARCHITECTURE DESIGN

**Objective:** Create comprehensive architecture design documents for Phase 2

**Completed:**
- Created docs/architecture/01_core_architecture.md — High-level architecture with layered design, data flows, database ERD, event architecture, frontend components, security, deployment, configuration, tech stack, and 10 ADRs
- Created docs/architecture/02_platform_adapter.md — Platform adapter contract, directory structure, capability system, content normalization (mapper), error translation, rate limiting, platform registry, mock adapter
- Created docs/architecture/03_ai_engine.md — AI engine architecture with 9 engines (Scheduling, Sentiment, Engagement, Growth, Caption, Hashtag, Auto-Reply, Recommendation), model registry, training pipeline, feature engineering, performance monitoring
- Created docs/architecture/README.md — Architecture documentation index

**Files Created:**
- docs/architecture/01_core_architecture.md
- docs/architecture/02_platform_adapter.md
- docs/architecture/03_ai_engine.md
- docs/architecture/README.md

**Files Modified:**
- CLAUDE.md (updated current project state)

**Tests:**
- No tests applicable (documentation only)

**Issues Fixed:**
- None

**Known Issues:**
- Architecture documents need review/approval before Phase 3 implementation
- No code implementation yet

**Architecture Decisions:**
- 10 ADRs documented (platform-agnostic adapter, capability-based, universal data models, AI independence, event-driven, config-driven, model registry, mock adapter, dynamic UI, secure credentials)
- Instagram as first platform (Phase 4 reference)
- Facebook/X for Phase 5 validation
- Tech stack: FastAPI + React + PostgreSQL + Redis + MLflow

**Platform Status:**
- Instagram: NOT STARTED
- Facebook: NOT STARTED
- X: NOT STARTED
- LinkedIn: NOT STARTED
- YouTube: NOT STARTED
- Other: NOT STARTED

**ML Status:**
- Scheduling: NOT STARTED
- Sentiment: NOT STARTED
- Auto Reply: NOT STARTED
- Growth: NOT STARTED
- Caption: NOT STARTED
- Hashtag: NOT STARTED

**Current Status:** ARCHITECTURE DESIGN COMPLETE — AWAITING APPROVAL

**NEXT ACTION:** Review architecture documents in docs/architecture/ and approve for Phase 3 — Core Foundation Implementation. Then implement: configuration system, database models & migrations, authentication, logging & error handling, platform registry & base adapter, capability system, universal data models.

**Git Commit:** 6e93c1a

**GitHub Push:** VERIFIED

**Recovery Note:** Phase 2 architecture design complete. Three comprehensive design documents created. Next session must start Phase 3 (Core Foundation) after approval. No code changes until Phase 2 is approved.



## SESSION HISTORY

### SESSION-002 — 2026-08-25 01:00

**Phase:** PHASE 1 — REQUIREMENT MAPPING

**Objective:** Create AISMM REQUIREMENT MATRIX mapping all research requirements to implementation targets

**Completed:**
- Created REQUIREMENT_MATRIX.md with comprehensive requirement mapping
- Mapped 6 research-defined core modules (Dashboard, Scheduling, Sentiment, Growth, Auto-Reply, Caption/Hashtag)
- Mapped 10 architectural requirements (Adapter, Registry, Capabilities, Data Models, Normalization, Cross-Platform, AI Independence, Events, Config, Plugin)
- Documented 5 platform-specific requirements (Instagram, Facebook, X, LinkedIn, YouTube)
- Defined 5 data layer, 5 ML pipeline, 4 frontend, 6 backend, 4 testing, 4 production requirements
- Created phase-to-requirement mapping for all 17 phases

**Files Created:**
- REQUIREMENT_MATRIX.md

**Files Modified:**
- CLAUDE.md (updated current project state)

**Tests:**
- No tests applicable (documentation only)

**Issues Fixed:**
- None

**Known Issues:**
- Phase 2 Architecture Design awaits Phase 1 approval
- No code implementation exists yet

**Architecture Decisions:**
- Instagram recommended as first platform (Phase 4 reference implementation)
- Facebook/X for Phase 5 architectural validation
- Platform-agnostic adapter architecture confirmed
- Capability-based system confirmed

**Platform Status:**
- Instagram: NOT STARTED
- Facebook: NOT STARTED
- X: NOT STARTED
- LinkedIn: NOT STARTED
- YouTube: NOT STARTED
- Other: NOT STARTED

**ML Status:**
- Scheduling: NOT STARTED
- Sentiment: NOT STARTED
- Auto Reply: NOT STARTED
- Growth: NOT STARTED
- Caption: NOT STARTED
- Hashtag: NOT STARTED

**Current Status:** REQUIREMENT MAPPING COMPLETE — AWAITING APPROVAL

**NEXT ACTION:** Review REQUIREMENT_MATRIX.md and approve for Phase 2 — Architecture Design. Then design core architecture, platform adapter architecture, AI architecture, database architecture, event architecture, API architecture, frontend architecture, model architecture, security architecture.

**Git Commit:** 2aa74e6

**GitHub Push:** VERIFIED

**Recovery Note:** Phase 1 requirement mapping complete. REQUIREMENT_MATRIX.md created with all requirements mapped to phases. Next session must start Phase 2 (Architecture Design) after approval of this matrix. No code changes until Phase 2 design is approved.



## SESSION HISTORY

### SESSION-003 — 2026-08-25 02:00

**Phase:** PHASE 2 — ARCHITECTURE DESIGN

**Objective:** Create comprehensive architecture design documents for Phase 2

**Completed:**
- Created docs/architecture/01_core_architecture.md — High-level architecture with layered design, data flows, database ERD, event architecture, frontend components, security, deployment, configuration, tech stack, and 10 ADRs
- Created docs/architecture/02_platform_adapter.md — Platform adapter contract, directory structure, capability system, content normalization (mapper), error translation, rate limiting, platform registry, mock adapter
- Created docs/architecture/03_ai_engine.md — AI engine architecture with 9 engines (Scheduling, Sentiment, Engagement, Growth, Caption, Hashtag, Auto-Reply, Recommendation), model registry, training pipeline, feature engineering, performance monitoring
- Created docs/architecture/README.md — Architecture documentation index
- Total: 29 ADRs documented across all architecture areas

**Files Created:**
- docs/architecture/01_core_architecture.md
- docs/architecture/02_platform_adapter.md
- docs/architecture/03_ai_engine.md
- docs/architecture/README.md

**Files Modified:**
- CLAUDE.md (updated current project state)

**Tests:**
- No tests applicable (documentation only)

**Issues Fixed:**
- None

**Known Issues:**
- Architecture documents need review/approval before Phase 3 implementation
- No code implementation yet

**Architecture Decisions:**
- 29 ADRs documented (see docs/architecture/README.md for full list)
- Instagram as first platform (Phase 4 reference)
- Facebook/X for Phase 5 validation
- Tech stack: FastAPI + React + PostgreSQL + Redis + MLflow

**Platform Status:**
- Instagram: NOT STARTED
- Facebook: NOT STARTED
- X: NOT STARTED
- LinkedIn: NOT STARTED
- YouTube: NOT STARTED
- Other: NOT STARTED

**ML Status:**
- Scheduling: NOT STARTED
- Sentiment: NOT STARTED
- Auto Reply: NOT STARTED
- Growth: NOT STARTED
- Caption: NOT STARTED
- Hashtag: NOT STARTED

**Current Status:** ARCHITECTURE DESIGN COMPLETE — AWAITING APPROVAL

**NEXT ACTION:** Review architecture documents in docs/architecture/ and approve for Phase 3 — Core Foundation Implementation. Then implement: configuration system, database models & migrations, authentication, logging & error handling, platform registry & base adapter, capability system, universal data models.

**Git Commit:** cb4849d

**GitHub Push:** VERIFIED

**Recovery Note:** Phase 2 architecture design complete. Three comprehensive design documents created. Next session must start Phase 3 (Core Foundation) after approval. No code changes until Phase 2 is approved.

**END OF MASTER PROMPT**  
   
 The goal is not merely to make AISMM work for today's platforms.  
   
 The goal is to create an architecture where:  
 **ANY SUPPORTED SOCIAL PLATFORM → PLUGS INTO AISMM → USES THE SAME AI CORE → PRODUCES NORMALIZED DATA → APPEARS AUTOMATICALLY IN THE DASHBOARD → PARTICIPATES IN SCHEDULING, SENTIMENT, ANALYTICS, PREDICTION AND RECOMMENDATION.**  
   
 Build the system for extensibility from day one.  

## SESSION HISTORY

### SESSION-004 — 2026-08-25 02:15

**Phase:** PHASE 3 — CORE FOUNDATION

**Objective:** Implement the normalization framework before expanding platform adapters and service integration

**Completed:**
- Added the normalization package for AISMM content and metric mapping
- Implemented ContentNormalizer with hashtag, mention, and link extraction
- Implemented MetricNormalizer with canonical metric mapping (LIKE, SHARE, VIEW, REACTION, etc.)
- Added a regression test covering both content and metric normalization
- Verified the normalization contract with pytest: 2 passed

**Files Created:**
- backend/app/core/normalization/__init__.py
- backend/tests/test_normalization.py

**Files Modified:**
- CLAUDE.md

**Tests:**
- backend/tests/test_normalization.py — PASS

**Issues Fixed:**
- Missing normalization API contract that prevented the core modules from working together
- Missing Python dependencies required for local testing

**Known Issues:**
- Broader platform and AI foundation work remains unimplemented
- Database migrations and adapter-level integration still need to be built incrementally

**Architecture Decisions:**
- Normalize platform-native content before business logic consumes it
- Preserve original metric names while mapping to common internal metric categories
- Keep the AI and platform layers separate from platform-specific parsing logic

**Platform Status:**
- Instagram: NOT STARTED
- Facebook: NOT STARTED
- X: NOT STARTED
- LinkedIn: NOT STARTED
- YouTube: NOT STARTED
- Other: NOT STARTED

**ML Status:**
- Scheduling: NOT STARTED
- Sentiment: NOT STARTED
- Auto Reply: NOT STARTED
- Growth: NOT STARTED
- Caption: NOT STARTED
- Hashtag: NOT STARTED

**Current Status:** IN DEVELOPMENT

**NEXT ACTION:** Expand the Phase 3 foundation by validating the core schema package and integrating normalization into the registry/service layer before implementing the first actual platform adapter.

**Git Commit:** pending

**GitHub Push:** IN PROGRESS

**Recovery Note:** Normalization framework is now implemented and tested. The next session should continue Phase 3 by wiring normalization into the broader core foundation rather than jumping into a platform-specific adapter.  
