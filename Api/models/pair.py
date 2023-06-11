from dataclasses import dataclass, field
from typing import Dict

from pandas import DataFrame

@dataclass
class Pair:
    """
    Holds pair data
    
    Args:
        name (str): The pair name
        time_frames (Dict[str, DataFrame | int]): Holds all time frames ("ohlc") an the number of 1m candles ("n_candles") required to form a single candle (row) in tha time frame
    """
    name: str
    time_frames: Dict[str, DataFrame | int] = field(default_factory=dict)
    
    current_minute: int = field(init=False)
    
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
        return max([ohlc_data.get("n_candles") for ohlc_data in self.time_frames.values()]) * 30

    
    
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