import psycopg2

conn = psycopg2.connect(
    dbname="financedb",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

create_tables_sql = """
CREATE TABLE IF NOT EXISTS full_articles (
    id SERIAL PRIMARY KEY,
    article_link TEXT,
    article_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS all_tickers (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(15) UNIQUE,
    company TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS DIA (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(15) UNIQUE,
    company TEXT,
    price_on_day FLOAT,
    yield_on_day FLOAT,
    market_cap_on_day FLOAT,
    one_day_change FLOAT,
    one_month_change FLOAT,
    one_year_change FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS article_titles (
    id SERIAL PRIMARY KEY,
    article_link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS QQQ (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(15) UNIQUE,
    country VARCHAR(15),
    exchange VARCHAR(15),
    sector TEXT,
    market_cap_b FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sentiment_day (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(15) UNIQUE,
    mentions INT,
    avg_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS SPY (
    id SERIAL PRIMARY KEY,
    num INT,
    company TEXT,
    symbol VARCHAR(15) UNIQUE,
    weight FLOAT,
    price FLOAT,
    change FLOAT,
    pct_change FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sentiment_all_time (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(15) UNIQUE,
    mentions INT,
    avg_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

try:
    cur.execute(create_tables_sql)
    conn.commit()
    print("All tables created successfully.")
except Exception as e:
    print("Error creating tables:", e)
finally:
    cur.close()
    conn.close()
