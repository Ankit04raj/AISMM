# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

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
