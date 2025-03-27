# data_analysis/service.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from cassandra.cluster import Cluster
from psycopg2 import connect
import joblib
import json
from flask import Flask, jsonify

app = Flask(__name__)

class DataAnalysisService:
    def __init__(self):
        # Connect to Cassandra
        self.cassandra_cluster = Cluster(['cassandra'])
        self.cassandra_session = self.cassandra_cluster.connect('finance')
        
        # Connect to PostgreSQL
        self.pg_conn = connect(
            host="postgres",
            database="finance",
            user="postgres",
            password="password"
        )

    def load_data(self, symbol, days=30):
        try:
            query = """
            SELECT symbol, window_start, avg_price, total_volume, max_price, min_price
            FROM processed_financial_data
            WHERE symbol = %s
            AND window_start >= toTimestamp(now()) - %s
            ALLOW FILTERING
            """
            result = self.cassandra_session.execute(query, (symbol, days * 24 * 60 * 60 * 1000))
            return pd.DataFrame([dict(row._asdict()) for row in result])
        except Exception as e:
            print(f"Database error: {str(e)}")
            return pd.DataFrame()

    # Add error handling to routes
    @app.route('/predict/<symbol>', methods=['GET'])
    def get_prediction(symbol):
        try:
            service = DataAnalysisService()
            df = service.load_data(symbol)
            if df.empty:
                return jsonify({"error": "No data available"}), 404

            latest_data = df.iloc[-1]
            # ... rest of prediction logic ...
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def train_model(self, symbol):
        df = self.load_data(symbol)
        if len(df) < 100:
            return None  # Not enough data
        
        # Feature engineering
        df['price_change'] = df['avg_price'].pct_change()
        df['volume_change'] = df['total_volume'].pct_change()
        df = df.dropna()
        
        X = df[['avg_price', 'total_volume', 'max_price', 'min_price', 'volume_change']]
        y = df['price_change'].shift(-1).dropna()
        X = X.iloc[:-1]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(model, f'models/{symbol}_model.pkl')
        return model.score(X_test, y_test)
    
    def predict(self, symbol, data):
        try:
            model = joblib.load(f'models/{symbol}_model.pkl')
            prediction = model.predict([data])
            return float(prediction[0])
        except:
            return None
    
    def generate_report(self, symbol):
        df = self.load_data(symbol)
        report = {
            'symbol': symbol,
            'last_price': df['avg_price'].iloc[-1],
            '30_day_avg': df['avg_price'].mean(),
            '30_day_high': df['max_price'].max(),
            '30_day_low': df['min_price'].min(),
            '30_day_volume': df['total_volume'].sum()
        }
        return report

@app.route('/report/<symbol>', methods=['GET'])
def get_report(symbol):
    service = DataAnalysisService()
    report = service.generate_report(symbol)
    return jsonify(report)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)