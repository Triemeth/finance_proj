# Sentiment Yahoo News Project

## Overview
This project scrapes news articles from Yahoo Finance for a given day and performs sentiment analysis on them. The focus is on identifying how often companies from the Dow Jones Industrial Average, Nasdaq-100, and S&P 500 are mentioned, and determining the overall sentiment surrounding those mentions. A few financal metrics are applied and then shown on PowerBI

## Steps symplified
* A containerized PostgreSQL database is used to store scraped and processed data.
* All stock tickers and company names for companies within the Dow Jones Industrial Average, Nasdaq-100, and S&P 500 are scraped.
* Articles from Yahoo Finance news are scraped.
* The articles are parsed for the company names(or ticker) if found the mention count is increased and the sentiment is calculated for the sentience where it was mentioned.
* Metrics such as Sharpe ratio and max drew down are calculated using the top 10 highest and lowest sentiments for the day (which must be above the threshold limit).
* Once all data is ready it is connected to PowerBI to create a simple dashboard.
  
![Power BI Dashboard](readme_img/fin_analysis_dash)

## Future Plans
