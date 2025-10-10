# Legal Template Format Specification

## Overview

Templates are stored as Markdown files with YAML front-matter, following a structured format that enables AI-powered document generation with variable substitution.

## Template Structure

### YAML Front-Matter

```yaml
---
template_id: tpl_incident_notice_v1
title: Incident Notice to Insurer
File_description: Description of the file to help with case matching
jurisdiction: IN
doc_type: legal_notice
variables:
  - key: claimant_full_name
    label: Claimant's full name
    description: Person/entity raising the claim.
    example: "Boy Kumar"
    required: true
  - key: incident_date
    label: Date of incident
    description: The date the insured event occurred (ISO 8601).
    example: "2025-07-12"
    required: true
  - key: policy_number
    label: Policy number
    description: Insurance policy reference as printed on schedule.
    example: "302786965"
    required: true
  - key: demand_amount_inr
    label: Demand amount (INR)
    description: Total principal claim excluding interest/fees.
    example: "450000"
    required: false
similarity_tags: ["insurance", "notice", "india", "motor", "health"]
---
```

### Template Body

After the front-matter, the template body uses double-brace syntax for variable placeholders:

```markdown
Dear Sir/Madam,

On {{incident_date}}, {{claimant_full_name}} hereby notifies you under Policy {{policy_number}}...

We demand payment of INR {{demand_amount_inr}} within 15 days...

Yours sincerely,
{{claimant_full_name}}
```

## Field Specifications

### Front-Matter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_id` | string | Yes | Unique identifier for the template (UUID or custom ID) |
| `title` | string | Yes | Human-readable template title |
| `File_description` | string | Yes | Description to help with template matching and discovery |
| `jurisdiction` | string | No | Legal jurisdiction (e.g., "IN", "US", "CA") |
| `doc_type` | string | Yes | Document type classification (e.g., "legal_notice", "contract", "agreement") |
| `variables` | array | Yes | List of variable definitions (see Variable Schema below) |
| `similarity_tags` | array | Yes | Tags for semantic search and categorization |

### Variable Schema

Each variable in the `variables` array must have:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | Yes | Variable identifier in **snake_case** format |
| `label` | string | Yes | Human-friendly display name |
| `description` | string | Yes | Detailed explanation of what the variable represents |
| `example` | string | Yes | Sample value to guide users |
| `required` | boolean | Yes | Whether the variable must be filled |

### Variable Key Naming Rules

**IMPORTANT**: All variable keys MUST follow snake_case convention:
- Lowercase letters only
- Words separated by underscores
- No special characters except underscores
- No leading or trailing underscores

✅ **Correct Examples:**
- `claimant_full_name`
- `incident_date`
- `policy_number`
- `demand_amount_inr`

❌ **Incorrect Examples:**
- `ClaimantFullName` (CamelCase)
- `claimant-full-name` (kebab-case)
- `claimant full name` (spaces)
- `claimant.full.name` (dots)

The system will automatically convert non-snake_case keys to snake_case.

## Variable Substitution

In the template body, variables are referenced using double-brace syntax:

```
{{variable_key}}
```

When a draft is generated, these placeholders are replaced with actual values provided by the user.

## Document Processing Pro Tips

### Chunking Long Documents

For documents exceeding the AI model's context window:

1. **Chunk 1 (Initial)**: Process first chunk to extract initial variable set
2. **Chunk 2+**: Pass both the chunk AND previously discovered variables
3. **Benefit**: AI reuses existing variable keys, preventing duplicates

Implementation:
```python
all_variables = []
for i, chunk in enumerate(chunks):
    # Pass existing vars to avoid duplicates
    existing_vars = all_variables if i > 0 else None
    result = gemini_service.extract_variables(chunk, existing_vars)
    
    # Merge new variables (deduplicated)
    for var in result.get("variables", []):
        if not any(v["key"] == var["key"] for v in all_variables):
            all_variables.append(var)
```

### Variable Extraction Guidelines

**DO extract variables for:**
- Names (parties, witnesses, entities)
- Dates (effective dates, deadlines, incidents)
- Amounts (monetary values, quantities)
- Addresses (physical and email)
- Reference numbers (policy, case, file numbers)
- Custom fields specific to document type

**DO NOT extract variables for:**
- Statutory text or legal citations
- Standard legal language
- Section headings
- Boilerplate clauses

## Question Generation

When collecting values from users, generate human-readable questions:

❌ **Bad**: "What is policy_number?"
✅ **Good**: "What is the insurance policy number on the schedule?"

Use the `description` and `example` fields to create clear, contextual questions.

## CSV Export Format

Variables can be exported to CSV with these columns:

```csv
key,label,description,example,data_type,is_required,default_value
claimant_full_name,Claimant's full name,Person/entity raising the claim.,Boy Kumar,text,True,
incident_date,Date of incident,The date the insured event occurred (ISO 8601).,2025-07-12,date,True,
```

## API Integration

### Creating Templates
`POST /api/templates/upload` - Upload DOCX/PDF, automatically extracts variables

### Exporting Templates
- `GET /api/templates/{id}/export` - Download as Markdown
- `GET /api/templates/{id}/variables/csv` - Download variables as CSV

### Generating Drafts
1. `POST /api/draft/match` - Find best matching template
2. `POST /api/draft/instance` - Create draft instance
3. `POST /api/draft/answers` - Fill in variable values
4. `POST /api/draft/generate` - Generate final document

### Exporting Drafts
- `GET /api/draft/{id}/export/markdown` - Download as Markdown
- `GET /api/draft/{id}/export/docx` - Download as Word document

## Best Practices

1. **Consistent Naming**: Always use snake_case for variable keys
2. **Clear Labels**: Make labels self-explanatory for end users
3. **Helpful Examples**: Provide realistic example values
4. **Good Descriptions**: Explain what each variable represents and where to find it
5. **Appropriate Tags**: Use similarity_tags for better template matching
6. **Jurisdictions**: Always specify jurisdiction when applicable
7. **Required vs Optional**: Mark variables as required only when truly necessary

## Database Schema

### Templates Table
- `template_id` (unique, indexed)
- `title`
- `description` (File_description)
- `doc_type` (indexed)
- `jurisdiction` (indexed)
- `similarity_tags` (JSON)
- `body_md` (full markdown content)
- `embedding` (vector for semantic search)
- `file_path` (path to .md file)

### Variables Table
- `template_id` (foreign key)
- `key` (snake_case, indexed)
- `label`
- `description`
- `example`
- `data_type`
- `is_required`
- `default_value`

### Draft Instances Table
- `instance_id` (unique)
- `template_id` (foreign key)
- `query` (user's original request)
- `answers` (JSON of variable values)
- `draft_md` (generated markdown)
- `draft_docx_path` (path to generated DOCX)
- `status` (pending/in_progress/completed)

## Example Template

See `/backend/test_new_format.py` for a complete working example of the incident notice template.
