#!/bin/bash

set -euo pipefail

echo "Setting up environment..."
./setup_env.sh

echo "Validating flashcard JSON files..."
python3 utilities/src/validate_cards.py

echo "Exporting flashcards to CSV..."
python3 utilities/src/export_csv.py

echo "All tasks completed successfully!"

