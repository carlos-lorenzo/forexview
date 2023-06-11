from dataclasses import dataclass, field
from typing import List, Dict

from .position import Position
from .pair import Pair



@dataclass
class Broker:
    """
    Manages logic for Position(s). Simulates a real-life broker
    Args:
        balance (float): Starting balance (default: 10000)
        pairs (Dict[str, Pair]): Dictionary (pair name, Pair). A Pair holds all of its time frames, current time
        
    Properties:
        balance (float): Current balance
        equity (float): Current equity (balance + profit/loss of all positions)
        pairs (Dict[str, Pair]): Dictionary (pair name, Pair). A Pair holds all of its time frames, current time
        open_positions (List[Position]): Holds a list of all currently open positions
        closed_potitions (List[Position]): Holds a list of all closed open positions
        
        
    """
    balance: float = field(default=10000)
    pairs: Dict[str, Pair] = field(default_factory=dict)
    
    
    open_positions: List[Position] = field(init=False, default_factory=list)
    closed_positions: List[Position] = field(init=False, default_factory=list)
    
    equity: float = field(init=False)
    
    
    
    
    def __post_init__(self):
        from .api import API
        self.equity = self.balance
        self.api = API(self, debug=True)
    
    def __str__(self) -> str:
        return f"Balance: {self.balance}\nEquity: {self.equity}\nAvailable pairs: {' | '.join(self.pairs.keys())}"
    
    
    def open_position(self, order_type: str, size: float, pair: str, take_profit: float = None, stop_loss: float = None) -> Dict[str, str]:
        """
        Opens a position and adds it to self.open_positions

        Args:
            order_type (str): "long" | "short"
            size (float): Position size (must be smaller than self.balance)
            pair (str): The pair where the position will be opened
            take_profit (float): Take profit rate (see Position.take_profit for more info). Defaults to None
            stop_loss (float): Stop loss rate (see Position.stop_loss for more info). Defaults to None

        Returns:
            Dict[str, str]: Status
        """
        pair = pair.upper()
        
        current_rate = self.pairs.get(pair).get_current_candle().get("close")
        
        
        if size <= self.balance:
            new_position = Position(order_type=order_type, 
                                    starting_size=size, 
                                    order_rate=current_rate,
                                    pair=pair,
                                    take_profit=take_profit,
                                    stop_loss=stop_loss)
        
            self.open_positions.append(new_position)
            
            self.balance -= size
            
            return {"status": "success"}

        
        else:
            return {"status": "not enough balance"}
    
    
    def close_position(self, position_id: str) -> Dict[str, str]:
        """
        Closes a position with a given id
        
        Args:
            position_id (str): An id (alphanumeric string)
        

        Returns:
            Dict[str, str]: Status
        """
        
        for position in self.open_positions:
            if position.id == position_id:
                position.active = False
                self.update()
                return {"status": f"Position {position.id} closed"}
        
        else:
            return {"status": f"{position_id} not an open position"}
            
          
        
    def update(self) -> None:
        """
        Updates all positions, balances and equity
        
        
        """
        for position in self.open_positions:
            current_candle = self.pairs.get(position.pair).get_current_candle()
            position.update_status(current_candle=current_candle)
            
            
            
            if not position.active:
                self.balance += (position.starting_size + position.profit_loss)
                self.closed_positions.append(self.open_positions.pop(self.open_positions.index(position)))
                
        self.equity = self.balance + sum([(position.starting_size + position.profit_loss) for position in self.open_positions])
            
    


    

