#!/bin/bash

# K-SectorRadar 서버 시작 스크립트

echo "Starting K-SectorRadar servers..."

# Backend 시작
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "Starting backend server..."
uvicorn app.main:app --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Frontend 시작
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi

echo "Starting frontend server..."
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "To stop servers, run: ./scripts/stop-servers.sh"


