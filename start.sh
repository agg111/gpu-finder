#!/bin/bash

# GPU Finder - Start Script
# This script starts both the backend and frontend servers

echo "🚀 Starting GPU Finder Platform..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Start backend server in background
echo "📡 Starting backend server on port 8000..."
python3 server.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend server is running"
else
    echo "⚠️  Backend server may not be ready yet. Check http://localhost:8000/api/health"
fi

echo ""

# Start frontend server
echo "🎨 Starting frontend server on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ GPU Finder Platform is starting!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT

# Keep script running
wait
