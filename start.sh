#!/bin/bash
set -e

python scripts/spy_dia_qqq_comp.py

echo "Waiting for data flush..."
sleep 5

echo "Running scrape.py to get articles..."
python scripts/scrape.py

echo "Waiting for data flush"
sleep 5

echo "Running sent_count_sum.py to compute sentiment"
python scripts/sent_count_sum.py

echo "Waiting for data flush"
sleep 5

echo "Running quant_stuff.py to compute ratios and what not"
python scripts/quant_stuff.py

echo "All scripts completed successfully."

