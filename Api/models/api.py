from dataclasses import dataclass
from typing import List, Dict

from pandas import DataFrame

from flask import Flask, request, jsonify
from flask_cors import CORS

import utils

from .broker import Broker
from .pair import Pair
from .position import Position


@dataclass
class API(Flask):
    """
    API class to provide an interface with a Broker object\n
    Inherits from flask.Flask

    Args:
        broker (Broker): The broker class for which it will provide an interface
        debug (bool): Sets debug property from parent Flask
    """
    
    broker: Broker
    debug: bool = False
    
    def __init__(self, broker: Broker, debug: bool = False):
        super().__init__(__name__)
        self.debug = debug
        self.broker = broker
        
        CORS(self)

        self.route('/')(self.index)
        self.route("/api/get-chart-data", methods = ['POST', "GET"])(self.get_data)
        self.route("/api/new-candle", methods = ['POST', "GET"])(self.get_current_candle)
        self.route("/api/update-time", methods = ["POST", "GET"])(self.update_time)
        self.route("/api/reset", methods = ["POST", "GET"])(self.reset)
        self.route("/api/get-balance", methods = ["POST", "GET"])(self.get_balance)
        self.route("/api/get-equity", methods = ["POST", "GET"])(self.get_equity)
        self.route("/api/open-position", methods = ["POST", "GET"])(self.open_position)
        self.route("/api/close-position", methods = ["POST", "GET"])(self.close_position)
        self.route("/api/fetch-open-positions", methods = ["POST", "GET"])(self.get_open_positions)
        self.route("/api/create-order-blocks", methods = ["POST", "GET"])(self.create_order_block)
        self.route("/api/fetch-order-blocks", methods = ["POST", "GET"])(self.fetch_order_blocks)
        #self.route("/api/save-broker", methods = ["POST", "GET"])(self.save_broker)
        #self.route("/api/load-broker", methods = ["POST", "GET"])(self.load_broker)
        
    
    
    def index(self) -> str:
        """
        Default route, to verify API's up and running

        Returns:
            str: Welcome message
        """
        return 'Welcome to the API!'
    

    def get_data(self) -> List[Dict[str, float]]:
        """
        Fetch the candles for a given pair and time frame will provide the last 1000 candles 

        Request args:
            time_frame (str): The timeframe for which data will be returned
            pair (str): The pair for which data will be returned
        
        Returns:
            List[Dict[str, float]]: A list of candles 
        """
        args = request.args
        time_frame: str = args.get("tf", "1m")
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get(pair, "EURUSD")
        
        ohlc: DataFrame = pair_data.time_frames.get(time_frame, "1m").get("ohlc")
        last_candle_index: int = pair_data.current_minute // utils.interval_to_minutes(time_frame)
        if last_candle_index > 3000:
            first_candle_index = last_candle_index - 3000
        else:
            first_candle_index = 0
            
        chart_data: List[Dict[str, float]] = ohlc.iloc[first_candle_index:last_candle_index].to_dict(orient="records")
        
        return jsonify(chart_data)
    
    def get_current_candle(self) -> Dict[str, float]:
        """
        Fetch the current candle of a given time frame

        Request args:
            time_frame (str): The timeframe for which data will be returned
            pair (str): The pair for which data will be returned

        Returns:
            Dict[str, float]: Single candle
        """
        args = request.args
        time_frame: str = args.get("tf", "1m")
        pair: str = args.get("pair", "EURUSD").upper()
        
        
        pair_data: Pair = self.broker.pairs.get("EURUSD") # replace with pair
        
        ohlc: DataFrame = pair_data.time_frames.get(time_frame, "1m").get("ohlc")
        last_candle_index: int = pair_data.current_minute // utils.interval_to_minutes(time_frame)
        
        
        
        new_candle: Dict[str, float] = ohlc.iloc[last_candle_index].to_dict()
        
        return jsonify(new_candle)
    
    def update_time(self) -> Dict[str, str]:
        """
        Update time (controls current candle)\n
        Will update time based on the number of 1m candles which form a single interval\n
        Example:\n
            - 15m interval will add 15 minutes (15 * 1)
            - 4h interval will add 240 minutes (4 * 60)

        Request args:
            time_frame (str): The timeframe for which time will be updated
            pair (str): The pair for which time will be updated
        
        Returns:
            Dict[str, str]: Status message
        """
        args = request.args
        time_frame: str = args.get("tf", "1m")
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get("EURUSD") # replace with pair
        
        pair_data.current_minute += utils.interval_to_minutes(time_frame)
        
        self.broker.update()
        
        return jsonify({"status" : "time updated"})
    
    def reset(self) -> Dict[str, str]:
        """
        Resets time, sets it back to the initial state (set by Pair object)

        Returns:
            Dict[str, str]: Status message
        """
        args = request.args
        
        pair: str = args.get("pair", "EURUSD").upper()
        
        pair_data: Pair = self.broker.pairs.get(pair) # replace with pairs
        
        pair_data.current_minute = pair_data.initilise_minute()
        pair_data.order_blocks = []
        
        
        self.broker.balance = 10000
        self.broker.equity = self.broker.balance
        self.broker.open_positions = []
        
        
        
        return jsonify({"status" : "reset"})
     
    def get_balance(self) -> Dict[str, float]:
        """
        Fetch the balance of self.Broker
        
        Returns:
            Dict[str, float]: Current balance
        """
        return jsonify({"balance": self.broker.balance})
     
    def get_equity(self) -> Dict[str, float]:
        """
        Fetch the equity of self.Broker
        
        Returns:
            Dict[str, float]: Current equity
        """
        return jsonify({"equity": self.broker.equity})
    
    def open_position(self) -> Dict[str, str | float]:
        """
        Opens a position

        Request args:
            order_type (str): The order type (short | long)
            pair (str): The pair for which the position will be opened
            take_profit (float): Take profit rate (see Position.take_profit for more info)
            stop_loss (float): Stop loss rate (see Position.stop_loss for more info)
        
        Returns:
            Dict[str, str | float]: Position meta-data (status, type, pair and rate)
        """
        
        args = request.args
        order_type: str = args.get("type", "long")
        pair: str = args.get("pair", "EURUSD").upper()
        size: float = self.broker.balance * 0.01
        
        
        take_profit: float = args.get("tp", None)
        if take_profit: take_profit = float(take_profit)
        
        stop_loss: float = args.get("sl", None)
        if stop_loss: stop_loss = float(stop_loss)

        
        
        meta = self.broker.open_position(order_type=order_type,
                                         size=size,
                                         pair=pair,
                                         take_profit=take_profit,
                                         stop_loss=stop_loss)
        
        
        return jsonify({"status": meta.get("status"),
                        "type": order_type,
                        "pair": pair,
                        "rate": self.broker.pairs.get(pair).get_current_candle()["close"]})
        
    def close_position(self) -> Dict[str, str]:
        """
        Closes a position with a given id
        
        Request args:
            id (str): An id (alphanumeric string)
        

        Returns:
            Dict[str, str]: Status
        """

        
        args = request.args
        position_id = args.get("id")
        
        meta = self.broker.close_position(position_id=position_id)
        
        return jsonify(meta)
        
    def get_open_positions(self) -> List[Dict[str, str | float]]:
        """
        Fetches all open positions

        Returns:
            List[Dict[str, str | float]]: List containing all open Position's data (id, type, open_rate, starting_size, profit_loss, tp, sl)
        """
        
        
        open_positions: List[Position] = self.broker.open_positions
        
        
        open_positions_data = []
        for position in open_positions:
            open_positions_data.append({"id": position.uid,
                                        "type": position.order_type,
                                        "open_rate": position.order_rate,
                                        "starting_size": position.starting_size,
                                        "profit_loss": position.profit_loss,
                                        "tp": position.take_profit,
                                        "sl": position.stop_loss})
            
        return jsonify(open_positions_data)
        
    def fetch_order_blocks(self) -> Dict[str, List[Dict[str, float | str]]]:
        args = request.args
        time_frame = args.get("tf", "15m")
        
        order_blocks = {}
        for pair, pair_data in self.broker.pairs.items():
            pair_order_blocks = []
            for pair_order_block in [order_block for order_block in pair_data.order_blocks if order_block.pair == pair]:
                pair_order_blocks.append({"id": pair_order_block.uid, "data": {
                        "type": pair_order_block.type,
                        "max_rate": pair_order_block.max_rate,
                        "min_rate": pair_order_block.min_rate,
                        "max_series_data": [{"time": time, "value": pair_order_block.max_rate} for time in range(pair_order_block.start_time, pair_data.current_minute, utils.interval_to_minutes(time_frame))],
                        "min_series_data": [{"time": time, "value": pair_order_block.min_rate} for time in range(pair_order_block.start_time, pair_data.current_minute, utils.interval_to_minutes(time_frame))],
                        }})
    
                    
            
            order_blocks[pair] = pair_order_blocks
                
        return jsonify(order_blocks)
    
    def create_order_block(self) -> Dict[str, str]:
        args = request.args
        pair: str = args.get("pair", "EURUSD")
        order_block_type: str = args.get("type", "bullish")
        time: int = int(args.get("time", 0))
        time_frame: str = args.get("tf", "15m")
        
        meta = self.broker.pairs[pair].add_order_block(order_block_type=order_block_type,
                                                       time=time,
                                                       time_frame=time_frame)
        
        return jsonify(meta)
    
    
    def save_broker(self) -> Dict[str, bool]:
        
        
        args = request.args
        
        filename = args.get("filename", "broker")
        
        self.broker.save(filename=filename)
        
        return jsonify({"Saved": True})
        
    
    def load_broker(self) -> Dict[str, bool]:
        args = request.args
        
        filename = args.get("filename", "broker")
        self.broker = utils.load_model(filename=filename)
        
        return jsonify({"Loaded": True})