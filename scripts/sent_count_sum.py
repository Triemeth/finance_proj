import pandas as pd
import json
from collections import defaultdict
import re
import nltk
import psycopg2
from sqlalchemy import create_engine
from datetime import date

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

def count_occurrences(word, sentence, case_sensitive=False):
    if pd.isna(word):
        return 0
    word = str(word).strip()
    if not word:
        return 0

    pattern = r'\b' + re.escape(word) + r'\b'
    if not case_sensitive:
        return len(re.findall(pattern, sentence.lower()))
    return len(re.findall(pattern, sentence))

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]

    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    return ' '.join(lemmatized_tokens)

def get_sentiment(text):
    scores = analyzer.polarity_scores(text)
    return 1 if scores['pos'] > 0 else 0

if __name__ == "__main__":
    engine = create_engine("postgresql+psycopg2://postgres:postgres@db:5432/financedb")
    conn = engine.connect()

    tickers = pd.read_sql("SELECT * FROM all_tickers", conn)
    articles_df = pd.read_sql("SELECT * FROM full_articles", conn)
    texts = articles_df["article_text"].tolist()

    ticker_counts = defaultdict(int)
    ticker_sentiments = defaultdict(list)

    analyzer = SentimentIntensityAnalyzer()

    for _, row in tickers.iterrows():
        symbol = row["Symbol"]
        company = row["Company"]
        if pd.isna(symbol) and pd.isna(company):
            continue

        ticker_key = str(symbol) if pd.notna(symbol) else str(company)
        mention_count = 0

        for text in texts:
            for sentence in sent_tokenize(text):
                mentioned = False

                if pd.notna(symbol) and count_occurrences(symbol, sentence, case_sensitive=True) > 0:
                    mentioned = True
                if pd.notna(company) and count_occurrences(company, sentence, case_sensitive=False) > 0:
                    mentioned = True

                if mentioned:
                    mention_count += 1
                    sentiment = get_sentiment(preprocess_text(sentence))
                    ticker_sentiments[ticker_key].append(sentiment)

        ticker_counts[ticker_key] = mention_count

    sentiment_avg = {
        ticker: sum(sentiments) / len(sentiments) if sentiments else 0.0
        for ticker, sentiments in ticker_sentiments.items()
    }

    result_df = pd.DataFrame({
        "ticker": list(ticker_counts.keys()),
        "mentions": list(ticker_counts.values()),
        "avg_sentiment": [sentiment_avg.get(t, 0.0) for t in ticker_counts.keys()],
    })

    result_df.to_sql("sentiment_day", conn, if_exists="replace", index=False)

    try:
        existing_df = pd.read_sql("SELECT * FROM sentiment_all_time", conn)

        for col in ["ticker", "mentions", "avg_sentiment"]:
            if col not in existing_df.columns:
                existing_df[col] = 0
        for col in ["ticker", "mentions", "avg_sentiment"]:
            if col not in result_df.columns:
                result_df[col] = 0

        merged_df = pd.merge(result_df, existing_df, on="ticker", how="outer", suffixes=('_new', '_old'))

        for col in ["mentions_new", "mentions_old", "avg_sentiment_new", "avg_sentiment_old"]:
            if col not in merged_df.columns:
                merged_df[col] = 0
            else:
                merged_df[col] = merged_df[col].fillna(0)

        merged_df["total_mentions"] = merged_df["mentions_new"] + merged_df["mentions_old"]
        merged_df["cumulative_sentiment"] = (
            (merged_df["avg_sentiment_new"] * merged_df["mentions_new"] +
             merged_df["avg_sentiment_old"] * merged_df["mentions_old"])
            / merged_df["total_mentions"].replace(0, 1)
        )

        all_time_df = pd.DataFrame({
            "ticker": merged_df["ticker"],
            "mentions": merged_df["total_mentions"],
            "avg_sentiment": merged_df["cumulative_sentiment"]
        })

    except Exception as e:
        print(f"Could not load existing sentiment_all_time: {e}")
        all_time_df = result_df[["ticker", "mentions", "avg_sentiment"]]

    all_time_df.to_sql("sentiment_all_time", conn, if_exists="replace", index=False)
