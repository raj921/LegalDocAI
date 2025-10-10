# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites Check ✓
Run the verification script:
```bash
./verify_setup.sh
```

All checks should pass ✓

---

## 📋 Setup Instructions

### Option 1: Quick Start (Already Setup)

Your project is ready! Just start the servers:

```bash
# Terminal 1: Start Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

---

### Option 2: Fresh Setup

If starting fresh or on a new machine:

#### 1. Backend Setup (2 minutes)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Edit `.env` and add your API key:**
```env
GEMINI_API_KEY=your_actual_key_here
```

**Run migration:**
```bash
python migrate_database.py
```

**Start server:**
```bash
python run.py
```

#### 2. Frontend Setup (1 minute)
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

---

## 🎯 Quick Test

### 1. Upload a Template

Visit http://localhost:3000/upload and upload a DOCX file, **OR** use curl:

```bash
curl -X POST http://localhost:8000/api/templates/upload \
  -F "file=@your_document.docx"
```

### 2. View Templates

Visit http://localhost:3000/templates

### 3. Create a Draft

Visit http://localhost:3000/draft and describe what you need

---

## 📖 What You Get

### Output Formats

1. **Rendered Markdown Draft**
   ```bash
   GET /api/draft/{id}/export/markdown
   ```

2. **Template File (YAML + Markdown)**
   ```bash
   GET /api/templates/{id}/export
   ```

3. **Variables CSV**
   ```bash
   GET /api/templates/{id}/variables/csv
   ```

4. **DOCX Document**
   ```bash
   GET /api/draft/{id}/export/docx
   ```

### Template Format

Your templates will have this structure:

```yaml
---
template_id: tpl_xxx
title: Document Title
File_description: What this template is for
jurisdiction: US
doc_type: contract
variables:
  - key: party_name          # Always snake_case
    label: Party Name
    description: Full legal name
    example: "Acme Corp"
    required: true
similarity_tags: ["contract", "business"]
---

This agreement with {{party_name}}...
```

---

## 🔥 Key Features

### 1. Smart Variable Extraction
- Automatically finds variables in documents
- Converts to **snake_case** (e.g., `party_name`)
- Deduplicates across long documents
- Includes example values

### 2. AI-Powered Matching
- Describe what you need in plain English
- System finds the best matching template
- Uses similarity tags and descriptions

### 3. Human-Readable Questions
- "What is the insurance policy number on the schedule?"
- NOT "What is policy_number?"

### 4. Multiple Export Formats
- Markdown (clean, editable)
- DOCX (ready to use)
- CSV (for spreadsheets)
- JSON (for integrations)

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `QUICKSTART.md` | **This file - start here!** |
| `TEMPLATE_FORMAT_SPEC.md` | Complete format specification |
| `FINAL_SUMMARY.md` | Full implementation details |
| `example_export_usage.sh` | API usage examples |

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check virtual environment
source venv/bin/activate

# Check API key is set
cat .env | grep GEMINI_API_KEY

# Check imports
python -c "from app.main import app; print('OK')"
```

### Frontend won't start
```bash
# Check dependencies
npm install

# Check configuration
cat .env.local
```

### Database issues
```bash
# Reset database
rm legal_templates.db
python migrate_database.py
```

### API not responding
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check logs
# Look at terminal where backend is running
```

---

## 🎓 Example Workflow

### Complete Example: Insurance Claim Notice

**1. Upload Template**
```bash
# Upload your insurance claim template
curl -X POST http://localhost:8000/api/templates/upload \
  -F "file=@claim_template.docx"

# Response:
# {
#   "template_id": "abc-123",
#   "title": "Insurance Claim Notice",
#   "variable_count": 4
# }
```

**2. Match to Query**
```bash
curl -X POST http://localhost:8000/api/draft/match \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I need to file an insurance claim for a car accident"
  }'

# Response:
# {
#   "best_match": { "template_id": "abc-123", ... },
#   "confidence": 0.92
# }
```

**3. Create Draft**
```bash
curl -X POST http://localhost:8000/api/draft/instance \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "abc-123",
    "query": "Car accident on Highway 101"
  }'

# Response:
# {
#   "instance_id": "def-456",
#   "questions": [
#     {
#       "variable_key": "claimant_name",
#       "question": "What is your full legal name?",
#       "placeholder": "John Doe"
#     }
#   ]
# }
```

**4. Fill Variables**
```bash
curl -X POST http://localhost:8000/api/draft/answers \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "def-456",
    "answers": {
      "claimant_name": "John Smith",
      "incident_date": "2025-01-15",
      "policy_number": "POL-12345"
    }
  }'
```

**5. Generate & Download**
```bash
# Generate
curl -X POST http://localhost:8000/api/draft/generate \
  -H "Content-Type: application/json" \
  -d '{"instance_id": "def-456"}'

# Download as DOCX
curl http://localhost:8000/api/draft/def-456/export/docx \
  -o my_claim.docx

# Open the document
open my_claim.docx  # macOS
# or: xdg-open my_claim.docx  # Linux
# or: start my_claim.docx  # Windows
```

**Done!** You have a completed legal document ready to use.

---

## ⚡ Pro Tips

### 1. Chunking Long Documents
Documents longer than 2000 characters are automatically chunked. The system:
- Extracts variables from chunk 1
- Passes those to chunk 2+ to avoid duplicates
- Results in cleaner, deduplicated variable lists

### 2. Variable Naming
All variables are automatically converted to snake_case:
- `ClaimantName` → `claimant_name`
- `Policy Number` → `policy_number`
- This ensures consistency across templates

### 3. Example Values
Always provide example values when creating templates:
```yaml
example: "Boy Kumar"  # Good
example: ""           # Not helpful
```

### 4. Similarity Tags
Use relevant tags for better matching:
```yaml
similarity_tags: ["insurance", "motor", "claim", "india"]
```

### 5. Question Quality
The system generates human-readable questions using:
- Variable label
- Description
- Example value

---

## 📞 Quick Reference

### Start Servers
```bash
# Backend
cd backend && source venv/bin/activate && python run.py

# Frontend
cd frontend && npm run dev
```

### Useful URLs
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### Key Directories
- Templates: `backend/templates_storage/`
- Uploads: `backend/uploads/`
- Database: `backend/legal_templates.db`

---

## ✅ Checklist

- [ ] Backend virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with GEMINI_API_KEY
- [ ] Database migrated (`python migrate_database.py`)
- [ ] Backend running (port 8000)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend running (port 3000)
- [ ] Can access frontend at localhost:3000
- [ ] Can access API docs at localhost:8000/docs

---

## 🎉 You're All Set!

The Legal Template Assistant is now ready to:
- ✅ Extract variables from legal documents
- ✅ Generate templates with proper formatting
- ✅ Match queries to best templates
- ✅ Create drafts with AI-powered questions
- ✅ Export in multiple formats

**Need Help?** Check `FINAL_SUMMARY.md` for detailed documentation.

**Happy Document Generating! 🚀**
