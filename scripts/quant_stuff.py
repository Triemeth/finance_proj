from sqlalchemy import create_engine
import yfinance as yf
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from datetime import date

def sharpe_ratio(return_series, rf):
    mean = return_series.mean() * 255 -rf
    sigma = return_series.std() * np.sqrt(255)
    return mean / sigma

def sortino_ratio(series, rf):
    mean = series.mean() * 255 -rf
    std_neg = series[series<0].std()*np.sqrt(255)
    return mean/std_neg

def max_drawdown(return_series):
    comp_ret = (return_series+1).cumprod()
    peak = comp_ret.expanding(min_periods=1).max()
    dd = (comp_ret/peak)-1
    return dd.min()

def calmar(df, max_dd):
    calmars = df.mean()*255/abs(max_dd)
    return calmars


if __name__ == "__main__":
    load_dotenv('/app/.env')

    db_user = os.getenv("POSTGRES_USER")
    db_pass = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")

    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    with engine.begin() as conn:
        sentiment = pd.read_sql("SELECT * FROM sentiment_day", conn)

        sentiment_good = sentiment.sort_values(['mentions', "avg_sentiment", ascending=[True, True]])
        top_companies = sentiment_good["ticker"].head(10)
        top_companies["postive"] = 1

        sentiment_bad = sentiment.sort_values(['mentions', "avg_sentiment", ascending=[True, False]])
        bottom_companies = sentiment_bad["ticker"].head(10)
        bottom_companies["postive"] = 0

        companies = pd.concat([top_companies, bottom_companies], ignore_index=True)

        today = date.today()
        one_year_ago = today.replace(year=today.year - 1)

        tnx = yf.Ticker("^TNX")
        rate = tnx.history(period="1d")
        rf_rate = rate["Close"].iloc[-1] / 100

        companies["sharpe"] = np.nan
        companies["sortino"] = np.nan
        companies["maxdd"] = np.nan
        companies["calmar"] = np.nan

        for i in range(len(companies)):
            ticker = yf.Ticker(companies["ticker"][i])
            ticker_data = ticker.history(start = one_year_ago, end = today)

            if ticker_data.empty or 'Adj Close' not in ticker_data:
                continue

            ticker_data['Daily Returns'] = ticker_data['Adj Close'].pct_change()
            returns = ticker_data['Daily Returns'].dropna()

            sharpe = sharpe_ratio(returns, rf_rate)
            sortino = sortino_ratio(returns, rf_rate)
            dd = max_drawdown(returns)
            calmar_val = calmar(returns, dd)

            companies.at[i, "sharpe"] = sharpe
            companies.at[i, "sortino"] = sortino
            companies.at[i, "maxdd"] = dd
            companies.at[i, "calmar"] = calmar_val

        companies.to_sql("quant_ratios", conn, if_exists="replace", index=False)





