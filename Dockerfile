FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt stopwords wordnet vader_lexicon

CMD ["python", "spy_dia_qqq_comp.py", "scrape.py"]
