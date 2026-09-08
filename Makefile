.PHONY: install test run-backend run-frontend build-frontend migrate docker-up
install:
	python -m venv .venv
	.venv/bin/pip install -r backend/requirements-dev.txt
	npm --prefix frontend ci
migrate:
	.venv/bin/alembic -c backend/alembic.ini upgrade head
test:
	.venv/bin/pytest -q
run-backend:
	.venv/bin/uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
run-frontend:
	npm --prefix frontend run dev
build-frontend:
	npm --prefix frontend run build
docker-up:
	docker compose up --build -d
