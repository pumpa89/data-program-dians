# data_visualization/app.py
from flask import Flask, render_template
import requests
import json
import asyncio

app = Flask(__name__)

ANALYSIS_SERVICE_URL = "http://data-analysis:5050"

async def main():
    async with serve(send_data, "0.0.0.0", 8765):
        await asyncio.Future()  # Run forever

async def send_data(websocket):
    consumer = KafkaConsumer(
        'raw-financial-data',
        bootstrap_servers='kafka:9092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    for message in consumer:
        data = message.value
        await websocket.send(json.dumps(data))
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    try:
        health = requests.get(f"{ANALYSIS_SERVICE_URL}/health").json()
        if not health.get("ok"):
            return "Analysis service unavailable", 503

    except requests.ConnectionError:
        return "Unable to connect to analysis service", 500
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    asyncio.run(main())