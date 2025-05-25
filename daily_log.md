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

# May 26, 2025 - Log 03

## Done
- **Implemented comprehensive production configuration system**
    - Created environment-specific config files (.env.development, .env.production, .env.staging)
    - Built ConfigManager class with singleton pattern (app/config.py)
    - Replaced all print() statements with proper structured logging
    - Set up environment-aware logging with different levels (DEBUG for dev, INFO for prod)

- **Deployed complete application to production**
    - Successfully deployed backend to Railway.app (https://smart-chatbot-production.up.railway.app)
    - Deployed frontend to Netlify (https://regal-custard-47715d.netlify.app)
    - Both environments working with live demo accessible to recruiters

- **Built automated frontend configuration system**
    - Created Python build script (scripts/build-frontend-config.py) to generate frontend config from .env files
    - Implemented environment auto-detection (localhost → dev, live domain → production)
    - Eliminated configuration duplication between frontend and backend
    - Added validation and helpful error messages for deployment issues

- **Enhanced NLP accuracy and functionality**
    - Applied quick fixes to intent classification (keyword rules + expanded training data)
    - Fixed NumPy serialization issues preventing FastAPI JSON responses
    - Improved conversation management with proper logging throughout
    - Added comprehensive error handling and debug information

- **Professional project setup and documentation**
    - Added MIT License file for portfolio compliance
    - Updated requirements.txt with python-dotenv dependency
    - Created comprehensive README.md with live demo URLs
    - Added technical documentation (NLP concepts, Git workflow, regex guide) in docs/ directory

## Bugs Encountered
**🔧 Poor Context Understanding** (from May 23) - SOLVED ✅
- **Solution**: Added keyword-based rules alongside ML classification
- **Fix**: Hybrid approach checking for "buy/purchase" vs "cancel/refund" keywords before ML fallback
- **Result**: Intent classification accuracy improved significantly for common cases
- **Files Changed**: `app/models/nlp_engine.py`, `app/data/training_data.py`

**🐛 NumPy Serialization Error** - SOLVED ✅
- **What**: `PydanticSerializationError: Unable to serialize unknown type: <class 'numpy.bool'>`
- **How**: FastAPI couldn't serialize NumPy types returned by scikit-learn to JSON
- **Where**: `/chat` endpoint when returning confidence scores and intent classifications
- **Fix**: Added explicit type conversion `str(intent), float(confidence)` in classify_intent method
- **Root Cause**: scikit-learn returns numpy.str_ and numpy.float64 instead of Python primitives

**🐛 Frontend Configuration Loading Race Condition** - SOLVED ✅
- **What**: `Cannot read properties of undefined (reading 'DEBUG')` in browser console
- **How**: JavaScript tried to use config before config.js finished loading
- **Where**: `frontend/index.html` initialization code
- **Fix**: Implemented async `waitForConfig()` function with Promise-based loading
- **Result**: Frontend now properly waits for configuration before initializing

**🐛 CORS Policy Blocking Production Frontend** - SOLVED ✅
- **What**: `Access to fetch blocked by CORS policy: No 'Access-Control-Allow-Origin' header`
- **How**: Railway backend wasn't configured to allow requests from Netlify domain
- **Where**: Production environment CORS configuration
- **Fix**: Added `https://regal-custard-47715d.netlify.app` to CORS_ORIGINS in .env.production
- **Result**: Frontend successfully communicates with backend API in production

**🐛 Double Slash in API URLs** - SOLVED ✅
- **What**: Generated URLs had double slashes: `api.railway.app//chat`
- **How**: BACKEND_API_URL in .env had trailing slash, frontend added another
- **Where**: Generated frontend/config.js file
- **Fix**: Removed trailing slash from BACKEND_API_URL environment variable
- **Prevention**: Added URL validation to build script

## Next
- **Immediate (Next Session):**
 - Implement database integration with SQLAlchemy for conversation persistence
 - Add user profile tracking and preference learning
 - Create conversation history and context awareness

- **Future Enhancements:**
 - Upgrade to transformer models (sentence-transformers) for better NLP accuracy
 - Add RAG (Retrieval-Augmented Generation) with vector database
 - Implement real-time analytics dashboard

## Learning Notes
- **Professional Environment Management**: Single source of truth with .env files + automated config generation eliminates deployment errors and shows enterprise-level practices
- **Logging Best Practices**: Centralized logging configuration in config.py with environment-specific formatting (detailed dev logs, clean production logs)
- **Git Workflow Mastery**: Learned professional branching strategies, hotfix procedures, and when to skip development branch for portfolio projects
- **Production Deployment Pipeline**: End-to-end deployment from local development → Railway (backend) + Netlify (frontend) with environment-specific configurations
- **API Serialization Issues**: NumPy types from ML libraries need explicit conversion to Python primitives for JSON serialization
- **CORS Configuration**: Production CORS requires exact domain matching - wildcards work for development but not production security

## Blocked
None - application fully functional in production, ready for recruiter demonstration

## Portfolio Impact
- **Live Demo**: Recruiters can immediately test bilingual chatbot capabilities
- **Professional Architecture**: Shows understanding of environment management, logging, deployment pipelines
- **Technical Depth**: Demonstrates NLP implementation, API design, and full-stack development
- **Enterprise Practices**: Configuration management, Git workflows, and production deployment experience

---