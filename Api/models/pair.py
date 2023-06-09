from dataclasses import dataclass, field
from typing import Dict, List

from pandas import DataFrame, Series


from .order_block import Order_Block

@dataclass
class Pair:
    """
    Holds pair data
    
    Args:
        name (str): The pair name
        time_frames (Dict[str, DataFrame | int]): Holds all time frames ("ohlc") an the number of 1m candles ("n_candles") required to form a single candle (row) in tha time frame
    
    Properties:
        name (str): The pair name
        time_frames (Dict[str, DataFrame | int]): Holds all time frames ("ohlc") an the number of 1m candles ("n_candles") required to form a single candle (row) in tha time frame
        current_minute (int): The current time for that pair
        order_blocks (List[Order_Block]): Holds all the Order_Block(s) for this Pair
    """
    name: str
    time_frames: Dict[str, DataFrame | int] = field(default_factory=dict)
    
    current_minute: int = field(init=False)
    order_blocks: List[Order_Block] = field(default_factory=list)
    
    def __post_init__(self):
        self.name = self.name.upper()
        self.current_minute = self.initilise_minute()
    
    # Init minutes
    def initilise_minute(self) -> int:
        """
        Sets self.current_minute to default value (30 of whatever the biggest tf is)

        Returns:
            int: Current minute
        """
        return max([ohlc_data.get("n_candles") for ohlc_data in self.time_frames.values()]) * 5

    
    
    def get_current_candle(self) -> Dict[str, float]:
        """
        Return the current candle

        Returns:
            Dict[str, float]: Candle data (time, open, high, low close)
        """
        return self.time_frames.get("1m").get("ohlc").iloc[self.current_minute].to_dict()
    
    
    def update_time(self, minutes: int) -> None:
        """
        Updates self.current minutes based on minutes

        Args:
            minutes (int): The amount of minutes to be added to self.minutes
        """
        
        
        self.current_minute += minutes
    
    def add_order_block(self, order_block_type: str, time: int, time_frame: str) -> Dict[str, bool]:
        """
        Creates and appends an Order_Block to self.order_blocks

        Args:
            order_block_type (str): "bullish" or "bearish"
            time (int): The starting time of the orderblock (it will displaced from that time)
            time_frame (str): The time frame where this order block was created in
        """
        
        order_block_type = order_block_type.lower()
        time = round(time)
        
        if order_block_type in ["bullish", "bearish"] and time > 0:
        
            time_frame_data: Dict[str, DataFrame | int] = self.time_frames.get(time_frame)
            
            ohlc: DataFrame = time_frame_data["ohlc"]
            
        
            order_block_candle = ohlc.loc[ohlc["time"] == time]
            
            
            open_rate = order_block_candle["open"].values[0]
            high_rate = order_block_candle["high"].values[0]
            low_rate = order_block_candle["low"].values[0]
            close_rate = order_block_candle["close"].values[0]
            
            wick_up_size = high_rate - open_rate
            wick_down_size = close_rate - low_rate
            body_size = abs(open_rate - close_rate)
            
            if order_block_type == "bullish":
                if wick_down_size > body_size:
                    max_rate: float = order_block_candle["open"].values[0]
                    min_rate: float = order_block_candle["low"].values[0]

                else:
                    max_rate: float = order_block_candle["high"].values[0]
                    min_rate: float = order_block_candle["low"].values[0]
                    
            else:
                if wick_up_size > body_size:
                    max_rate: float = order_block_candle["high"].values[0]
                    min_rate: float = order_block_candle["close"].values[0]

                else:
                    max_rate: float = order_block_candle["high"].values[0]
                    min_rate: float = order_block_candle["low"].values[0]
                
                
            new_order_block = Order_Block(type=order_block_type,
                                          pair=self.name,
                                          start_time=time, 
                                          max_rate=max_rate,
                                          min_rate=min_rate)
            
            
            self.order_blocks.append(new_order_block)
            
            return {"created": True, "id": new_order_block.uid}
        
        else:
            return {"created": False}


    def filter_order_blocks(self) -> None:
        """
        Removes order blocks that have been mitigated (price has surpassed 50% of the orderblock) from self.order_blocks
        """
        current_candle: Series = self.time_frames["1m"]["ohlc"].iloc[self.current_minute]
        
        
        
        for i, order_block in enumerate(self.order_blocks):
            mid_point: float = ((order_block.max_rate + order_block.min_rate) / 2)
            
            if order_block.type == "bullish":
                if current_candle["low"] <= mid_point:
                    self.order_blocks.pop(i)
                   
                    
            else:
                if current_candle["high"] >= mid_point:
                    self.order_blocks.pop(i)
                    