#!/bin/bash

# Test script for Legal Template Assistant API
BASE_URL="http://localhost:8000/api"

echo "=== Testing Legal Template Assistant API ==="
echo ""

# 1. Health Check
echo "1. Health Check"
curl -X GET "${BASE_URL}/health"
echo -e "\n"

# 2. List Templates (should be empty initially)
echo "2. List Templates"
curl -X GET "${BASE_URL}/templates"
echo -e "\n"

# 3. Upload Template (create a test file first)
echo "3. Upload Template"
echo "Note: Create a test DOCX file first, then run:"
echo "curl -X POST \"${BASE_URL}/templates/upload\" -F \"file=@test_document.docx\""
echo -e "\n"

# 4. Match Template (after uploading)
echo "4. Match Template to Query"
curl -X POST "${BASE_URL}/draft/match" \
  -H "Content-Type: application/json" \
  -d '{"query": "Draft a notice to insurance company"}'
echo -e "\n"

# 5. Create Draft Instance
echo "5. Create Draft Instance"
echo "Note: Replace TEMPLATE_ID with actual template ID"
echo "curl -X POST \"${BASE_URL}/draft/instance\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"template_id\": \"TEMPLATE_ID\", \"query\": \"Draft notice\"}'"
echo -e "\n"

# 6. Update Answers
echo "6. Update Draft Answers"
echo "curl -X POST \"${BASE_URL}/draft/answers\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"instance_id\": \"INSTANCE_ID\", \"answers\": {\"policy_number\": \"12345\"}}'"
echo -e "\n"

# 7. Generate Draft
echo "7. Generate Final Draft"
echo "curl -X POST \"${BASE_URL}/draft/generate\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"instance_id\": \"INSTANCE_ID\"}'"
echo -e "\n"

echo "=== API Test Script Complete ==="
