# realtime_processing/service.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
import json

class RealTimeProcessingService:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("FinancialDataProcessor") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
            .getOrCreate()
        
        self.schema = StructType([
            StructField("symbol", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("price", DoubleType()),
            StructField("volume", DoubleType()),
            StructField("high", DoubleType()),
            StructField("low", DoubleType())
        ])
    
    def process_stream(self):
        # Read from Kafka
        df = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "raw-financial-data") \
            .load()
        
        # Parse JSON data
        parsed_df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), self.schema).alias("data")) \
            .select("data.*")
        
        # Processing: Filter, aggregate, transform
        processed_df = parsed_df \
            .withWatermark("timestamp", "1 minute") \
            .groupBy(
                window("timestamp", "5 minutes"),
                "symbol"
            ) \
            .agg(
                {"price": "avg", "volume": "sum", "high": "max", "low": "min"}
            ) \
            .withColumnRenamed("avg(price)", "avg_price") \
            .withColumnRenamed("sum(volume)", "total_volume") \
            .withColumnRenamed("max(high)", "max_price") \
            .withColumnRenamed("min(low)", "min_price")
        
        # Write to Cassandra and PostgreSQL
        query = processed_df.writeStream \
            .foreachBatch(self.write_to_databases) \
            .outputMode("complete") \
            .start()
        
        query.awaitTermination()
    
    def write_to_databases(self, batch_df, batch_id):
        # Write to Cassandra
        batch_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .options(table="financial_data", keyspace="finance") \
            .save()
        
        # Write to PostgreSQL
        batch_df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://postgres:5432/finance") \
            .option("dbtable", "financial_data") \
            .option("user", "postgres") \
            .option("password", "password") \
            .mode("append") \
            .save()

if __name__ == "__main__":
    processor = RealTimeProcessingService()
    processor.process_stream()