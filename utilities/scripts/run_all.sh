#!/bin/bash

set -euo pipefail

rm -rf ./data/*

echo "Setting up environment..."
./utilities/scripts/setup_env.sh

echo "Validating flashcard JSON files..."
python3 utilities/src/validate_cards.py

echo "Exporting flashcards to CSV..."
python3 utilities/src/export_csv.py

echo "All tasks completed successfully!"

