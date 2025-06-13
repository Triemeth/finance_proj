FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt stopwords wordnet vader_lexicon

COPY . .

RUN dos2unix start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]
