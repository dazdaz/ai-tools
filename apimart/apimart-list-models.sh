#!/bin/bash

API_KEY="${APIMART_API_KEY:-YOUR_API_KEY_HERE}"
ENDPOINT="https://api.apimart.ai/v1/models"

if [[ "$API_KEY" == "YOUR_API_KEY_HERE" || -z "$API_KEY" ]]; then
  echo "ERROR: Set your API Mart key!"
  echo "   export APIMART_API_KEY=sk-..."
  exit 1
fi

echo "Fetching available models from API Mart..."
echo "----------------------------------------"

response=$(curl -s -X GET "$ENDPOINT" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json")

if echo "$response" | jq . > /dev/null 2>&1; then
  echo "$response" | jq -r '.data[] | .id' | sort
else
  echo "Failed to fetch models:"
  echo "$response"
fi
