# May 23, 2025 - Log 01

## Done
- Set up FastAPI project with NLP engine (spaCy + scikit-learn)
- Created conversation manager for bilingual responses (EN/ZH)
- Built chat API endpoint at /chat (POST)

## Bugs Encountered
**🐛 CORS Middleware Error** - SOLVED ✅
- **What**: `TypeError: CORSMiddleware.__init__() got an unexpected keyword argument 'all_methods'`
- **How**: When running `python main.py`, server starts but crashes on first HTTP request
- **Where**: `app/main.py` CORS configuration
- **Fix**: Changed `all_methods=["*"]` to `allow_methods=["*"]`
- **Root Cause**: Incorrect parameter name in FastAPI CORS setup

## Next / Blocked
- Test API endpoints at http://localhost:8000/docs
- Build frontend chat interface (HTML file ready)

## Notes
- Server should start clean after CORS fix
- Chinese language support implemented for competitive advantage
---

# May 23, 2025 - Log 02

## Done
- Identified and diagnosed NLP accuracy issues through testing
- Frontend chat interface working properly after fixing DOM manipulation bug
- Bilingual conversation flow functioning (EN/ZH detection working)

## Bugs Encountered
**🐛 Frontend DOM Hierarchy Error** - SOLVED ✅
- **What**: `HierarchyRequestError: Failed to execute 'appendChild' on 'Node'`
- **How**: When clicking Send button, messages wouldn't appear and console showed DOM error
- **Where**: `frontend/index.html` JavaScript `addMessage()` function
- **Fix**: Changed `messageDiv.appendChild(messageDiv)` to `messagesDiv.appendChild(messageDiv)`
- **Root Cause**: Accidentally trying to append element to itself instead of parent container

**🐛 Poor Context Understanding** - IN PROGRESS 🟡
- **What**: Intent classification giving wrong results with low confidence
- **How**: 
 - "I want to buy a product" → Classified as `cancel_order` (wrong!)
 - "I want to buy, not cancel" → Still classified as `cancel_order` (wrong!)
 - Low confidence scores (0.28, 0.31) indicate model uncertainty
- **Where**: `app/models/nlp_engine.py` - basic Naive Bayes classifier
- **Root Cause**: Simple approach using basic TF-IDF + limited training data (5 examples per intent)
- **Tried**: Initial testing revealed the scope of the problem
- **Next**: Apply quick fixes - expand training data, add keyword rules, improve responses

## Next
- **Phase 1 Quick Fixes:**
 1. Expand training data in `app/data/training_data.py` (add 3-5 more examples per intent)
 2. Add keyword-based rules to `classify_intent()` method for better accuracy
 3. Update response templates in `load_responses()` for more natural conversations
- **Phase 2 Robust Solution:**
 - Research transformer models (BERT/DistilBERT) for better understanding
 - Implement conversation memory and context tracking
 - Add dialogue state management

## Learning Notes
- Simple ML models need much more training data than expected
- Hybrid approach (ML + rule-based) often works better for chatbots
- DOM debugging skills proving valuable - caught the appendChild bug quickly
- Bilingual detection working well - Chinese characters properly identified

## Blocked
None - ready to implement quick fixes

<img src="assets/images/image.png" alt="alt text" width="450px">

---
