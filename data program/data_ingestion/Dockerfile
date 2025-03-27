FROM python:3.9-slim

# Install system dependencies only if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Optional: Default fallback for KAFKA_BROKERS (override in compose)
ENV KAFKA_BROKERS=kafka:9092
ENV YAHOO_SYMBOLS=AAPL,MSFT,GOOGL

CMD ["python", "-u", "service.py"]