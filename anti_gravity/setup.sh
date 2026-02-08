#!/bin/bash
# =============================================================================
# Anti-Gravity Setup Script
# Installs all Python dependencies for the autonomous affiliate marketing engine
# =============================================================================

set -e

echo "============================================"
echo "  Anti-Gravity: Setup"
echo "============================================"
echo ""

# Check Python version
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using: $($PYTHON_CMD --version)"
echo ""

# Install dependencies
echo "Installing dependencies..."
$PYTHON_CMD -m pip install \
    requests \
    google-generativeai \
    sqlalchemy \
    python-dotenv \
    pydantic-settings \
    backoff

echo ""
echo "============================================"
echo "  Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and fill in your API keys"
echo "  2. Test keyword discovery:"
echo "     $PYTHON_CMD -m anti_gravity.main discover --niche 'home office furniture'"
echo "  3. Dry-run an article:"
echo "     $PYTHON_CMD -m anti_gravity.main write --keyword 'best standing desks' --dry-run"
echo "  4. Full pipeline:"
echo "     $PYTHON_CMD -m anti_gravity.main run --niche 'AI writing tools' --count 3"
echo ""
