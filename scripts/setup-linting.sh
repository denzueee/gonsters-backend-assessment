#!/bin/bash

# Auto-Linting Setup Script
# This script installs and configures auto-linting for Python and JavaScript/React

set -e

echo "🔧 Setting up Auto-Linting for GONSTERS Project..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Install Python linting tools
echo -e "${BLUE}📦 Installing Python linting tools...${NC}"
pip install black flake8 isort bandit pre-commit

# Install pre-commit hooks
echo -e "${BLUE}🪝 Installing pre-commit hooks...${NC}"
pre-commit install
pre-commit install --hook-type pre-push

# Install Node.js dependencies for frontend
if [ -d "app/ui" ]; then
    echo -e "${BLUE}📦 Installing Node.js linting tools...${NC}"
    cd app/ui
    npm install --save-dev eslint eslint-plugin-react eslint-plugin-react-hooks prettier
    cd ../..
fi

# Run initial linting
echo -e "${BLUE}🧹 Running initial auto-fix on all files...${NC}"
echo -e "${YELLOW}⚠️  This may take a moment...${NC}"

# Format Python files
echo -e "${BLUE}  → Formatting Python files with Black...${NC}"
black . --exclude '(migrations|venv|\.venv|htmlcov|app/ui)' || true

echo -e "${BLUE}  → Sorting Python imports with isort...${NC}"
isort . --skip migrations --skip venv --skip .venv --skip htmlcov --skip app/ui || true

echo -e "${BLUE}  → Linting Python with flake8...${NC}"
flake8 . --exclude=migrations,venv,.venv,htmlcov,app/ui --max-line-length=120 || true

# Format JavaScript/React files
if [ -d "app/ui/src" ]; then
    echo -e "${BLUE}  → Formatting React files with Prettier...${NC}"
    cd app/ui
    npx prettier --write "src/**/*.{js,jsx,json,css,md}" || true
    cd ../..
fi

echo ""
echo -e "${GREEN}✅ Auto-linting setup complete!${NC}"
echo ""
echo -e "${GREEN}📋 Available commands:${NC}"
echo -e "  ${BLUE}Python:${NC}"
echo -e "    black .              # Format Python code"
echo -e "    isort .              # Sort Python imports"
echo -e "    flake8 .             # Lint Python code"
echo -e "    bandit -r app        # Security check"
echo ""
echo -e "  ${BLUE}React:${NC}"
echo -e "    cd app/ui && npm run lint    # Lint React code"
echo -e "    cd app/ui && npm run format  # Format React code"
echo ""
echo -e "  ${BLUE}Pre-commit:${NC}"
echo -e "    pre-commit run --all-files   # Run all checks manually"
echo ""
echo -e "${GREEN}🎉 Git hooks are now active!${NC}"
echo -e "   Auto-linting will run automatically on git push"
echo ""
