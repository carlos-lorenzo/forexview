from flask import Flask, jsonify
from flask_cors import CORS

import pandas as pd

import yfinance as yf

app = Flask(__name__)
CORS(app)

app.debug = True

df = yf.download('EURUSD=X', period="1d", interval="15m")
df = df.rename(columns={"Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close"})

df["time"] = pd.to_datetime(df.index).astype('int64') / 10**9
df = df.drop(["Adj Close", "Volume"], axis=1)

SCALAR = 1000

df["open"] *= SCALAR
df["high"] *= SCALAR
df["low"] *= SCALAR
df["close"] *= SCALAR

base_candle_number = 10 
current_candle = base_candle_number


@app.route("/")
def index():
    return "Working"


@app.route("/api/get-chart-data", methods = ["POST", "GET"])
def get_data():
    
    chart_data = df.iloc[:base_candle_number].to_dict(orient='records')
    
    return jsonify(chart_data)


@app.route("/api/new-candle", methods = ['POST', "GET"])
def update_current_candle():
    global current_candle
    current_candle += 1
    
    return jsonify(df.iloc[current_candle].to_dict())

if __name__ == '__main__':
    app.run()