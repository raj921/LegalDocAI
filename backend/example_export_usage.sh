#!/bin/bash
# Example usage of export endpoints

API_URL="http://localhost:8000/api"

echo "=== Legal Template Assistant - Export Examples ==="
echo ""

# 1. List all templates
echo "1. Listing all templates..."
curl -s "${API_URL}/templates" | python3 -m json.tool | head -20
echo ""

# 2. Get specific template with variables (replace TEMPLATE_ID)
# TEMPLATE_ID="your-template-id-here"
# echo "2. Getting template details..."
# curl -s "${API_URL}/templates/${TEMPLATE_ID}" | python3 -m json.tool
# echo ""

# 3. Export template variables to CSV
# echo "3. Exporting variables to CSV..."
# curl -s "${API_URL}/templates/${TEMPLATE_ID}/variables/csv" -o template_variables.csv
# echo "Saved to: template_variables.csv"
# cat template_variables.csv
# echo ""

# 4. Export template as Markdown
# echo "4. Exporting template as Markdown..."
# curl -s "${API_URL}/templates/${TEMPLATE_ID}/export" -o template.md
# echo "Saved to: template.md"
# head -20 template.md
# echo ""

# 5. Export draft as Markdown (replace INSTANCE_ID)
# INSTANCE_ID="your-instance-id-here"
# echo "5. Exporting draft as Markdown..."
# curl -s "${API_URL}/draft/${INSTANCE_ID}/export/markdown" -o draft.md
# echo "Saved to: draft.md"
# echo ""

# 6. Export draft as DOCX
# echo "6. Exporting draft as DOCX..."
# curl -s "${API_URL}/draft/${INSTANCE_ID}/export/docx" -o draft.docx
# echo "Saved to: draft.docx"
# file draft.docx
# echo ""

echo "=== Usage Examples ==="
echo ""
echo "To use these endpoints, replace TEMPLATE_ID and INSTANCE_ID with actual IDs"
echo ""
echo "Example curl commands:"
echo "  curl '${API_URL}/templates' | jq"
echo "  curl '${API_URL}/templates/{id}/variables/csv' -o vars.csv"
echo "  curl '${API_URL}/templates/{id}/export' -o template.md"
echo "  curl '${API_URL}/draft/{id}/export/markdown' -o draft.md"
echo "  curl '${API_URL}/draft/{id}/export/docx' -o draft.docx"
echo ""
