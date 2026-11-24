# Selenium test agent: Python + pytest + Selenium + Chromium + ChromeDriver
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium chromium-driver \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tests
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY test_site.py .

ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver \
    BASE_URL=http://site-staging \
    RESULTS_DIR=/tests/results

CMD ["pytest", "-v", "--junitxml=/tests/results/results.xml"]
