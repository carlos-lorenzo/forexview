from typing import Dict

from flask import Flask, jsonify, request
from flask_cors import CORS

import pandas as pd

from defractalise_ohlc import interval_to_minutes

def initilise_minutes(time_frames: Dict) -> int:
    return max([ohlc_data.get("n_candles") for ohlc_data in time_frames.values()])


app = Flask(__name__)
CORS(app)

app.debug = True



time_frames = {
    "1m": {"ohlc": pd.read_csv("Data/1m_EURUSD.csv"), "n_candles": 1},
    "15m": {"ohlc": pd.read_csv("Data/15m_EURUSD.csv"), "n_candles": 15},
    "1h": {"ohlc": pd.read_csv("Data/1h_EURUSD.csv"), "n_candles": 60},
    "4h": {"ohlc": pd.read_csv("Data/4h_EURUSD.csv"), "n_candles": 240},
    "1D": {"ohlc": pd.read_csv("Data/1D_EURUSD.csv"), "n_candles": 1440},
}


current_minute = initilise_minutes(time_frames=time_frames)

@app.route("/")
def index():
    return "Working"


@app.route("/api/get-chart-data", methods = ["POST", "GET"])
def get_data():
    
    global current_minute
    
    args = request.args
    time_frame = args.get("tf", "1m")
    
    
    ohlc_data = time_frames.get(time_frame).get("ohlc")
    
    last_candle_index = current_minute // interval_to_minutes(time_frame)
    
    chart_data = ohlc_data.iloc[:last_candle_index].to_dict(orient='records')
    
    return jsonify(chart_data)


@app.route("/api/new-candle", methods = ['POST', "GET"])
def update_current_candle():
    global current_minute
    
    
    args = request.args
    time_frame = args.get("tf", "1m")
    
    ohlc_data = time_frames.get(time_frame).get("ohlc")
    
    last_candle_index = current_minute // interval_to_minutes(time_frame)
    
    new_candle = ohlc_data.iloc[last_candle_index].to_dict()
    
    return new_candle


@app.route("/api/update-time", methods = ["POST", "GET"])
def update_time():
    global current_minute
    
    args = request.args
    time_frame = args.get("tf", "1m")
    
    current_minute += interval_to_minutes(time_frame)

    
    return jsonify({"current_time": current_minute})


@app.route("/api/reset-time", methods = ["POST", "GET"])
def reset_time():
    global current_minute
    
    current_minute = initilise_minutes(time_frames=time_frames)

    return {"stauts": 0}

if __name__ == '__main__':
    app.run()