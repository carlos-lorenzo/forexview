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
        self.route("/api/reset-time", methods = ["POST", "GET"])(self.reset_time)
        self.route("/api/get-balance", methods = ["POST", "GET"])(self.get_balance)
        self.route("/api/open-position", methods = ["POST", "GET"])(self.open_position)
    
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
        
        return jsonify({"status" : "time updated"})
    
    def reset_time(self):
        args = request.args
        
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get(pair, "EURUSD")
        
        pair_data.current_minute = pair_data.initilise_minute()

        return jsonify({"status" : "time reset"})
    
    def get_balance(self):
        return jsonify({"balance": self.broker.balance})
    
    
    def open_position(self):
        args = request.args
        order_type: str = args.get("type", "long")
        size: float = float(args.get("size", self.broker.balance * 0.01))
        pair: str = args.get("pair", "EURUSD").upper()
        take_profit: float = float(args.get("tp", None))
        stop_loss: float = float(args.get("sl", None))

        meta = self.broker.open_position(order_type=order_type,
                                           size=size,
                                           pair=pair,
                                           take_profit=take_profit,
                                           stop_loss=stop_loss)
        
        return jsonify({"status": meta.get("status"),
                        "type": order_type,
                        "pair": pair,
                        "rate": self.broker.pairs.get(pair).get_current_candle()["close"]})
    
        
