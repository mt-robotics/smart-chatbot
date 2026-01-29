# ============================================================================
# MAKEFILE - Docker Compose Shortcuts
# ============================================================================
# Usage:
#   make dev          - Start development environment with pgAdmin
#   make dev-no-tools - Start development without pgAdmin
#   make down         - Stop all services
#   make restart      - Restart all services
#   make rebuild      - Rebuild image and recreate containers
#   make logs         - Follow backend logs (main service)
#   make logs-all     - Follow all service logs
#   make logs-be      - Backend logs (last 50 lines)
#   make logs-fe      - Frontend logs (last 50 lines)
#   make logs-db      - PostgreSQL logs (last 50 lines)
#   make logs-pg      - pgAdmin logs (last 50 lines)
#   make clean        - Stop and remove volumes (fresh database)
# ============================================================================

# Variables (change these if your env file or compose file names change)
ENV_FILE := .env.development
COMPOSE_FILE := docker-compose.dev.yml

# ============================================================================
# DEVELOPMENT ENVIRONMENT
# ============================================================================

dev:
	@echo "Starting development environment with pgAdmin..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) --profile tools up -d

dev-no-tools:
	@echo "Starting development environment without pgAdmin..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d

down:
	@echo "Stopping all services..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) --profile tools down

restart:
	@echo "Restarting all services..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) --profile tools restart

# ============================================================================
# BUILD AND REBUILD
# ============================================================================

build:
	@echo "Building development image..."
	docker build --target development -t smart-chatbot:dev .

rebuild:
	@echo "Rebuilding image and recreating containers..."
	docker build --target development -t smart-chatbot:dev .
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) --profile tools up -d --force-recreate

# ============================================================================
# LOGS
# ============================================================================
# Two approaches:
# 1. docker compose logs -f <service>  - Follows logs in real-time (requires compose context)
# 2. docker logs <container> --tail N  - Shows last N lines (simpler, works anywhere)
#
# When to use what:
# - Quick check: Use docker logs (faster, simpler)
# - Multiple services: Use docker compose logs -f service1 service2
# - Real-time debugging: Use docker compose logs -f (can add --tail 100 to limit initial output)
# ============================================================================

# Follow backend logs in real-time (recommended for active development)
logs:
	@echo "Following backend logs (Ctrl+C to stop)..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f smart-chatbot

# Follow ALL service logs (useful for debugging service interactions)
logs-all:
	@echo "Following all service logs (Ctrl+C to stop)..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) --profile tools logs -f

# Quick log checks (last 50 lines, no real-time follow)
# Use these for quick inspections without staying attached
logs-be:
	@echo "Backend logs (last 50 lines):"
	@docker logs chatbot_backend_dev --tail 50

logs-fe:
	@echo "Frontend logs (last 50 lines):"
	@docker logs chatbot_frontend_dev --tail 50

logs-db:
	@echo "PostgreSQL logs (last 50 lines):"
	@docker logs chatbot_postgres_dev --tail 50

logs-pg:
	@echo "pgAdmin logs (last 50 lines):"
	@docker logs chatbot_pgadmin_dev --tail 50

# ============================================================================
# DATABASE
# ============================================================================

clean:
	@echo "Stopping services and removing volumes (fresh database)..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down -v

# ============================================================================
# TESTING
# ============================================================================

test:
	@echo "Running test_config.py inside container..."
	docker exec -it chatbot_backend_dev python -m app.utils.test_config

# ============================================================================
# HELP
# ============================================================================

help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start dev environment with pgAdmin"
	@echo "  make dev-no-tools - Start dev environment without pgAdmin"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo ""
	@echo "Build:"
	@echo "  make build        - Build development image"
	@echo "  make rebuild      - Rebuild image and recreate containers"
	@echo ""
	@echo "Logs:"
	@echo "  make logs         - Follow backend logs (real-time)"
	@echo "  make logs-all     - Follow all service logs (real-time)"
	@echo "  make logs-be      - Backend logs (last 50 lines)"
	@echo "  make logs-fe      - Frontend logs (last 50 lines)"
	@echo "  make logs-db      - PostgreSQL logs (last 50 lines)"
	@echo "  make logs-pg      - pgAdmin logs (last 50 lines)"
	@echo ""
	@echo "Database:"
	@echo "  make clean        - Stop and remove volumes (fresh database)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run test_config.py"

.PHONY: dev dev-no-tools down restart build rebuild logs logs-all logs-be logs-fe logs-db logs-pg clean test help
