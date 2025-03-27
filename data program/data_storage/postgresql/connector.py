import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
import logging
from contextlib import contextmanager

class PostgreSQLConnector:
    def __init__(self, 
                 host='postgres',
                 database='finance',
                 user='postgres',
                 password='password',
                 port=5432):
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def insert_raw_data(self, data):
        query = """
        INSERT INTO raw_financial_data 
        (symbol, timestamp, open, high, low, close, volume)
        VALUES (%(symbol)s, %(timestamp)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s)
        ON CONFLICT (symbol, timestamp) DO NOTHING
        """
        
        with self.get_connection() as conn, conn.cursor() as cursor:
            execute_batch(cursor, query, data)
            conn.commit()
    
    def get_processed_data(self, symbol, start_time, end_time):
        query = """
        SELECT * FROM processed_financial_data
        WHERE symbol = %s AND window_start >= %s AND window_end <= %s
        ORDER BY window_start DESC
        """
        
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query, (symbol, start_time, end_time))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
    
    def execute_query(self, query, params=None):
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.commit()
            return None