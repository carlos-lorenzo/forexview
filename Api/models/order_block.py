import string
import gc

from dataclasses import dataclass, field
from random import choices
from typing import List

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
        self.uid = self.assign_order_block_id()
    
    
    def assign_order_block_id(self) -> str:
        """
        Returns a unique ID that no other Order_Block has

        Returns:
            str: A unique id
        """
        def generate_id() -> str:
            """
            Generates a 6 digit alphanumeric id

            Returns:
                str: _description_
            """
            return "".join(choices(string.ascii_letters + string.digits, k=6))
        
        
        while True:
            order_block_id: str = generate_id()
            
            order_blocks: List[Order_Block] = list(filter(lambda object: isinstance(object, Order_Block), gc.get_objects()))
            
            if order_block_id not in [order_block.uid for order_block in order_blocks]:
                return order_block_id