#!/bin/bash
# Verification script for Legal Template Assistant

echo "============================================================"
echo "Legal Template Assistant - Setup Verification"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_mark="${GREEN}✓${NC}"
cross_mark="${RED}✗${NC}"
info_mark="${YELLOW}ℹ${NC}"

# Check backend
echo "Backend Checks:"
echo "---------------"

# Python
if command -v python3 &> /dev/null; then
    echo -e "${check_mark} Python 3 installed: $(python3 --version)"
else
    echo -e "${cross_mark} Python 3 not found"
fi

# Virtual environment
if [ -d "backend/venv" ]; then
    echo -e "${check_mark} Virtual environment exists"
else
    echo -e "${cross_mark} Virtual environment not found"
fi

# Dependencies
if [ -f "backend/requirements.txt" ]; then
    echo -e "${check_mark} requirements.txt found"
else
    echo -e "${cross_mark} requirements.txt not found"
fi

# .env file
if [ -f "backend/.env" ]; then
    echo -e "${check_mark} Backend .env file exists"
else
    echo -e "${info_mark} Backend .env file not found (copy from .env.example)"
fi

# Database
if [ -f "backend/legal_templates.db" ]; then
    echo -e "${check_mark} Database exists"
else
    echo -e "${info_mark} Database will be created on first run"
fi

# Key files
echo ""
echo "Backend Files:"
for file in "app/main.py" "app/api/routes.py" "app/core/database.py" "app/services/document_service.py" "app/services/template_service.py" "app/services/gemini_service.py" "app/models/template.py" "migrate_database.py" "run.py"; do
    if [ -f "backend/$file" ]; then
        echo -e "  ${check_mark} $file"
    else
        echo -e "  ${cross_mark} $file missing"
    fi
done

# Frontend
echo ""
echo "Frontend Checks:"
echo "----------------"

# Node.js
if command -v node &> /dev/null; then
    echo -e "${check_mark} Node.js installed: $(node --version)"
else
    echo -e "${cross_mark} Node.js not found"
fi

# npm
if command -v npm &> /dev/null; then
    echo -e "${check_mark} npm installed: $(npm --version)"
else
    echo -e "${cross_mark} npm not found"
fi

# node_modules
if [ -d "frontend/node_modules" ]; then
    echo -e "${check_mark} Dependencies installed"
else
    echo -e "${cross_mark} Run 'npm install' in frontend directory"
fi

# .env.local
if [ -f "frontend/.env.local" ]; then
    echo -e "${check_mark} Frontend .env.local exists"
else
    echo -e "${info_mark} Frontend .env.local not found (copy from .env.local.example)"
fi

# Key files
echo ""
echo "Frontend Files:"
for file in "app/page.tsx" "app/layout.tsx" "package.json"; do
    if [ -f "frontend/$file" ]; then
        echo -e "  ${check_mark} $file"
    else
        echo -e "  ${cross_mark} $file missing"
    fi
done

# Documentation
echo ""
echo "Documentation:"
echo "--------------"
for file in "README.md" "TEMPLATE_FORMAT_SPEC.md" "IMPLEMENTATION_SUMMARY.md" "IMPLEMENTATION_UPDATE_V2.md" "FINAL_SUMMARY.md"; do
    if [ -f "$file" ]; then
        echo -e "  ${check_mark} $file"
    else
        echo -e "  ${cross_mark} $file missing"
    fi
done

# Test Python syntax
echo ""
echo "Python Syntax Check:"
echo "--------------------"
if [ -d "backend/venv" ]; then
    cd backend
    source venv/bin/activate 2>/dev/null
    if python3 -c "from app.main import app; print('OK')" 2>/dev/null; then
        echo -e "${check_mark} Backend code imports successfully"
    else
        echo -e "${cross_mark} Backend import errors"
    fi
    cd ..
else
    echo -e "${info_mark} Skipped (no venv)"
fi

echo ""
echo "============================================================"
echo "Next Steps:"
echo "============================================================"
echo ""
echo "1. Backend Setup:"
echo "   cd backend"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   cp .env.example .env  # Add your GEMINI_API_KEY"
echo "   python migrate_database.py"
echo "   python run.py"
echo ""
echo "2. Frontend Setup (in new terminal):"
echo "   cd frontend"
echo "   npm install"
echo "   cp .env.local.example .env.local"
echo "   npm run dev"
echo ""
echo "3. Access:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "============================================================"
