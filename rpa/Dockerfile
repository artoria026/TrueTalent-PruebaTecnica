FROM python:3.12-slim-bookworm

RUN addgroup --system app && adduser --system --group app

# Shared, world-readable location so the non-root `app` user (below) can use
# the browser installed here as root.
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN mkdir -p /ms-playwright && chmod -R 777 /ms-playwright

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

COPY . ./rpa

USER app

CMD ["python", "-m", "rpa.main"]
