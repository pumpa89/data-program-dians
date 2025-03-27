from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import BatchStatement
import logging

class CassandraConnector:
    def __init__(self, hosts=['cassandra'], port=9042, keyspace='finance'):
        self.hosts = hosts
        self.port = port
        self.keyspace = keyspace
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        try:
            auth_provider = PlainTextAuthProvider(
                username='cassandra',
                password='cassandra'
            )
            cluster = Cluster(
                self.hosts,
                port=self.port,
                auth_provider=auth_provider
            )
            self.session = cluster.connect(self.keyspace)
            self.logger.info("Connected to Cassandra cluster")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Cassandra: {e}")
            return False
    
    def insert_raw_data(self, data):
        query = """
        INSERT INTO raw_financial_data 
        (symbol, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        prepared = self.session.prepare(query)
        
        batch = BatchStatement()
        for record in data:
            batch.add(prepared, (
                record['symbol'],
                record['timestamp'],
                record['open'],
                record['high'],
                record['low'],
                record['close'],
                record['volume']
            ))
        
        self.session.execute(batch)
    
    def get_processed_data(self, symbol, start_time, end_time):
        query = """
        SELECT * FROM processed_financial_data
        WHERE symbol = ? AND window_start >= ? AND window_end <= ?
        """
        prepared = self.session.prepare(query)
        result = self.session.execute(prepared, (symbol, start_time, end_time))
        return list(result)
    
    def close(self):
        if self.session:
            self.session.shutdown()