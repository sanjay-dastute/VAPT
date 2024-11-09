#!/bin/bash

echo "Starting VAPT Scanner services..."

# Start PostgreSQL if not running
if ! pg_isready; then
    echo "Starting PostgreSQL..."
    sudo service postgresql start
    sleep 5
fi

# Start backend
cd backend
echo "Starting backend server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 10

# Start frontend
cd frontend
echo "Starting frontend server..."
npm start &
cd ..

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 15

# Check services
echo "Checking services..."
curl -s http://localhost:8000/docs > /dev/null && echo "Backend is running" || echo "Backend failed to start"
curl -s http://localhost:3000 > /dev/null && echo "Frontend is running" || echo "Frontend failed to start"

echo "Services should be running now!"
