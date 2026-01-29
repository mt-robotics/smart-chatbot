# Docker Setup Guide

Complete guide for running Smart Chatbot with Docker in both development and production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment](#development-environment)
3. [Production Environment](#production-environment)
4. [Common Commands](#common-commands)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose V2+ (included with Docker Desktop)

### Build Docker Images

Before using docker-compose, build both images:

```bash
# Build development image
docker build --target development -t smart-chatbot:dev .

# Build production image
docker build --target production -t smart-chatbot:prod .

# Verify images exist
docker images | grep smart-chatbot
```

**Expected output:**
```
smart-chatbot   dev    44b9fe83a94a   2 minutes ago   879MB
smart-chatbot   prod   094a56b14934   1 minute ago    879MB
```

---

## Development Environment

### Setup for Local Development

#### 1. Create External Proxy Network

```bash
docker network create proxy-network
```

This network allows integration with your host machine's nginx proxy.

#### 2. Configure Host nginx (Optional but Recommended)

Add to `/etc/hosts`:
```
127.0.0.1 smart-chatbot.local
```

Add to nginx config (e.g., `/usr/local/etc/nginx/servers/smart-chatbot.conf`):
```nginx
server {
    listen 80;
    server_name smart-chatbot.local;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Reload nginx:
```bash
sudo nginx -s reload
```

#### 3. Start Development Environment

**Basic (without pgAdmin):**
```bash
docker-compose -f docker-compose.dev.yml up
```

**With pgAdmin (database management tool):**
```bash
docker-compose -f docker-compose.dev.yml up --profile tools
```

**Background mode:**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### 4. Access Services

- **Backend API (direct):** http://localhost:8000
- **Backend API (nginx proxy):** http://smart-chatbot.local
- **PostgreSQL:** localhost:5432
  - Database: `chatbot_dev`
  - User: `chatbot_user`
  - Password: `chatbot_pass`
- **pgAdmin** (if started with `--profile tools`): http://localhost:8080
  - Email: `admin@chatbot.local`
  - Password: `admin123`

#### 5. Development Workflow

**Hot reload is enabled!** Any changes to `./app/*` files will automatically:
1. Trigger uvicorn to detect file changes
2. Restart the server
3. Apply your code changes immediately

**Test the hot reload:**
```bash
# Make a change to any file in ./app/
# Watch docker-compose logs to see server restart
docker-compose -f docker-compose.dev.yml logs -f smart-chatbot
```

#### 6. Stop Development Environment

```bash
# Stop containers (keep data)
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (fresh database)
docker-compose -f docker-compose.dev.yml down -v
```

---

## Production Environment

### Setup for Production Deployment

#### 1. Configure Environment Variables

**Option A: Use .env.prod file (recommended)**
```bash
# Create production environment file
cat > .env.prod << EOF
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://chatbot_user:your_secure_password_here@postgres:5432/chatbot_prod
EOF
```

**Option B: Export environment variables**
```bash
export POSTGRES_PASSWORD=your_secure_password_here
```

#### 2. Configure Nginx

Edit `nginx/conf.d/default.conf` and change:
```nginx
server_name localhost;  # Change to your actual domain
```

To:
```nginx
server_name your-domain.com www.your-domain.com;
```

#### 3. Start Production Environment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 4. Access Services

- **Public API:** http://your-domain.com (via nginx)
- **Backend:** NOT accessible from outside (internal network only)
- **PostgreSQL:** NOT accessible from outside (internal network only)

#### 5. Verify Services are Running

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check health checks
docker-compose -f docker-compose.prod.yml ps | grep healthy
```

**Expected output:**
```
chatbot_backend_prod   healthy
chatbot_nginx_prod     healthy
chatbot_postgres_prod  healthy
```

#### 6. View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f smart-chatbot
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f postgres
```

---

## Common Commands

### Rebuild After Code Changes

**Development:**
```bash
# Rebuild dev image
docker build --target development -t smart-chatbot:dev .

# Restart development services
docker-compose -f docker-compose.dev.yml up -d --force-recreate
```

**Production:**
```bash
# Rebuild production image
docker build --target production -t smart-chatbot:prod .

# Deploy new version (zero-downtime with health checks)
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### Database Operations

**Backup database:**
```bash
# Development
docker-compose -f docker-compose.dev.yml exec postgres \
    pg_dump -U chatbot_user chatbot_dev > backup_dev.sql

# Production
docker-compose -f docker-compose.prod.yml exec postgres \
    pg_dump -U chatbot_user chatbot_prod > backup_prod.sql
```

**Restore database:**
```bash
# Development
docker-compose -f docker-compose.dev.yml exec -T postgres \
    psql -U chatbot_user chatbot_dev < backup_dev.sql

# Production
docker-compose -f docker-compose.prod.yml exec -T postgres \
    psql -U chatbot_user chatbot_prod < backup_prod.sql
```

**Access PostgreSQL shell:**
```bash
# Development
docker-compose -f docker-compose.dev.yml exec postgres \
    psql -U chatbot_user -d chatbot_dev

# Production
docker-compose -f docker-compose.prod.yml exec postgres \
    psql -U chatbot_user -d chatbot_prod
```

### Clean Up

**Remove all containers, networks, and volumes:**
```bash
# Development
docker-compose -f docker-compose.dev.yml down -v

# Production
docker-compose -f docker-compose.prod.yml down -v
```

**Remove images:**
```bash
docker rmi smart-chatbot:dev smart-chatbot:prod
```

**Prune unused Docker resources:**
```bash
docker system prune -a --volumes
```

---

## Troubleshooting

### Issue: Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

### Issue: proxy-network Not Found

**Error:**
```
network proxy-network declared as external, but could not be found
```

**Solution:**
```bash
# Create the network
docker network create proxy-network
```

### Issue: Database Connection Failed

**Error in logs:**
```
connection to server at "postgres" failed
```

**Solution:**
```bash
# Check if postgres service is healthy
docker-compose -f docker-compose.dev.yml ps

# View postgres logs
docker-compose -f docker-compose.dev.yml logs postgres

# Restart services
docker-compose -f docker-compose.dev.yml restart
```

### Issue: Hot Reload Not Working

**Problem:** Changes to code don't trigger server restart

**Solution:**
1. Verify volume mount exists:
   ```bash
   docker-compose -f docker-compose.dev.yml config | grep volumes -A 3
   ```

2. Check uvicorn is running with --reload:
   ```bash
   docker-compose -f docker-compose.dev.yml exec smart-chatbot ps aux
   ```

3. Restart development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml restart smart-chatbot
   ```

### Issue: Nginx Cannot Reach Backend

**Error in nginx logs:**
```
connect() failed (111: Connection refused) while connecting to upstream
```

**Solution:**
1. Verify backend is running:
   ```bash
   docker-compose -f docker-compose.prod.yml ps smart-chatbot
   ```

2. Check backend health:
   ```bash
   docker-compose -f docker-compose.prod.yml exec smart-chatbot curl http://localhost:8000/health
   ```

3. Verify network connectivity:
   ```bash
   docker-compose -f docker-compose.prod.yml exec nginx ping smart-chatbot
   ```

### Issue: Permission Denied on Volumes

**Error:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Or run with sudo (not recommended for production)
sudo docker-compose -f docker-compose.dev.yml up
```

### Check Container Health

```bash
# Development
docker inspect chatbot_backend_dev --format='{{.State.Health.Status}}'

# Production
docker inspect chatbot_backend_prod --format='{{.State.Health.Status}}'
docker inspect chatbot_nginx_prod --format='{{.State.Health.Status}}'
```

**Expected:** `healthy`

---

## Architecture Diagrams

### Development Architecture

```
┌─────────────────────────────────────────────────────┐
│ Host Machine                                        │
│                                                     │
│  ┌──────────────┐         ┌──────────────────────┐ │
│  │ Nginx Proxy  │────────▶│ Docker Container     │ │
│  │ (Optional)   │         │ smart-chatbot:dev    │ │
│  └──────────────┘         │ Port: 8000           │ │
│         │                 │ Volume: ./app:/app   │ │
│         │                 │ Hot Reload: ON       │ │
│         │                 └──────────┬───────────┘ │
│         │                            │             │
│         │                 ┌──────────▼───────────┐ │
│         │                 │ PostgreSQL           │ │
│         │                 │ Port: 5432           │ │
│         │                 │ Volume: Persistent   │ │
│         │                 └──────────────────────┘ │
│         │                            │             │
│         ▼                            ▼             │
│  Access via:                   Access via:         │
│  - localhost:8000              - localhost:5432    │
│  - smart-chatbot.local         - DBeaver/psql     │
└─────────────────────────────────────────────────────┘
```

### Production Architecture

```
┌─────────────────────────────────────────────────────┐
│ Docker Internal Network (backend-network)          │
│                                                     │
│  ┌──────────────────────┐                          │
│  │ Nginx Container      │◀────── Port 80 (Public) │
│  │ nginx:alpine         │                          │
│  └──────────┬───────────┘                          │
│             │                                       │
│             │ proxy_pass                            │
│             │                                       │
│  ┌──────────▼───────────┐                          │
│  │ Backend Container    │                          │
│  │ smart-chatbot:prod   │                          │
│  │ Port: 8000 (Internal)│                          │
│  │ Workers: 4           │                          │
│  │ Debug: OFF           │                          │
│  └──────────┬───────────┘                          │
│             │                                       │
│             │ DATABASE_URL                          │
│             │                                       │
│  ┌──────────▼───────────┐                          │
│  │ PostgreSQL Container │                          │
│  │ Port: 5432 (Internal)│                          │
│  │ Volume: Persistent   │                          │
│  └──────────────────────┘                          │
│                                                     │
│  Internet ──▶ nginx:80 ──▶ backend:8000 ──▶ DB    │
│               (PUBLIC)     (INTERNAL)      (INTERNAL)
└─────────────────────────────────────────────────────┘
```

---

## Next Steps

### For Development:
1. ✅ Build images
2. ✅ Create proxy-network
3. ✅ Configure host nginx (optional)
4. ✅ Start services
5. ✅ Test API endpoints
6. ✅ Develop with hot reload

### For Production:
1. ✅ Build production image
2. ✅ Set production passwords
3. ✅ Configure domain name
4. ⬜ Set up SSL/HTTPS (recommended)
5. ⬜ Configure firewall rules
6. ⬜ Set up monitoring
7. ⬜ Configure automated backups
8. ✅ Deploy services

---

## References

- **Dockerfile:** `/Dockerfile` - Multi-stage build definition
- **Dev Compose:** `/docker-compose.dev.yml` - Development environment
- **Prod Compose:** `/docker-compose.prod.yml` - Production environment
- **Nginx Config:** `/nginx/` - Nginx reverse proxy configuration
- **Environment:** `/.env` - Development environment variables

---

**Questions? Issues?** Check the troubleshooting section or review container logs.
