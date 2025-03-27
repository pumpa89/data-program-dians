import requests
from websocket import create_connection
import json
import time
from kafka import KafkaProducer
from kafka import KafkaAdminClient
from dotenv import load_dotenv
import os
from kafka.errors import NoBrokersAvailable

load_dotenv()  # Load .env file

config = {
    "alpha_vantage": {
        "api_key": os.getenv("ALPHA_VANTAGE_API_KEY"),
        "symbols": ["AAPL", "MSFT"]
    }
}


class DataIngestionService:
    def __init__(self):
        self.kafka_producer = None
        self.max_retries = 5
        self.retry_delay = 5
        self._init_kafka()  # Initialize Kafka connection

    def _init_kafka(self, retries=10, delay=10):  # Increased retries and delay
        for attempt in range(retries):
            try:
                self.kafka_producer = KafkaProducer(
                    bootstrap_servers=['kafka:9092'],
                    api_version=(2, 8, 1),
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    request_timeout_ms=60000,  # Increased timeout
                    retries=5,
                    metadata_max_age_ms=30000
                )
                print("✅ Successfully connected to Kafka")
                # Verify connection by listing topics
                admin_client = KafkaAdminClient(bootstrap_servers='kafka:9092')
                print("Existing topics:", admin_client.list_topics())
                return
            except Exception as e:
                print(f"⚠️ Kafka connection failed: {str(e)}")
                if attempt == retries - 1:
                    raise
                time.sleep(delay)

    def fetch_from_yahoo_finance(self, symbols):
        base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        for symbol in symbols:
            url = f"{base_url}{symbol}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.kafka_producer.send('raw-financial-data', data)

    # Add time loop and data parsing
    def fetch_alpha_vantage_data(self, api_key, symbols):
        base_url = "https://www.alphavantage.co/query"
        while True:  # Continuous fetching
            for symbol in symbols:
                try:
                    params = {
                        "function": "TIME_SERIES_INTRADAY",
                        "symbol": symbol,
                        "interval": "5min",
                        "apikey": api_key,
                        "outputsize": "compact"
                    }
                    response = requests.get(base_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        # Extract and format time series data
                        time_series = data.get("Time Series (5min)", {})
                        for timestamp, values in time_series.items():
                            kafka_data = {
                                "symbol": symbol,
                                "timestamp": timestamp,
                                "open": float(values["1. open"]),
                                "high": float(values["2. high"]),
                                "low": float(values["3. low"]),
                                "close": float(values["4. close"]),
                                "volume": int(values["5. volume"])
                            }
                            self.kafka_producer.send('raw-financial-data', kafka_data)
                        print(f"✅ Sent {len(time_series)} records for {symbol}")
                    else:
                        print(f"⚠️ API Error: {response.text}")
                    time.sleep(60)  # Respect API rate limits
                except Exception as e:
                    print(f"🔥 Error: {str(e)}")
                    time.sleep(30)

    def run(self, sources):
        if 'alpha_vantage' in sources:
            self.fetch_alpha_vantage_data(
                sources['alpha_vantage']['api_key'],
                sources['alpha_vantage']['symbols']
            )

if __name__ == "__main__":
    service = DataIngestionService()
    service.run({
        "alpha_vantage": {
            "api_key": os.getenv("ALPHA_VANTAGE_API_KEY"),
            "symbols": os.getenv("SYMBOLS", "AAPL,MSFT").split(",")
        }
    })