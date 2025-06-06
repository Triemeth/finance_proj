import pandas as pd
import json

def count_occurrences(word, sentence):
    return sentence.lower().split().count(word)

if __name__ == "__main__":
    tickers = pd.read_csv("data/all_tickers.csv")
    
    with open('data/full_article_dump.json', 'r') as file:
        article_text = json.load(file)

    texts = [entry["text"] for entry in article_text]

    
#py -3.12 sent_count_sum.py