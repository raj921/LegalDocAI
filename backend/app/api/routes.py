from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os
import shutil
from ..core.database import get_db
from ..services.template_service import template_service
from ..services.draft_service import draft_service
from ..services.document_service import document_service
from ..core.config import get_settings

settings = get_settings()
router = APIRouter()

class TemplateMatchRequest(BaseModel):
    query: str
    include_web_search: bool = True

class DraftInstanceRequest(BaseModel):
    template_id: str
    query: str

class UpdateAnswersRequest(BaseModel):
    instance_id: str
    answers: dict

class GenerateDraftRequest(BaseModel):
    instance_id: str

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "legal-template-assistant"}

@router.post("/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import logging
    logger = logging.getLogger(__name__)
    
    if not file.filename.endswith(('.docx', '.pdf')):
        raise HTTPException(status_code=400, detail="Only DOCX and PDF files are supported")
    
    # Check file size (10MB limit)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    logger.info(f"Uploading: {file.filename} ({file_size / 1024:.1f} KB)")
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info("File saved. Starting AI processing...")
    
    try:
        result = template_service.process_uploaded_document(file_path, file.filename, db)
        logger.info(f"✓ Template created: {result.get('template_id')}")
        return {
            "success": True,
            "message": "Template created successfully",
            **result
        }
    except Exception as e:
        logger.error(f"Error processing template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/templates")
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    templates = template_service.list_templates(db, skip, limit)
    return {
        "templates": [t.to_dict() for t in templates],
        "count": len(templates)
    }

@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    try:
        template = template_service.get_template(template_id, db)
        return {
            **template.to_dict(),
            "variables": [v.to_dict() for v in template.variables]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/templates/{template_id}/variables/csv")
async def export_template_variables_csv(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Export template variables to CSV format."""
    try:
        template = template_service.get_template(template_id, db)
        variables = [v.to_dict() for v in template.variables]
        
        csv_content = document_service.export_variables_to_csv(variables)
        
        filename = f"{template.title.replace(' ', '_')}_variables.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}/export")
async def export_template_markdown(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Export the template markdown file."""
    try:
        template = template_service.get_template(template_id, db)
        
        with open(template.file_path, 'r') as f:
            markdown_content = f.read()
        
        filename = f"{template.title.replace(' ', '_')}.md"
        
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft/match")
async def match_template(
    request: TemplateMatchRequest,
    db: Session = Depends(get_db)
):
    result = draft_service.match_template(
        request.query, 
        db, 
        include_web_search=request.include_web_search
    )
    return result

@router.post("/draft/instance")
async def create_draft_instance(
    request: DraftInstanceRequest,
    db: Session = Depends(get_db)
):
    try:
        result = draft_service.create_draft_instance(request.template_id, request.query, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/draft/answers")
async def update_draft_answers(
    request: UpdateAnswersRequest,
    db: Session = Depends(get_db)
):
    try:
        result = draft_service.update_answers(request.instance_id, request.answers, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/draft/generate")
async def generate_draft(
    request: GenerateDraftRequest,
    db: Session = Depends(get_db)
):
    try:
        result = draft_service.generate_draft(request.instance_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/draft/{instance_id}")
async def get_draft_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    try:
        instance = draft_service.get_instance(instance_id, db)
        return instance.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/draft/{instance_id}/export/markdown")
async def export_draft_markdown(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """Export the generated draft as markdown."""
    try:
        instance = draft_service.get_instance(instance_id, db)
        
        if not instance.draft_md:
            raise HTTPException(status_code=400, detail="Draft not yet generated")
        
        filename = f"draft_{instance_id}.md"
        
        return Response(
            content=instance.draft_md,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/draft/{instance_id}/export/docx")
async def export_draft_docx(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """Export the generated draft as DOCX."""
    try:
        instance = draft_service.get_instance(instance_id, db)
        
        if not instance.draft_docx_path or not os.path.exists(instance.draft_docx_path):
            raise HTTPException(status_code=400, detail="DOCX draft not available")
        
        with open(instance.draft_docx_path, 'rb') as f:
            docx_content = f.read()
        
        filename = f"draft_{instance_id}.docx"
        
        return Response(
            content=docx_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
