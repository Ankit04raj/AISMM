# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

   
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
