-- Database Schema for Legal Template Assistant
-- This schema is automatically created by SQLAlchemy on first run
-- This file is provided for reference only

-- Templates table: stores uploaded legal document templates
CREATE TABLE templates (
	id INTEGER NOT NULL PRIMARY KEY,
	template_id VARCHAR NOT NULL UNIQUE,
	title VARCHAR NOT NULL,
	description TEXT,
	doc_type VARCHAR,
	jurisdiction VARCHAR,
	file_path VARCHAR NOT NULL,
	original_file_path VARCHAR,
	embedding TEXT,  -- JSON array of embedding vectors
	tags TEXT,  -- Deprecated: use similarity_tags
	similarity_tags TEXT,  -- JSON array of tags
	body_md TEXT,  -- Template body in markdown
	created_at DATETIME,
	updated_at DATETIME
);

CREATE INDEX ix_templates_id ON templates (id);
CREATE INDEX ix_templates_doc_type ON templates (doc_type);
CREATE UNIQUE INDEX ix_templates_template_id ON templates (template_id);
CREATE INDEX ix_templates_jurisdiction ON templates (jurisdiction);

-- Variables table: stores template variables/fields
CREATE TABLE variables (
	id INTEGER NOT NULL PRIMARY KEY,
	template_id INTEGER NOT NULL,
	"key" VARCHAR NOT NULL,
	label VARCHAR NOT NULL,
	description TEXT,
	data_type VARCHAR DEFAULT 'text',
	example VARCHAR,  -- Example value for the variable
	validation_rules TEXT,  -- JSON validation rules
	is_required INTEGER DEFAULT 1,
	default_value VARCHAR,
	FOREIGN KEY(template_id) REFERENCES templates (id) ON DELETE CASCADE
);

CREATE INDEX idx_template_key ON variables (template_id, "key");
CREATE INDEX ix_variables_id ON variables (id);

-- Draft instances table: stores user-generated drafts
CREATE TABLE draft_instances (
	id INTEGER NOT NULL PRIMARY KEY,
	instance_id VARCHAR NOT NULL UNIQUE,
	template_id INTEGER NOT NULL,
	"query" TEXT,  -- Original user query
	answers TEXT,  -- JSON object with variable answers
	draft_md TEXT,  -- Generated draft in markdown
	draft_docx_path VARCHAR,  -- Path to exported DOCX
	status VARCHAR DEFAULT 'pending',
	created_at DATETIME,
	updated_at DATETIME,
	FOREIGN KEY(template_id) REFERENCES templates (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_draft_instances_instance_id ON draft_instances (instance_id);
CREATE INDEX ix_draft_instances_id ON draft_instances (id);
