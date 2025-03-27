from cassandra.connector import CassandraConnector
from postgresql.connector import PostgreSQLConnector
from datetime import datetime, timedelta
import logging

class DataStorageService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cassandra = CassandraConnector()
        self.postgres = PostgreSQLConnector()
        
        # Initialize connections
        if not self.cassandra.connect():
            raise Exception("Failed to connect to Cassandra")
        
    def store_raw_data(self, data):
        """Store raw data in both databases"""
        try:
            # Store in Cassandra
            self.cassandra.insert_raw_data(data)
            
            # Store in PostgreSQL
            self.postgres.insert_raw_data(data)
            
            self.logger.info(f"Stored {len(data)} raw records")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store raw data: {e}")
            return False
    
    def store_processed_data(self, data):
        """Store processed data in both databases"""
        try:
            # Cassandra expects a different format
            cassandra_data = [{
                'symbol': item['symbol'],
                'window_start': item['window_start'],
                'window_end': item['window_end'],
                'avg_price': item['avg_price'],
                'total_volume': item['total_volume'],
                'max_price': item['max_price'],
                'min_price': item['min_price']
            } for item in data]
            
            # PostgreSQL can use the same format
            self.postgres.insert_processed_data(data)
            
            self.logger.info(f"Stored {len(data)} processed records")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store processed data: {e}")
            return False
    
    def get_historical_data(self, symbol, days=30):
        """Get historical data from both databases"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        try:
            # Get from PostgreSQL (structured)
            pg_data = self.postgres.get_processed_data(symbol, start_time, end_time)
            
            # Get from Cassandra (unstructured)
            cassandra_data = self.cassandra.get_processed_data(symbol, start_time, end_time)
            
            return {
                'postgres': pg_data,
                'cassandra': cassandra_data
            }
        except Exception as e:
            self.logger.error(f"Failed to retrieve historical data: {e}")
            return None
    
    def close(self):
        """Clean up connections"""
        self.cassandra.close()