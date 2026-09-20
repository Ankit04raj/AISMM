#!/usr/bin/env bash
# AISMM Local Development Server Runner
# Starts FastAPI backend (port 8000) and Vite frontend (port 5173) concurrently.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "========================================================"
echo "Starting AISMM AI Social Media Manager (Local Dev)"
echo "========================================================"

# 1. Ensure virtualenv exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please create one with: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 2. Run database migrations to head
echo "[1/3] Running database migrations..."
PYTHONPATH=. .venv/bin/python -m alembic -c backend/alembic.ini upgrade head

# 3. Start backend
echo "[2/3] Starting FastAPI backend on http://127.0.0.1:8000..."
PYTHONPATH=. .venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 4. Start frontend
echo "[3/3] Starting Vite frontend on http://localhost:5173..."
cd "$REPO_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

trap "echo 'Shutting down AISMM...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM EXIT

wait
