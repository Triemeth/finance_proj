import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from io import StringIO
import time
from sqlalchemy import create_engine, insert, text

def convert_to_billion(val):
    val = val.strip('$£')
    if val.endswith('bn'):
        return float(val.replace('bn', ''))
    elif val.endswith('m'):
        return float(val.replace('m', '')) / 1000
    else:
        return None

def get_dia():
    url = 'https://www.dogsofthedow.com/dow-jones-industrial-average-companies.htm'
    request = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})

    soup = bs(request.text, "lxml")
    stats = soup.find('table',class_='tablepress tablepress-id-42 tablepress-responsive')
    pulled_df = pd.read_html(StringIO(str(stats)))[0]

    return pulled_df

def get_spy():
    url = 'https://www.slickcharts.com/sp500'
    request = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})

    soup = bs(request.text, "lxml")
    stats = soup.find('table',class_='table table-hover table-borderless table-sm')

    df = pd.read_html(StringIO(str(stats)))[0]

    df['% Chg'] = df['% Chg'].str.strip('()-%')
    df['% Chg'] = pd.to_numeric(df['% Chg'])
    df['Chg'] = pd.to_numeric(df['Chg'])

    return df

def get_qqq():

    df = pd.DataFrame()

    urls = ['https://www.dividendmax.com/market-index-constituents/nasdaq-100',
    'https://www.dividendmax.com/market-index-constituents/nasdaq-100?page=2',
    'https://www.dividendmax.com/market-index-constituents/nasdaq-100?page=3']

    for url in urls:
        request = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
        soup = bs(request.text, "lxml")

        stats = soup.find('table',class_='mdc-data-table__table')
        temp = pd.read_html(StringIO(str(stats)))[0]

        df = pd.concat([df, temp], ignore_index=True)

    df.rename(columns={'Market Cap':'Market Cap $bn'},inplace=True)
    df['Market Cap $bn'] = df['Market Cap $bn'].apply(convert_to_billion)

    df = df.sort_values('Market Cap $bn',ascending=False)

    return df

if __name__ == "__main__":
    dia = get_dia()
    spy = get_spy()
    qqq = get_qqq()

    #dia.to_csv("data/dia_df.csv", index = False)
    #spy.to_csv("data/spy_df.csv", index = False)
    #qqq.to_csv("data/qqq_df.csv", index = False)

    dia_tickers = dia[["Symbol", "Company"]]
    spy_tickers = spy[["Symbol", "Company"]]
    qqq_tickers = qqq[["Ticker", "Company"]]

    qqq_tickers["Symbol"] = qqq_tickers["Ticker"]
    qqq_tickers = qqq_tickers.drop(columns = "Ticker", axis = 1)

    qqq["Country"] = qqq["Unnamed: 2"]
    qqq["Market_cap_b"] = qqq["Market Cap $bn"]
    qqq = qqq.drop(columns = ["Market Cap $bn", "Unnamed: 2"], axis = 1)

    spy["Pct_chg"] = spy["% Chg"]
    spy = spy.drop(columns = ["% Chg", "#"], axis = 1)

    dia["Price_on_day"] = dia["Price 6-3-25"]
    dia["Yield_on_day"] = dia["Yield on 6/3/25"]
    dia["Market_cap_on_day"] = dia["Market Cap on 6/3/25"]
    dia["One_day_change"] = dia["1d Chg on 6/3/25"]
    dia["One_month_change"] = dia["1m Chg on 6/3/25"]
    dia["One_year_change"] = dia["12m Chg on 6/3/25"]
    dia = dia.drop(columns = ["Price 6-3-25", "Yield on 6/3/25", 
                              "Market Cap on 6/3/25", "1d Chg on 6/3/25",
                              "1m Chg on 6/3/25", "12m Chg on 6/3/25"], axis = 1)

    ticker_df = pd.concat([dia_tickers, spy_tickers, qqq_tickers], ignore_index=True)
    ticker_df = ticker_df.drop_duplicates()
    
    #ticker_df.to_csv("data/all_tickers.csv", index = False)

"""    time.sleep(5)

    engine = create_engine("postgresql+psycopg2://postgres:postgres@db:5432/financedb")

    dia.to_sql("DIA", engine, if_exists="replace", index=False)
    spy.to_sql("SPY", engine, if_exists="replace", index=False)
    qqq.to_sql("QQQ", engine, if_exists="replace", index=False)
    ticker_df.to_sql("all_tickers", engine, if_exists="replace", index=False)"""
    

#py -3.12 spy_dia_qqq_comp.py