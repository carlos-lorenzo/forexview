from flask import Flask, jsonify, request
from flask_cors import CORS

import pandas as pd

from defractalise_ohlc import defractalise_ohlc


app = Flask(__name__)
CORS(app)

app.debug = True


df = pd.read_csv("Data/EURUSD_1m.csv", nrows=10000)

df = df.rename(columns={"Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close"})

df["time"] = pd.to_datetime(df["Time"]).astype('int64') / 10**9

df = df.drop(["Volume", "Time"], axis=1)

SCALAR = 1000

df["open"] *= SCALAR
df["high"] *= SCALAR
df["low"] *= SCALAR
df["close"] *= SCALAR

time_frames = {
    "1m": df,
    "15m": defractalise_ohlc(df=df, interval="15m"),
    "1h": defractalise_ohlc(df=df, interval="1h"),
    "4h": defractalise_ohlc(df=df, interval="4h"),
    "1D": defractalise_ohlc(df=df, interval="1D"),
    "1W": defractalise_ohlc(df=df, interval="1W"),
    "1M": defractalise_ohlc(df=df, interval="1M"),
}


base_candle_number = 100
current_candle = base_candle_number

@app.route("/")
def index():
    return "Working"


@app.route("/api/get-chart-data", methods = ["POST", "GET"])
def get_data():
    global current_candle
    
    current_candle = base_candle_number
    
    args = request.args
    time_frame = args.get("tf", "1m")
    
    
    chart_data = time_frames.get(time_frame).iloc[:base_candle_number].to_dict(orient='records')
    
    return jsonify(chart_data)


@app.route("/api/new-candle", methods = ['POST', "GET"])
def update_current_candle():
    global current_candle
    current_candle += 1
    
    args = request.args
    time_frame = args.get("tf", "1m")
    
    
    return jsonify(time_frames.get(time_frame).iloc[current_candle].to_dict())

if __name__ == '__main__':
    app.run()