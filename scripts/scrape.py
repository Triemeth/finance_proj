from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random
import traceback
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

URL = "https://finance.yahoo.com/news/"

def get_chrome_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(options=options)

def get_full_article_list():
    driver = get_chrome_driver()
    try:
        driver.get(URL)
        for _ in range(5): 
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = []

        for tag in soup.select('section[role="article"] a[href]'):
            href = tag.get("href")
            if href:
                full_url = f"https://finance.yahoo.com{href}" if href.startswith("/") else href
                if full_url not in articles:
                    articles.append(full_url)

        return articles
    finally:
        driver.quit()

def scrape_articles(articles):
    driver = get_chrome_driver()
    article_data = []

    try:
        for i, art in enumerate(articles):  
            print(f"[{i+1}] Fetching: {art}")
            time.sleep(random.uniform(2, 5))

            try:
                driver.set_page_load_timeout(30)
                driver.get(art)
            except Exception as e:
                print(f"Timeout or connection error for {art}: {e}")
                continue

            try:
                read_more_buttons = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//a[contains(text(), 'Read more') or contains(text(), 'Continue reading') or contains(text(), 'Full Article')]")
                    )
                )
                for btn in read_more_buttons:
                    try:
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(1)
                    except Exception as inner_e:
                        print(f"Could not click button: {inner_e}")
            except Exception:
                pass  

            try:
                paragraphs = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "p"))
                )
                article_text = " ".join([p.text for p in paragraphs if p.text.strip()])
            except Exception:
                article_text = ""

            article_data.append({
                "url": art,
                "text": article_text
            })

    finally:
        driver.quit()

    return article_data

if __name__ == "__main__":
    load_dotenv('/app/.env')

    db_user = os.getenv("POSTGRES_USER")
    db_pass = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")

    try:
        articles = get_full_article_list()
        if not articles:
            print("No articles found.")
        else:
            article_data = scrape_articles(articles)

            titles_df = pd.DataFrame({'article_link': articles})
            full_df = pd.DataFrame(article_data)

            full_df.rename(columns={"text":"article_text"}, inplace=True)

            time.sleep(5)

            engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

            titles_df.to_sql("article_titles", engine, if_exists="append", index=False)
            full_df.to_sql("full_articles", engine, if_exists="append", index=False)


    except Exception:
        print("An error occurred during scraping:")
        traceback.print_exc()

