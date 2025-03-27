# data_analysis/Dockerfile
FROM python:3.9-slim

# Install system dependencies for scikit-learn
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV FLASK_APP=service.py
ENV FLASK_ENV=production
ENV CASSANDRA_HOST=cassandra
ENV POSTGRES_HOST=postgres
ENV MODEL_DIR=/app/models
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Create model directory
RUN mkdir -p ${MODEL_DIR}

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "service:app"]