.PHONY: help install run test lint format clean docker-up docker-down

help:
	@echo "🏥 PharmaRec AI - Development Commands"
	@echo ""
	@echo "Setup & Install:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Run backend server (FastAPI)"
	@echo "  make frontend-dev  - Run frontend dev server"
	@echo "  make dev           - Run both backend and frontend"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate    - Run database migrations"
	@echo "  make db-reset      - Reset database (remove pharmacy.db)"
	@echo ""
	@echo "ML:"
	@echo "  make train-model   - Train reorder prediction model"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test          - Run pytest tests"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start containers"
	@echo "  make docker-down   - Stop containers"
	@echo "  make docker-logs   - View container logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Clean cache and build artifacts"
	@echo "  make docs-open     - Open API docs in browser"

# Python Environment Setup
install:
	pip install -r requirements.txt

frontend-install:
	cd frontend && npm install

# Development Servers
run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd frontend && npm run dev

dev:
	@echo "Starting both backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@make run &
	@sleep 3
	@make frontend-dev

# Database
db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

db-reset:
	rm -f pharmacy.db
	@echo "Database reset. It will be recreated on next run."

db-seed:
	python scripts/seed_db.py

# ML Training
train-model:
	python ml-engine/training/train_reorder.py

# Testing & Quality
test:
	pytest tests/ -v --tb=short

lint:
	pylint backend/app --disable=all --enable=E,F

format:
	black backend/ frontend/src tests/ -l 100

# Docker Commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "✅ Services started"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-test:
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Utilities
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	@echo "✨ Cleaned up cache and build artifacts"

docs-open:
	@echo "Opening API documentation..."
	python -m webbrowser http://localhost:8000/docs

# Setup for fresh development
setup: install frontend-install db-reset
	@echo "✅ Development environment ready!"
	@echo "Run 'make dev' to start the application"
