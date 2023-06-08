from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Pair:
    name: str
    time_frames: Dict = field(default_factory=dict)
    
    current_minute: int = field(init=False)
    
    def __post_init__(self):
        self.name = self.name.upper()
        self.current_minute = self.initilise_minute()
    
    # Init minutes
    def initilise_minute(self) -> int:
        return max([ohlc_data.get("n_candles") for ohlc_data in self.time_frames.values()])

    
    
    def get_current_candle(self) -> Dict[str, float]:
        return self.time_frames.get("1m").get("ohlc").iloc[self.current_minute].to_dict()
    
    
    
    
    def update_time(self, minutes: int) -> None:
        self.current_minute += minutes