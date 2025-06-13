#!/bin/bash
set -e

echo "Running spy_dia_qqq_comp.py..."
python spy_dia_qqq_comp.py

echo "Running scrape.py..."
python scrape.py

echo "All scripts completed successfully."
