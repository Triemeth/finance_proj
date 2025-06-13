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
nltk.download('punkt_tab')

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize

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
    
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token not in stopwords.words('english')]
    
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    processed_text = ' '.join(lemmatized_tokens)
    return processed_text

def get_sentiment(text):

    scores = analyzer.polarity_scores(text)
    sentiment = 1 if scores['pos'] > 0 else 0
    return sentiment


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
            sentences = sent_tokenize(text)

            for sentence in sentences:
                mentioned = False

                if pd.notna(symbol) and count_occurrences(symbol, sentence, case_sensitive=True) > 0:
                    mentioned = True

                if pd.notna(company) and count_occurrences(company, sentence, case_sensitive=False) > 0:
                    mentioned = True

                if mentioned:
                    mention_count += 1
                    preprocessed = preprocess_text(sentence)
                    sentiment = get_sentiment(preprocessed)
                    ticker_sentiments[ticker_key].append(sentiment)

        ticker_counts[ticker_key] = mention_count

    sentiment_avg = {
        ticker: sum(sentiments)/len(sentiments) if sentiments else 0
        for ticker, sentiments in ticker_sentiments.items()
    }

    result_df = pd.DataFrame({
        "ticker": list(ticker_counts.keys()),
        "mentions": list(ticker_counts.values()),
        "avg_Sentiment": [sentiment_avg.get(t, 0.0) for t in ticker_counts.keys()],
    })

    result_df.to_sql("sentiment_day", conn, if_exists="replace", index=False)

    try:
        existing_df = pd.read_sql("SELECT * FROM sentiment_all_time", conn)
        merged_df = pd.merge(result_df, existing_df, on="ticker", how="outer", suffixes=('_new', '_old'))

        merged_df["mentions_new"] = merged_df["mentions_new"].fillna(0)
        merged_df["mentions_old"] = merged_df["mentions_old"].fillna(0)
        merged_df["avg_sentiment_new"] = merged_df["avg_sentiment_new"].fillna(0)
        merged_df["avg_sentiment_old"] = merged_df["avg_sentiment_old"].fillna(0)

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

    except Exception:
        all_time_df = result_df[["ticker", "mentions", "avg_sentiment"]]

    all_time_df.to_sql("sentiment_all_time", conn, if_exists="replace", index=False)


#py -3.12 sent_count_sum.py