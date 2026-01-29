# ============================================================================
# MULTI-STAGE DOCKERFILE: Development + Production
# ============================================================================
# What is multi-stage build?
# - ONE Dockerfile that can create DIFFERENT images for dev vs prod
# - Uses "FROM ... AS stage-name" to define stages
# - Build specific stage with: `docker build --target stage-name -t image:tag .`
#
# Benefits:
# - Single source of truth (one Dockerfile, not two separate files)
# - Share common setup (base stage) between dev and prod
# - Actually different images (not just different docker-compose configs)
#
# Reference: docker_images_vs_services.md - Approach B (Multi-Stage Dockerfile)
# ============================================================================


# ============================================================================
# STAGE 1: BASE (Shared by both dev and prod)
# ============================================================================
# Why separate base stage?
# - Avoid duplicating common setup (Python install, uv setup, dependencies)
# - Changes here affect both dev and prod
# - Faster builds (shared layers cached once)
# ============================================================================

FROM python:3.11-slim AS base

# Set working directory to project root
# NOTE: Changed from /app to /project to support absolute imports (app.*)
# This allows imports like "from app.utils.config import get_logger"
# to work consistently in both IDE and Docker environments
WORKDIR /project

# Install uv (modern Python package manager)
# COPY --from=IMAGE means: copy FROM another image (not from host)
# Source: /uv (binary from astral-sh's image)
# Destination: /usr/local/bin/uv (system PATH in our image)
# Why uv? Faster than pip, uses lockfile (uv.lock) for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (for layer caching optimization)
# Why before code? Dependencies change less frequently than code
# If only code changes, Docker reuses this cached layer (faster rebuilds)
#
# What are these files?
# - pyproject.toml = Python project metadata + dependency list (like package.json)
# - uv.lock = Exact pinned versions of all dependencies (like package-lock.json)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# Using "uv pip install" instead of "uv sync" for system-wide installation
#
# Flags explained:
# pip install      = Use pip-compatible interface (supports --system)
# --system         = Install to system Python (not venv) - CRITICAL for Docker
# -r pyproject.toml = Install from project dependencies
#
# Why --system is required in Docker:
#
# WITHOUT --system (default behavior):
#   - uv creates a virtual environment (.venv/) and installs packages there
#   - Executables end up in: .venv/bin/uvicorn (hidden location)
#   - Docker can't find them in PATH → Error: "No such file or directory"
#   - You'd need to use "uv run uvicorn ..." which adds complexity
#
# WITH --system:
#   - uv installs directly to system Python (no .venv/ folder created)
#   - Executables go to: /usr/local/bin/uvicorn (standard PATH location)
#   - Docker finds them immediately → uvicorn command just works
#   - Cleaner CMD: just "uvicorn ..." instead of "uv run uvicorn ..."
#
# Why virtual environments (.venv/) are "extra" in Docker:
#   On your laptop: .venv/ needed to separate multiple projects
#     - Project A needs pandas 1.0
#     - Project B needs pandas 2.0
#     - .venv/ prevents conflicts
#
#   In Docker: Container itself provides isolation
#     - Container 1 has its own Python + packages (completely isolated)
#     - Container 2 has its own Python + packages (can't see Container 1)
#     - .venv/ inside container = locking a safe inside another safe (redundant)
#
# Analogy:
#   Without --system = Hiding keys in a drawer (Docker can't find them)
#   With --system    = Putting keys on the key hook (Docker finds them easily)
#
# This replaces traditional: pip install -r requirements.txt
RUN uv pip install --system -r pyproject.toml

# Copy application code
# NOTE: Changed to copy entire project instead of just app/ directory
# This maintains the project structure: /project/app/, /project/pyproject.toml, etc.
# Allows absolute imports like "from app.utils.config import get_logger" to work
#
# Source: ./ (entire project root on host)
# Destination: . (current WORKDIR, which is /project inside container)
#
# Result: Files land at /project/app/main.py, /project/app/models/, etc.
COPY . .

# ============================================================================
# Why we DON'T set CMD or ENV here?
# - Base stage is INCOMPLETE - not meant to run directly
# - Each final stage (development/production) will set their own CMD and ENV
# - This keeps base stage flexible for different use cases
# ============================================================================


# ============================================================================
# STAGE 2: DEVELOPMENT
# ============================================================================
# When to use this stage?
# - Local development on host machine
# - Need hot reload (code changes auto-restart server)
# - Need debug mode (verbose logging, error traces)
# - Don't care about image size or optimization
#
# How to build: docker build --target development -t smart-chatbot:dev .
# ============================================================================

FROM base AS development

# Set environment variables for development
# DEBUG=true enables:
# - Verbose logging
# - Detailed error traces in API responses
# - Development-only features
ENV DEBUG=true

# Development-specific command
# Flags explained:
# uvicorn             = ASGI server for FastAPI (installed to system with --system flag)
# app.main:app        = Import path (app/main.py file, app object) - using absolute import
# --reload            = Watch for code changes, auto-restart server (hot reload)
# --host 0.0.0.0      = Listen on ALL network interfaces (required for Docker)
# --port 8000         = Port number (matches EXPOSE, nginx proxy_pass target)
#
# NOTE: Changed from "main:app" to "app.main:app" to match absolute import structure
# This works because WORKDIR is /project (contains app/ directory)
#
# Why different from production CMD?
# - --reload is EXPENSIVE (file watching, auto-restart) - only for development
# - Production uses gunicorn (multi-worker, more robust)
#
# Note: No "uv run" needed because we used --system flag during install
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# Port documentation (doesn't actually open ports)
# How this works with docker-compose in DEVELOPMENT:
#
#   smart-chatbot:
#     image: smart-chatbot:dev
#     ports:
#       - "8000:8000"    ← EXPOSED to host
#     volumes:
#       - ./app:/app     ← Bind mount (code changes reflect immediately)
#
# Access options:
# - Direct: http://localhost:8000
# - Via nginx proxy: http://smart-chatbot.local (requires /etc/hosts + nginx config)
EXPOSE 8000


# ============================================================================
# STAGE 3: PRODUCTION
# ============================================================================
# When to use this stage?
# - Deploying to server (Railway, AWS, DigitalOcean, etc.)
# - Need performance (multi-worker, optimized)
# - Need security (debug off, minimal attack surface)
# - Care about image size and resource usage
#
# How to build: docker build --target production -t smart-chatbot:prod .
# ============================================================================

FROM base AS production

# Set environment variables for production
# DEBUG=false disables:
# - Verbose logging (only errors/warnings logged)
# - Detailed error traces (attackers can't see internal structure)
# - Development-only features
ENV DEBUG=false

# Production-specific command
# Why gunicorn instead of uvicorn?
# - Gunicorn = Production-grade WSGI server with process management
# - Can run MULTIPLE workers (parallel request handling)
# - Better stability, graceful shutdowns, worker health monitoring
#
# Flags explained:
# gunicorn                     = WSGI server (wraps uvicorn workers, installed to system)
# app.main:app                 = Import path (app/main.py file, app object) - using absolute import
# -k uvicorn.workers.UvicornWorker  = Use Uvicorn worker class (for ASGI support)
# -w 4                         = 4 worker processes (adjust based on CPU cores)
# -b 0.0.0.0:8000             = Bind to all interfaces, port 8000
#
# NOTE: Changed from "main:app" to "app.main:app" to match absolute import structure
# This works because WORKDIR is /project (contains app/ directory)
#
# Worker count rule of thumb: (2 × CPU_cores) + 1
# Example: 2-core server → 5 workers, 4-core server → 9 workers
#
# Note: No "uv run" needed because we used --system flag during install
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]

# Port documentation (doesn't actually open ports)
# How this works with docker-compose in PRODUCTION:
#
#   smart-chatbot:
#     image: smart-chatbot:prod
#     expose:
#       - 8000           ← INTERNAL ONLY (only other containers can access)
#     # NO "ports:" section = NOT accessible from host/internet
#
#   nginx:
#     ports:
#       - "80:80"        ← Only nginx exposed to internet
#     # nginx.conf: proxy_pass http://smart-chatbot:8000
#
# Request flow: Internet → nginx:80 → smart-chatbot:8000 (internal)
EXPOSE 8000


# ============================================================================
# HOW TO USE THIS DOCKERFILE
# ============================================================================
#
# BUILD DEVELOPMENT IMAGE:
#   docker build --target development -t smart-chatbot:dev .
#
# BUILD PRODUCTION IMAGE:
#   docker build --target production -t smart-chatbot:prod .
#
# BUILD BOTH (for testing):
#   docker build --target development -t smart-chatbot:dev .
#   docker build --target production -t smart-chatbot:prod .
#
# VERIFY IMAGES EXIST:
#   docker images | grep smart-chatbot
#
# RUN DEVELOPMENT CONTAINER (standalone, no compose):
#   docker run -p 8000:8000 -v $(pwd)/app:/app smart-chatbot:dev
#
# RUN PRODUCTION CONTAINER (standalone, no compose):
#   docker run -p 8000:8000 smart-chatbot:prod
#
# ============================================================================
# WHAT'S THE DIFFERENCE BETWEEN IMAGES?
# ============================================================================
#
# smart-chatbot:dev (DEVELOPMENT)
# ✅ Has: --reload flag (hot reload for code changes)
# ✅ Has: DEBUG=true (verbose logging, error traces)
# ✅ Has: Single-worker uvicorn (simpler debugging)
# ❌ Slower, higher memory usage, less secure
#
# smart-chatbot:prod (PRODUCTION)
# ✅ Has: Multi-worker gunicorn (parallel requests, better performance)
# ✅ Has: DEBUG=false (minimal logging, no error traces)
# ✅ Has: Optimized for speed and security
# ❌ No hot reload (must rebuild image for code changes)
#
# ============================================================================
# WHAT ABOUT DOCKER-COMPOSE?
# ============================================================================
# You can use these images in docker-compose.yml:
#
# DEVELOPMENT (docker-compose.dev.yml):
#   services:
#     smart-chatbot:
#       image: smart-chatbot:dev    ← Uses development stage
#       ports:
#         - "8000:8000"              ← Exposed to host (localhost:8000)
#       volumes:
#         - ./app:/app               ← Bind mount (hot reload works!)
#
# PRODUCTION (docker-compose.prod.yml):
#   services:
#     smart-chatbot:
#       image: smart-chatbot:prod   ← Uses production stage
#       expose:
#         - 8000                     ← Internal only (nginx access only)
#       # NO volumes (code baked into image)
#
#     nginx:
#       image: nginx:alpine
#       ports:
#         - "80:80"                  ← Only nginx exposed to internet
#
# ============================================================================
