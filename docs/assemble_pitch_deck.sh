#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cat deck_b64/part_* | base64 -d > MergeMate_Pitch_Deck.pptx
echo "Wrote $(pwd)/MergeMate_Pitch_Deck.pptx ($(wc -c < MergeMate_Pitch_Deck.pptx) bytes)"
