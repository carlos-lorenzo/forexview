from dataclasses import dataclass
from typing import List, Dict

from pandas import DataFrame

from flask import Flask, request, jsonify
from flask_cors import CORS

from defractalise_ohlc import interval_to_minutes

from .broker import Broker
from .pair import Pair


@dataclass
class API(Flask):
    broker: Broker
    debug: bool = False
    
    def __init__(self, broker: Broker, debug: bool = False):
        super().__init__(__name__)
        self.broker = broker
        
        CORS(self)

        self.route('/')(self.index)
        self.route("/api/get-chart-data", methods = ['POST', "GET"])(self.get_data)
        self.route("/api/new-candle", methods = ['POST', "GET"])(self.get_current_candle)
        self.route("/api/update-time", methods = ["POST", "GET"])(self.update_time)
    
    def index(self):
        return 'Welcome to the API!'
    

    def get_data(self):
        args = request.args
        time_frame: str = args.get("tf", "1m")
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get(pair, "EURUSD")
        
        ohlc: DataFrame = pair_data.time_frames.get(time_frame, "1m").get("ohlc")
        last_candle_index: int = pair_data.current_minute // interval_to_minutes(time_frame)
        
        chart_data: List[Dict[str, float]] = ohlc.iloc[:last_candle_index].to_dict(orient="records")
        
        return jsonify(chart_data)
    
    
    def get_current_candle(self):
        
        args = request.args
        time_frame: str = args.get("tf", "1m")
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get(pair, "EURUSD")
        
        ohlc: DataFrame = pair_data.time_frames.get(time_frame, "1m").get("ohlc")
        last_candle_index: int = pair_data.current_minute // interval_to_minutes(time_frame)
        
        new_candle: Dict[str, float] = ohlc.iloc[last_candle_index].to_dict()
        
        return jsonify(new_candle)
    
    
    def update_time(self):
        args = request.args
        time_frame: str = args.get("tf", "1m")
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get(pair, "EURUSD")
        
        pair_data.current_minute += interval_to_minutes(time_frame)
        
    
    def reset_time(self):
        args = request.args
        
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get(pair, "EURUSD")
        
        pair_data.current_minute = pair_data.initilise_minutes()
    
    
    
        
