import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ..models.template import Template, DraftInstance
from .gemini_service import gemini_service
from .document_service import document_service
from .exa_service import exa_service
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DraftService:
    def match_template(
        self, 
        query: str, 
        db: Session, 
        include_web_search: bool = True
    ) -> Dict[str, Any]:
        query_embedding = gemini_service.generate_embedding(query)
        
        templates = db.query(Template).all()
        
        result = {
            "best_match": None,
            "confidence": 0.0,
            "reasoning": "",
            "alternatives": [],
            "web_results": [],
            "message": ""
        }
        
        if not templates:
            result["message"] = "No templates available in library"
            if include_web_search and settings.EXA_API_KEY:
                logger.info("No local templates, searching web with Exa...")
                result["web_results"] = exa_service.search_legal_templates(query)
                if result["web_results"]:
                    result["message"] = "No local templates found. Showing web search results."
            return result
        
        similarities = []
        for template in templates:
            template_embedding = template.get_embedding_vector()
            if template_embedding:
                similarity = cosine_similarity(
                    [query_embedding],
                    [template_embedding]
                )[0][0]
                similarities.append({
                    "template": template,
                    "similarity": float(similarity)
                })
        
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_candidates = similarities[:5]
        
        candidate_dicts = [
            {
                "title": c["template"].title,
                "doc_type": c["template"].doc_type,
                "description": c["template"].description,
                "similarity": c["similarity"]
            }
            for c in top_candidates
        ]
        
        llm_result = gemini_service.match_templates(query, candidate_dicts)
        
        best_index = llm_result.get("best_match_index") or 0
        best_match = top_candidates[best_index]["template"] if (top_candidates and best_index is not None) else None
        confidence = llm_result.get("confidence") or 0.5
        
        result.update({
            "best_match": best_match.to_dict() if best_match else None,
            "confidence": confidence,
            "reasoning": llm_result.get("reasoning", ""),
            "alternatives": [
                {
                    **c["template"].to_dict(),
                    "similarity_score": c["similarity"]
                }
                for c in top_candidates[1:4]
            ]
        })
        
        if include_web_search and confidence < settings.MIN_CONFIDENCE_THRESHOLD:
            if settings.EXA_API_KEY:
                logger.info(f"Low confidence ({confidence:.2f}), searching web with Exa...")
                web_results = exa_service.search_legal_templates(
                    query,
                    doc_type=best_match.doc_type if best_match else None
                )
                result["web_results"] = web_results
                if web_results:
                    result["message"] = f"Low confidence match ({confidence:.0%}). Also showing web search results."
            else:
                logger.warning("Low confidence but EXA_API_KEY not configured")
        
        return result
    
    def create_draft_instance(self, template_id: str, query: str, db: Session) -> Dict[str, Any]:
        template = db.query(Template).filter(Template.template_id == template_id).first()
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        instance_id = str(uuid.uuid4())
        
        variables = [v.to_dict() for v in template.variables]
        
        prefilled = gemini_service.prefill_variables(query, variables)
        
        instance = DraftInstance(
            instance_id=instance_id,
            template_id=template.id,
            query=query,
            status="pending"
        )
        instance.set_answers(prefilled)
        
        db.add(instance)
        db.commit()
        db.refresh(instance)
        
        questions = gemini_service.generate_questions(variables)
        
        return {
            "instance_id": instance_id,
            "template": template.to_dict(),
            "questions": questions,
            "prefilled_answers": prefilled
        }
    
    def update_answers(self, instance_id: str, answers: Dict[str, Any], db: Session) -> Dict[str, Any]:
        instance = db.query(DraftInstance).filter(DraftInstance.instance_id == instance_id).first()
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        instance.update_answers(answers)
        instance.status = "in_progress"
        db.commit()
        
        return {
            "instance_id": instance_id,
            "status": instance.status,
            "answers": instance.get_answers()
        }
    
    def generate_draft(self, instance_id: str, db: Session) -> Dict[str, Any]:
        instance = db.query(DraftInstance).filter(DraftInstance.instance_id == instance_id).first()
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        template = instance.template
        answers = instance.get_answers()
        
        with open(template.file_path, 'r') as f:
            template_content = f.read()
        
        draft_content = template_content
        for key, value in answers.items():
            draft_content = draft_content.replace(f"{{{{{key}}}}}", str(value))
        
        instance.draft_md = draft_content
        instance.status = "completed"
        
        docx_filename = f"{instance_id}.docx"
        docx_path = os.path.join(settings.UPLOAD_DIR, docx_filename)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        document_service.generate_docx_from_markdown(draft_content, docx_path)
        instance.draft_docx_path = docx_path
        
        db.commit()
        
        return {
            "instance_id": instance_id,
            "draft_md": draft_content,
            "draft_docx_path": docx_path,
            "status": "completed"
        }
    
    def get_instance(self, instance_id: str, db: Session) -> DraftInstance:
        instance = db.query(DraftInstance).filter(DraftInstance.instance_id == instance_id).first()
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        return instance

draft_service = DraftService()
