#!/bin/bash

echo "Testing GPU Finder API..."
echo ""

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s http://localhost:8000/api/health | jq .
echo ""

# Test 2: Root endpoint
echo "2. Testing root endpoint..."
curl -s http://localhost:8000/ | jq .
echo ""

# Test 3: Test plan endpoint with sample data
echo "3. Testing plan endpoint with sample data..."
echo "Note: This will take ~2 minutes as it fetches real data"
echo ""

curl -X POST http://localhost:8000/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "modelName": "meta-llama/Llama-2-7b-hf",
    "workload": "500GB",
    "duration": "24",
    "budget": "500"
  }' \
  2>&1 | head -20

echo ""
echo "API test complete!"
