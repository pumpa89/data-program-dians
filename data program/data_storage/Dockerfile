# data_storage/Dockerfile
FROM python:3.9-slim

# Install system dependencies for PostgreSQL and Cassandra clients
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV CASSANDRA_HOSTS=cassandra
ENV CASSANDRA_PORT=9042
ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=finance

# Initialize databases and run service
CMD ["sh", "-c", "python initialize.py && python service.py"]