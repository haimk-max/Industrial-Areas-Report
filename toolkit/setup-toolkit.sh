#!/bin/bash
# setup-toolkit.sh — One-step Toolkit installation for team members

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Industrial Areas Toolkit Setup${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Check Python version
echo -e "${YELLOW}[1/5]${NC} Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "   Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Step 2: Check pip
echo -e "${YELLOW}[2/5]${NC} Checking pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}❌ pip not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} pip is installed"

# Step 3: Install signalkit (pylib)
echo -e "${YELLOW}[3/5]${NC} Installing signalkit library..."
if [ ! -d "./toolkit/pylib" ]; then
    echo -e "${RED}❌ Error: toolkit/pylib/ not found${NC}"
    echo "   Are you in the right directory? (should contain toolkit/)"
    exit 1
fi

if pip install -e ./toolkit/pylib > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} signalkit installed successfully"
else
    echo -e "${RED}❌ Failed to install signalkit${NC}"
    echo "   Try: pip install -e ./toolkit/pylib"
    exit 1
fi

# Step 4: Install Claude Code Skills
echo -e "${YELLOW}[4/5]${NC} Installing Claude Code Skills..."
SKILLS_DIR="$HOME/.claude/skills"

if [ ! -d "$SKILLS_DIR" ]; then
    echo "   Creating $SKILLS_DIR..."
    mkdir -p "$SKILLS_DIR"
fi

SKILLS=("severity-calculator" "trend-detective" "agent-rag")
for skill in "${SKILLS[@]}"; do
    if [ -d "./toolkit/skills/$skill" ]; then
        cp -r "./toolkit/skills/$skill" "$SKILLS_DIR/" 2>/dev/null && \
            echo -e "${GREEN}✓${NC} $skill installed" || \
            echo -e "${YELLOW}⚠${NC} $skill (already exists, skipped)"
    else
        echo -e "${YELLOW}⚠${NC} $skill not found (skipped)"
    fi
done

# Step 5: Verify installation
echo -e "${YELLOW}[5/5]${NC} Verifying installation..."
if python3 -c "from signalkit import calculate_bucket, calculate_mann_kendall; print('OK')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Python library verified"
else
    echo -e "${RED}❌ Python library verification failed${NC}"
    exit 1
fi

if [ -f "$SKILLS_DIR/severity-calculator/SKILL.md" ]; then
    echo -e "${GREEN}✓${NC} Skills directory verified"
else
    echo -e "${RED}❌ Skills directory verification failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Read the toolkit README:"
echo -e "     ${YELLOW}cat toolkit/README.md${NC}"
echo -e ""
echo -e "  2. Try a skill in Claude Code:"
echo -e "     ${YELLOW}/<severity-calculator> --c_max 101 --dws 10${NC}"
echo -e ""
echo -e "  3. Use Python library:"
echo -e "     ${YELLOW}python3 -c \"from signalkit import calculate_bucket; print(calculate_bucket(101, 10))\"${NC}"
echo -e ""
echo -e "For troubleshooting, see: ${YELLOW}toolkit/INSTALLATION.md${NC}"
echo ""
