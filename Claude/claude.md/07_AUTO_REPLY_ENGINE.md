# AISMM CLAUDE Documentation

> Extracted from the original CLAUDE(3).md. Preserve content semantics.

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
