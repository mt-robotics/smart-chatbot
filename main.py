import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

    # pylint: disable=pointless-string-statement
    """
    Why we use import string "app.main:app" instead of importing the app object:
    
    BAD APPROACH:
    from app.main import app
    uvicorn.run(app, reload=True)  # ← This causes reload issues
    
    PROBLEMS WITH IMPORTING APP OBJECT:
    1. App is imported once at startup - Python caches the module
    2. When files change, uvicorn can't "reimport" the cached app
    3. Hot reload fails - you must manually restart the server
    4. Slower development cycle - constant manual restarts
    5. Risk of testing old code after changes
    
    WHY IMPORT STRING WORKS:
    1. "app.main:app" tells uvicorn WHERE to find the app, not the app itself
    2. Uvicorn can reimport the module fresh when files change
    3. Hot reload works properly - automatic server restart on changes
    4. Faster development - just save file and test immediately
    5. Always testing the latest code changes
    
    PRODUCTION NOTE:
    - In production, reload=False anyway, so this doesn't matter
    - But using import string is still the recommended practice
    - Railway uses: uvicorn app.main:app (import string format)
    
    DEVELOPMENT BENEFIT:
    - Change Python code → Save file → Server auto-restarts → Test immediately
    - No more manual stop/start cycles during development
    """
