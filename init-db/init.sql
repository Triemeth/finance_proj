CREATE TABLE IF NOT EXISTS full_articles (
    id SERIAL PRIMARY KEY,
    url TEXT,
    article_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS all_tickers (
    id SERIAL PRIMARY KEY,
    Symbol VARCHAR(15) UNIQUE,
    Company TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dia (
    id SERIAL PRIMARY KEY,
    Symbol VARCHAR(15) UNIQUE,
    Company TEXT,
    Price_on_day FLOAT,
    Yield_on_day FLOAT,
    Market_cap_on_day FLOAT,
    One_day_change FLOAT,
    One_month_change FLOAT,
    One_year_change FLOAT,
    Created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS article_titles (
    id SERIAL PRIMARY KEY,
    article_link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qqq (
    id SERIAL PRIMARY KEY,
    Company TEXT,
    Ticker VARCHAR(15) UNIQUE,
    Country VARCHAR(15),
    Exchange VARCHAR(15),
    Sector TEXT,
    Market_cap_b FLOAT,
    Created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sentiment_day (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(15) UNIQUE,
    mentions INT,
    avg_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS spy (
    id SERIAL PRIMARY KEY,
    Company TEXT,
    Symbol VARCHAR(15) UNIQUE,
    Weight FLOAT,
    Price FLOAT,
    Chg FLOAT,
    Pct_chg FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sentiment_all_time (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(15) UNIQUE,
    mentions INT,
    avg_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXIST quant_ratios(
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(15) UNIQUE,
    postive INT,
    sortino FLOAT,
    sharpe FLOAT,
    maxdd FLOAT,
    calmar FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
