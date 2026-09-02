.PHONY: help install test test-verbose run-backend run-frontend build-frontend docker-up docker-down clean

help:
	@echo "AISMM — AI Social Media Management System"
	@echo "Available commands:"
	@echo "  make install        Install Python and Node dependencies"
	@echo "  make test           Run all 194 automated backend tests"
	@echo "  make run-backend    Start FastAPI backend server on :8000"
	@echo "  make run-frontend   Start Vite React development server on :5173"
	@echo "  make build-frontend Build production frontend assets"
	@echo "  make docker-up      Start full-stack container environment"
	@echo "  make docker-down    Stop all containers"
	@echo "  make clean          Clean temporary files and cache"

install:
	pip install -r requirements.txt
	cd frontend && npm install

test:
	pytest -q

test-verbose:
	pytest -v

run-backend:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
