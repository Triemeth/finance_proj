import pandas as pd
import json
from collections import defaultdict
import re

def count_occurrences(word, sentence, case_sensitive=False):
    if pd.isna(word):
        return 0

    word = str(word).strip()

    if not word:
        return 0

    if case_sensitive:
        pattern = r'\b' + re.escape(word) + r'\b'
        return len(re.findall(pattern, sentence))
    else:
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        return len(re.findall(pattern, sentence.lower()))

if __name__ == "__main__":
    tickers = pd.read_csv("data/all_tickers.csv")
    
    with open('data/full_article_dump.json', 'r') as file:
        article_text = json.load(file)

    texts = [entry["text"] for entry in article_text]

    ticker_counts = defaultdict(int)

    for _, row in tickers.iterrows():
        symbol = row["Symbol"]
        company = row["Company"]

        if pd.isna(symbol) and pd.isna(company):
            continue

        total_count = 0

        for text in texts:
            if pd.notna(symbol):
                total_count += count_occurrences(symbol, text, case_sensitive=True)
            if pd.notna(company):
                total_count += count_occurrences(company, text, case_sensitive=False)

        ticker_key = str(symbol) if pd.notna(symbol) else str(company)
        ticker_counts[ticker_key] = total_count


    result_df = pd.DataFrame(list(ticker_counts.items()), columns=["Ticker", "Mentions"])
    result_df = result_df.sort_values("Mentions", ascending=False)

    print(result_df.head())
#py -3.12 sent_count_sum.py