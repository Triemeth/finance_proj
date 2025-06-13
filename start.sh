#!/bin/bash
set -e

echo "Running spy_dia_qqq_comp.py..."
python scripts/spy_dia_qqq_comp.py

echo "Running scrape.py..."
python scripts/scrape.py

echo "Running scrape.py..."
python scripts/sent_count_sum.py

echo "All scripts completed successfully."
