import google.generativeai as genai
import json
import logging
from typing import List, Dict, Any, Optional
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL
        # Set timeout to 10 minutes to handle long PDF processing
        self.request_options = {'timeout': 600}
    
    def extract_variables(self, text: str, existing_variables: Optional[List[Dict]] = None) -> Dict[str, Any]:
        logger.info(f"Extracting variables from {len(text)} characters...")
        existing_vars_context = ""
        if existing_variables:
            existing_vars_context = f"\n\nExisting variables to reuse:\n{json.dumps(existing_variables, indent=2)}"
            logger.info(f"Reusing {len(existing_variables)} existing variables")
        
        prompt = f"""You are a legal document templating assistant. Extract variables from the following legal document text.

Extract:
1. Variables that should be filled in (names, dates, amounts, addresses, etc.)
2. Metadata (document type, jurisdiction if mentioned)
3. Tags for categorization

Do NOT variable-ize:
- Statutory text or legal citations
- Standard legal language
- Section headings

{existing_vars_context}

Document text:
{text}

Return a JSON object with this structure:
{{
    "variables": [
        {{
            "key": "snake_case_key",
            "label": "Human-friendly label",
            "description": "What this variable represents",
            "example": "Sample value for guidance",
            "data_type": "text|number|date|email",
            "is_required": true|false
        }}
    ],
    "doc_type": "type of document",
    "jurisdiction": "jurisdiction if mentioned",
    "tags": ["tag1", "tag2"]
}}

IMPORTANT: Variable keys MUST be snake_case (lowercase with underscores).

Return ONLY valid JSON, no other text."""

        try:
            import time
            start_time = time.time()
            logger.info("→ Calling Gemini API for variable extraction...")
            response = self.model.generate_content(prompt, request_options=self.request_options)
            elapsed = time.time() - start_time
            result_text = response.text.strip()
            logger.info(f"✓ Gemini API response received in {elapsed:.1f}s")
            
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            logger.info(f"✓ Extracted {len(result.get('variables', []))} variables")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return {"variables": [], "doc_type": "unknown", "jurisdiction": "", "tags": []}
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise
    
    def match_templates(self, query: str, candidates: List[Dict]) -> Dict[str, Any]:
        candidates_text = "\n\n".join([
            f"Template {i+1}:\n"
            f"  Title: {c['title']}\n"
            f"  Type: {c.get('doc_type', 'N/A')}\n"
            f"  Description: {c.get('description', 'N/A')}"
            for i, c in enumerate(candidates)
        ])
        
        prompt = f"""Given a user query and template candidates, identify the best matching template.

User query: "{query}"

Candidates:
{candidates_text}

Return JSON:
{{
    "best_match_index": 0,
    "confidence": 0.95,
    "reasoning": "Why this template matches"
}}

Return ONLY valid JSON."""

        try:
            response = self.model.generate_content(prompt, request_options=self.request_options)
            result_text = response.text.strip()
            
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            return json.loads(result_text.strip())
        except Exception as e:
            logger.error(f"Template matching error: {e}")
            return {"best_match_index": 0, "confidence": 0.5, "reasoning": "Default selection"}
    
    def generate_questions(self, variables: List[Dict]) -> List[Dict]:
        vars_text = json.dumps(variables, indent=2)
        
        prompt = f"""Convert these technical variables into user-friendly questions.

Variables:
{vars_text}

Rules:
- NO technical jargon like "what is policy_number?"
- YES human-readable like "What is the insurance policy number on the schedule?"
- Use the description and example to create clear questions

Return JSON array of questions:
[
    {{
        "variable_key": "key",
        "question": "Clear, human-readable question?",
        "placeholder": "Example value from variable.example",
        "help_text": "Additional guidance from variable.description"
    }}
]

Return ONLY valid JSON array."""

        try:
            response = self.model.generate_content(prompt, request_options=self.request_options)
            result_text = response.text.strip()
            
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            return json.loads(result_text.strip())
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return [
                {
                    "variable_key": v["key"],
                    "question": v.get("label", v["key"]).replace("_", " ").title() + "?",
                    "placeholder": f"Enter {v['key']}",
                    "help_text": v.get("description", "")
                }
                for v in variables
            ]
    
    def prefill_variables(self, query: str, variables: List[Dict]) -> Dict[str, Any]:
        vars_text = json.dumps(variables, indent=2)
        
        prompt = f"""Extract any variable values mentioned in the user query.

Query: "{query}"

Variables:
{vars_text}

Return JSON with any values you can extract:
{{
    "variable_key": "extracted value",
    ...
}}

If no values can be extracted, return empty object {{}}.
Return ONLY valid JSON."""

        try:
            response = self.model.generate_content(prompt, request_options=self.request_options)
            result_text = response.text.strip()
            
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            return json.loads(result_text.strip())
        except Exception as e:
            logger.error(f"Prefill error: {e}")
            return {}

gemini_service = GeminiService()
