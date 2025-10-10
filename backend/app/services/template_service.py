import os
import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models.template import Template, Variable
from .gemini_service import gemini_service
from .document_service import document_service
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TemplateService:
    @staticmethod
    def to_snake_case(text: str) -> str:
        """Convert text to snake_case."""
        import re
        # Replace spaces and hyphens with underscores
        text = text.replace(' ', '_').replace('-', '_')
        # Insert underscore before capitals and convert to lowercase
        text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
        # Remove any non-alphanumeric characters except underscores
        text = re.sub(r'[^a-z0-9_]', '', text.lower())
        # Remove duplicate underscores
        text = re.sub(r'_+', '_', text)
        # Remove leading/trailing underscores
        return text.strip('_')
    
    def process_uploaded_document(self, file_path: str, filename: str, db: Session) -> Dict[str, Any]:
        logger.info(f"Processing document: {filename}")
        
        if filename.lower().endswith('.docx'):
            logger.info("Extracting text from DOCX...")
            text = document_service.extract_text_from_docx(file_path)
        elif filename.lower().endswith('.pdf'):
            logger.info("Extracting text from PDF...")
            text = document_service.extract_text_from_pdf(file_path)
        else:
            raise ValueError("Unsupported file type")
        
        logger.info(f"Extracted {len(text)} characters")
        chunks = document_service.chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        logger.info(f"Split into {len(chunks)} chunks")
        
        all_variables = []
        doc_type = "unknown"
        jurisdiction = ""
        tags = []
        
        # Pro Tip Implementation: Process chunk 1 to build initial variable set,
        # then for chunk 2+, send chunk + previously discovered variables
        for i, chunk in enumerate(chunks):
            progress = int((i / len(chunks)) * 100)
            logger.info(f"📄 Processing chunk {i+1}/{len(chunks)} ({progress}%)...")
            # Pass existing variables to avoid duplicates
            existing_vars = all_variables if i > 0 else None
            result = gemini_service.extract_variables(chunk, existing_vars)
            
            # Add new variables, ensuring snake_case keys
            for var in result.get("variables", []):
                # Ensure key is snake_case
                original_key = var.get("key", "")
                var["key"] = self.to_snake_case(original_key)
                
                # Only add if not already present (deduplication)
                if not any(v["key"] == var["key"] for v in all_variables):
                    all_variables.append(var)
            
            # Get metadata from first chunk
            if i == 0:
                doc_type = result.get("doc_type", "unknown")
                jurisdiction = result.get("jurisdiction", "")
                tags = result.get("tags", [])
        
        title = os.path.splitext(filename)[0].replace("_", " ").title()
        template_id = str(uuid.uuid4())
        description = f"Template generated from {filename}"
        
        # Create markdown with new format
        markdown_content = document_service.create_markdown_template(
            title=title,
            content=text,
            variables=all_variables,
            doc_type=doc_type,
            jurisdiction=jurisdiction,
            tags=tags,
            template_id=template_id,
            description=description
        )
        
        template_file_path = os.path.join(settings.TEMPLATES_DIR, f"{template_id}.md")
        os.makedirs(settings.TEMPLATES_DIR, exist_ok=True)
        
        with open(template_file_path, 'w') as f:
            f.write(markdown_content)
        
        logger.info("Generating embedding...")
        embedding = gemini_service.generate_embedding(text[:1000])
        logger.info("✓ Embedding generated")
        
        import json
        template = Template(
            template_id=template_id,
            title=title,
            description=description,
            doc_type=doc_type,
            jurisdiction=jurisdiction,
            file_path=template_file_path,
            original_file_path=file_path,
            tags=json.dumps(tags),  # Deprecated
            similarity_tags=json.dumps(tags),
            body_md=text
        )
        template.set_embedding_vector(embedding)
        
        db.add(template)
        db.flush()
        
        for var_data in all_variables:
            variable = Variable(
                template_id=template.id,
                key=var_data["key"],
                label=var_data.get("label", var_data["key"].replace('_', ' ').title()),
                description=var_data.get("description", ""),
                example=var_data.get("example", ""),
                data_type=var_data.get("data_type", "text"),
                is_required=1 if var_data.get("is_required", True) else 0
            )
            db.add(variable)
        
        db.commit()
        db.refresh(template)
        
        return {
            "template_id": template.template_id,
            "title": template.title,
            "doc_type": template.doc_type,
            "jurisdiction": template.jurisdiction,
            "variables": all_variables,
            "variable_count": len(all_variables)
        }
    
    def get_template(self, template_id: str, db: Session) -> Template:
        template = db.query(Template).filter(Template.template_id == template_id).first()
        if not template:
            raise ValueError(f"Template {template_id} not found")
        return template
    
    def list_templates(self, db: Session, skip: int = 0, limit: int = 100) -> List[Template]:
        return db.query(Template).offset(skip).limit(limit).all()

template_service = TemplateService()
