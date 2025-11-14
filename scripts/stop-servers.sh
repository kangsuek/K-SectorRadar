#!/bin/bash

# K-SectorRadar 서버 중지 스크립트

echo "Stopping K-SectorRadar servers..."

# Backend 중지
pkill -f "uvicorn app.main:app"

# Frontend 중지
pkill -f "vite"

echo "Servers stopped."

