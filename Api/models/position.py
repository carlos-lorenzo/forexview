import gc
import string
from random import choices
from dataclasses import dataclass, field
from typing import Optional, Dict, List


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
    
    id: str = field(init=False, default="")
    
    PIP: float = 0.00001
    
    
    def __post_init__(self):
        
        self.id = self.assign_position_id()
        
        self.order_type = self.order_type.lower()
        
        if self.order_type not in ("long", "short"):
            raise Exception("Invalid order type, order must be 'long' | 'short'")
        
        
        if not self.stop_loss:
            self.stop_loss = round((self.order_rate - (20 * self.PIP) if self.order_type == "long" else self.order_rate + (20 * self.PIP)), 5)

        if not self.take_profit:
            self.take_profit = round((self.order_rate + (200 * self.PIP) if self.order_type == "long" else self.order_rate - (200 * self.PIP)), 5)
        
        
        if self.order_type == "long":
            self.risk_reward = round((self.take_profit - self.order_rate) / (self.order_rate - self.stop_loss))
        
        else:
            self.risk_reward = round((self.order_rate - self.take_profit) / (self.stop_loss - self.order_rate))
          
    
    def assign_position_id(self) -> str:
        """
        Returns a unique ID that no other Position has

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
            position_id: str = generate_id()
            
            positions: List[Position] = list(filter(lambda object: isinstance(object, Position), gc.get_objects()))
            
            if position_id not in [position.id for position in positions]:
                return position_id
    
    
    def __update_profit_loss(self, current_rate: float) -> None:
        """
        Update profit_loss based on current_rate

        Args:
            current_rate (float): current_rate of a given pair
        """
        
        if self.order_type == "long":
            change_multiplyer = (current_rate - self.order_rate) / (self.take_profit - self.order_rate)

        else:
            change_multiplyer = (self.order_rate - current_rate) / (self.order_rate - self.take_profit)
            
        self.profit_loss = round((change_multiplyer * self.starting_size), 2)
                

    def update_status(self, current_candle: Dict[str, float]) -> None:
        """
        Update status (set position as active or not)\n
        Active position if tp or sl haven't been broken

        Args:
            current_candle (Dict[str, float]): Dict holding current candle data (time, open, high, low, close)
        """
        
        high = current_candle.get("high", self.order_rate)
        low = current_candle.get("low", self.order_rate)
        close = current_candle.get("close", self.order_rate)
        
        self.__update_profit_loss(current_rate=close)
        
        if self.order_type == "long":
            if high >= self.take_profit or low <= self.stop_loss:
                self.active = False
                
                 
        else:
            if high <= self.take_profit or low >= self.stop_loss:
                self.active = False
                