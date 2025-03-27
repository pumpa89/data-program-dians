FROM bitnami/spark:3.5

USER root

# Install Python dependencies
RUN pip install --no-cache-dir \
    kafka-python==2.0.2 \
    cassandra-driver==3.28.0 \
    psycopg2-binary==2.9.9 \
    python-dotenv==1.0.0

# Set environment variables
ENV PYSPARK_PYTHON=/opt/bitnami/python/bin/python
ENV PYTHONPATH=/opt/bitnami/spark/python:/opt/bitnami/spark/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH

WORKDIR /app
COPY . .

# Fix permissions
RUN chown -R 1001:1001 /app
USER 1001