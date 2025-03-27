# data_visualization/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV ANALYSIS_SERVICE_URL=http://data-analysis-service:5000

# Install frontend dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    npm \
    && npm install -g d3 plotly.js \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]