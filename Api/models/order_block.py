from dataclasses import dataclass, field

from utils import generate_uid

@dataclass
class Order_Block:
    """
    Args:
        order_block_type (str): "bullish" or "bearish"
        pair (str): The pair to which it belongs
        start_time (int): The starting time of the orderblock (it will displaced from that time)
        max_rate (float): The max. rate from the Order_Block (higest point in price range)
        min_rate (float): The min. rate from the Order_Block (lowest point in price range)
    
    
    Properties:
        uid (str): Unique, alphanumeric identifier
        order_block_type (str): "bullish" or "bearish"
        pair (str): The pair to which it belongs
        start_time (int): The starting time of the orderblock (it will displaced from that time)
        max_rate (float): The max. rate from the Order_Block (higest point in price range)
        min_rate (float): The min. rate from the Order_Block (lowest point in price range)
    """
    
    type: str
    pair: str
    start_time: float
    max_rate: float
    min_rate: float
    
    uid: str = field(init=False, default="")
    
    def __post_init__(self):
        self.uid = generate_uid(Model=Order_Block)
    
