from dataclasses import dataclass

@dataclass
class Order_Block:
    """
    Properties & Args:
        order_block_type (str): "bullish" or "bearish"
        start_time (int): The starting time of the orderblock (it will displaced from that time)
        max_rate (float): The max. rate from the Order_Block (higest point in price range)
        min_rate (float): The min. rate from the Order_Block (lowest point in price range)
    """
    type: str
    start_time: float
    max_rate: float
    min_rate: float