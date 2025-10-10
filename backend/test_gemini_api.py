#!/usr/bin/env python3
"""Quick test to verify Gemini API is working"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')
print(f"API Key configured: {API_KEY[:10]}..." if API_KEY else "No API Key found!")

try:
    # Configure Gemini
    genai.configure(api_key=API_KEY)
    
    # Test 1: Simple text generation
    print("\n🧪 Test 1: Simple text generation...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Hello, API is working!' in exactly 5 words.")
    print(f"✅ Response: {response.text}")
    
    # Test 2: Embedding generation
    print("\n🧪 Test 2: Embedding generation...")
    result = genai.embed_content(
        model='models/text-embedding-004',
        content="Test document",
        task_type="retrieval_document"
    )
    embedding_length = len(result['embedding'])
    print(f"✅ Embedding generated: {embedding_length} dimensions")
    
    # Test 3: JSON extraction (like our variable extraction)
    print("\n🧪 Test 3: JSON extraction test...")
    prompt = """Extract information from this text as JSON:
    
Text: "The tenant John Smith agrees to pay $1500 per month."

Return JSON:
{
    "name": "extracted name",
    "amount": "extracted amount"
}

Return ONLY valid JSON."""
    
    response = model.generate_content(prompt)
    result_text = response.text.strip()
    
    # Clean JSON markdown
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    if result_text.startswith("```"):
        result_text = result_text[3:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]
    
    import json
    parsed = json.loads(result_text.strip())
    print(f"✅ JSON parsed: {parsed}")
    
    print("\n✅ ALL TESTS PASSED! Gemini API is working correctly.")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print("\nPossible issues:")
    print("- API key is invalid or expired")
    print("- Network connectivity issues")
    print("- API quota exceeded")
    print("- google-generativeai package not installed")
