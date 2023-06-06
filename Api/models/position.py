from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class Position:
    """
    Args:
        order_type (str): "long" | "short"
        starting_size (float): Position size (money invested)
        order_rate (float): Rate at which the position was opened
        pair (float): The currency pair in which this Position was opened
        take_profit Optional(float): Rate at which the position will be closed (on a profit). Default ± 20 pips
        stop_loss Optional(float): Rate at which the position will be closed (on a loss). Default ± 2 pips
    
    
    Properties:
        order_type (str): "long" | "short"
        starting_size (float): Position size (money invested)
        order_rate (float): Rate at which the position was opened
        pair (float): The currency pair in which this Position was opened
        take_profit (float): Rate at which the position will be closed (on a profit)
        stop_loss (float): Rate at which the position will be closed (on a loss)
        profit_loss (float): The profit | loss of a Position
        risk_reward (float): Risk-reward ratio, constant by which profit_loss is multiplied 
        active (bool): The status of the Position. False if take_profit | stop_loss surpassed
        PIP: float: Standard FOREX unity. The smallest price movement possible (0.00001).

    Raises:
        Exception: order_type set incorrectly (can only be set to "long" | "short")
    """
    
    
    order_type: str
    starting_size: float
    order_rate: float
    
    pair: str = field(default="EURUSD")
    take_profit: Optional[float] = field(default=None)
    stop_loss: Optional[float] = field(default=None)
    
    
    
    profit_loss: float = field(init=False, default=0)
    risk_reward: float = field(init=False, default=1)
    active: bool = field(init=False, default=True)
    
    PIP: float = 0.00001
    
    
    def __post_init__(self):
        
        self.order_type = self.order_type.lower()
        
        if self.order_type not in ("long", "short"):
            raise Exception("Invalid order type, order must be 'long' | 'short'")
        
        
        if not self.stop_loss:
            self.stop_loss = self.order_rate - (2 * self.PIP) if self.order_type == "long" else self.order_rate + (2 * self.PIP)

        if not self.take_profit:
            self.take_profit = self.order_rate + (20 * self.PIP) if self.order_type == "long" else self.order_rate - (20 * self.PIP)
        
        
        if self.order_type == "long":
            self.risk_reward = round((self.take_profit - self.order_rate) / (self.order_rate - self.stop_loss))
        
        else:
            self.risk_reward = round((self.order_rate - self.take_profit) / (self.stop_loss - self.order_rate))
          
    
    def __update_profit_loss(self, current_rate: float) -> None:
        if self.order_type == "buy":
            price_change = (current_rate - self.order_rate) / (self.take_profit - self.order_rate)

        else:
            price_change = (self.order_rate - current_rate) / (self.order_rate - self.take_profit)
            
        self.profit_loss = round((price_change * (self.starting_size * self.risk_reward)), 2)
                

    def update_status(self, current_candle: Dict[str, float]) -> None:
        high_rate = current_candle.get("high", self.order_rate)
        low_rate = current_candle.get("low", self.order_rate)
        close_rate = current_candle.get("close", self.order_rate)
        
        self.__update_profit_loss(current_rate=close_rate)
        
        if self.order_type == "long":
            if high_rate >= self.take_profit or low_rate <= self.stop_loss:
                self.active = False
                 
        else:
            if high_rate <= self.take_profit or low_rate >= self.stop_loss:
                self.active = False
