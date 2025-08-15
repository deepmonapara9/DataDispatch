#!/bin/bash
# Quick Newsletter Generator
# Simple wrapper script for easy newsletter generation

echo "🚀 Generating fresh newsletter content..."

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Generate and update newsletter
python auto_update_newsletter.py --open

echo "✅ Done! Check your sample_newsletter.html file"
