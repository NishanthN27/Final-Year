# Makefile for Multi-Agentic RAG Interview System

.PHONY: help build up down restart logs clean test migrate seed

# Default target
help:
	@echo "Multi-Agentic RAG Interview System - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build         - Build all Docker images"
	@echo "  make up            - Start all services (development)"
	@echo "  make up-prod       - Start all services (production)"
	@echo "  make down          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View logs from all services"
	@echo "  make logs-backend  - View backend logs"
	@echo "  make logs-frontend - View frontend logs"
	@echo "  make clean         - Remove all containers, volumes, and images"
	@echo "  make migrate       - Run database migrations"
	@echo "  make seed          - Seed the database with initial data"
	@echo "  make shell-backend - Open a shell in the backend container"
	@echo "  make shell-db      - Open a PostgreSQL shell"
	@echo "  make test          - Run tests"
	@echo "  make ps            - Show running containers"
	@echo ""

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start services (development)
up:
	@echo "Starting services (development mode)..."
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Start services (production)
up-prod:
	@echo "Starting services (production mode)..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production services started!"

# Stop services
down:
	@echo "Stopping services..."
	docker-compose down

# Restart services
restart:
	@echo "Restarting services..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres_db

# Clean up everything
clean:
	@echo "Cleaning up containers, volumes, and images..."
	docker-compose down -v --rmi all
	@echo "Cleanup complete!"

# Run database migrations
migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

# Seed database
seed:
	@echo "Seeding database..."
	docker-compose exec backend python scripts/seed_database.py

# Open backend shell
shell-backend:
	docker-compose exec backend /bin/bash

# Open database shell
shell-db:
	docker-compose exec postgres_db psql -U interview_user -d interview_db

# Run tests
test:
	@echo "Running tests..."
	docker-compose exec backend pytest

# Show running containers
ps:
	docker-compose ps

# Health check
health:
	@echo "Checking service health..."
	@echo "Backend health:"
	@curl -f http://localhost:8000/health || echo "Backend not healthy"
	@echo "\nFrontend health:"
	@curl -f http://localhost/health || echo "Frontend not healthy"

# Initial setup
setup:
	@echo "Setting up the application..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your actual configuration values"; \
	fi
	@echo "Building images..."
	@$(MAKE) build
	@echo "Starting services..."
	@$(MAKE) up
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Running migrations..."
	@$(MAKE) migrate
	@echo "\nSetup complete! Access the application at:"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"