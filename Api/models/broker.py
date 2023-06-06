from dataclasses import dataclass, field
from typing import List, Dict

from .position import Position
from .pair import Pair



@dataclass
class Broker:
    balance: float
    pairs: Dict[str, Pair] = field(default_factory=dict)
    
    
    open_positions: List[Position] = field(init=False, default_factory=list)
    closed_positions: List[Position] = field(init=False, default_factory=list)
    
    equity: float = field(init=False)
    
    def __post_init__(self):
        self.equity = self.balance
    
    
    def open_position(self, order_type: str, size: float, pair: str) -> None: #Add TP / SL parameter
        pair = pair.upper()
        
        current_rate = self.pairs.get(pair).get_current_candle().get("close")
        
        new_position = Position(order_type=order_type, 
                                starting_size=size, 
                                order_rate=current_rate,
                                pair=pair)
        
        self.open_positions.append(new_position)
    
    
    def update(self) -> None:
        for position in self.open_positions:
            current_candle = self.pairs.get(position.pair).get_current_candle()
            position.update_status(current_candle=current_candle)
            
            self.equity += position.profit_loss
            
            
            if not position.active:
                self.balance = self.equity
                self.closed_positions.append(self.open_positions.pop(self.open_positions.index(position)))
            
            

    

