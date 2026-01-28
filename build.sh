#!/bin/bash
set -e

echo "=== Building CSGB CRM ==="

echo "Step 1: Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Step 2: Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "=== Build complete ==="
echo "Frontend built to: app/static/"
ls -la app/static/ || echo "Warning: app/static/ directory not found"
