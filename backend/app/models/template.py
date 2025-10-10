from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from ..core.database import Base

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    doc_type = Column(String, index=True)
    jurisdiction = Column(String, index=True)
    file_path = Column(String, nullable=False)
    original_file_path = Column(String)
    embedding = Column(Text)
    tags = Column(Text)  # Deprecated: use similarity_tags
    similarity_tags = Column(Text)  # JSON array
    body_md = Column(Text)  # Template body markdown
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    variables = relationship("Variable", back_populates="template", cascade="all, delete-orphan")
    instances = relationship("DraftInstance", back_populates="template", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "template_id": self.template_id,
            "title": self.title,
            "description": self.description,
            "doc_type": self.doc_type,
            "jurisdiction": self.jurisdiction,
            "file_path": self.file_path,
            "similarity_tags": json.loads(self.similarity_tags) if self.similarity_tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "variable_count": len(self.variables)
        }
    
    def get_embedding_vector(self):
        return json.loads(self.embedding) if self.embedding else None
    
    def set_embedding_vector(self, vector):
        self.embedding = json.dumps(vector)

class Variable(Base):
    __tablename__ = "variables"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    key = Column(String, nullable=False)
    label = Column(String, nullable=False)
    description = Column(Text)
    data_type = Column(String, default="text")
    example = Column(String)  # Example value for the variable
    validation_rules = Column(Text)
    is_required = Column(Integer, default=1)
    default_value = Column(String)
    
    template = relationship("Template", back_populates="variables")
    
    __table_args__ = (
        Index('idx_template_key', 'template_id', 'key'),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "label": self.label,
            "description": self.description,
            "data_type": self.data_type,
            "example": self.example,
            "validation_rules": json.loads(self.validation_rules) if self.validation_rules else None,
            "is_required": bool(self.is_required),
            "default_value": self.default_value
        }

class DraftInstance(Base):
    __tablename__ = "draft_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String, unique=True, index=True, nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    query = Column(Text)
    answers = Column(Text)
    draft_md = Column(Text)
    draft_docx_path = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    template = relationship("Template", back_populates="instances")
    
    def to_dict(self):
        return {
            "id": self.id,
            "instance_id": self.instance_id,
            "template_id": self.template.template_id if self.template else None,
            "query": self.query,
            "answers": json.loads(self.answers) if self.answers else {},
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "has_draft": bool(self.draft_md)
        }
    
    def get_answers(self):
        return json.loads(self.answers) if self.answers else {}
    
    def set_answers(self, answers_dict):
        self.answers = json.dumps(answers_dict)
    
    def update_answers(self, new_answers):
        current = self.get_answers()
        current.update(new_answers)
        self.set_answers(current)
