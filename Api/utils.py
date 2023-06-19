import string
import gc
from random import choices
from typing import Dict, List, Any
import dill

import pandas as pd



def interval_to_minutes(interval: str) -> int:
    """
    Convert an interval to the number of minutes\n

    Format: {amount}{time scale} e.g. 15m, 1h, 1D,...
    
    Args:
        interval (str): Inteval of time (15m, 1h, 1D)

    Returns:
        int: Number of minutes in interval (1h = 60m)
    """
    
    scales: Dict[str: int] = {
        "m": 1,
        "h": 60,
        "D": 1440,
        "W": 10080,
        "M": 302400
    }
    
    
    multiplyer = int(interval[:-1])
    scale = interval[-1]
    
    if scale not in scales.keys():
        raise KeyError("Invalid time scale. Valid scales: m (minutes), h (hours), D (days), M (months)")
    
    else:
        return multiplyer * scales.get(scale)
    

def defractalise_ohlc(df: pd.DataFrame, interval: str) -> Dict:
    """
    Convert a mintute ohlc DataFrame into a higher tf DataFrame\n
    For example: 1m -> 1h (specified by interval)

    Args:
        df (pd.DataFrame): 1m ohlc (and Volume) DataFrane
        interval (str): An interval of time in the format (1m, 15m, 4h, ...)

    Returns:
        Dict: {ohlc: the actual ohlc data,
                 n_candles: number of candles used to create data (set by interval)}
    """
    
    n_candles = interval_to_minutes(interval=interval)
    
    ohlc_data: List[Dict] = []
    for i in range(1, df.shape[0], n_candles):
        
        try:
            new_candle = df.iloc[i:i+n_candles]
        
        except IndexError:
            break
        
        
        current_candle_data: Dict = {
            "time": new_candle.iloc[-1]["time"],
            "open":  new_candle.iloc[0]["open"],
            "high":  new_candle["high"].max(),
            "low":  new_candle["low"].min(),
            "close": new_candle.iloc[-1]["close"],
        }
        
        if "volume" in [column.lower() for column in df.columns.values]:
            current_candle_data["Volume"] = round(new_candle["Volume"].mean(), 2)
        
        ohlc_data.append(current_candle_data)
        

        
    return {
        "ohlc": pd.DataFrame(ohlc_data, columns=df.columns),
        "n_candles": n_candles
    }


def generate_id(length) -> str:
    """
    Generates a 6 digit alphanumeric id

    Returns:
        str: alphanumeric id
    """
    return "".join(choices(string.ascii_letters + string.digits, k=length))


def generate_uid(Model: object, length: int = 6) -> str:
    """
    Returns a unique ID that no other model has

    Args:
        Model (object): An object with a uid property
    
    Returns:
        str: A unique id
    """
    
    while True:
        model_id: str = generate_id(length=length)
        
        models: List[Model] = list(filter(lambda object: isinstance(object, Model), gc.get_objects()))
        
        if model_id not in [model.uid for model in models]:
            return model_id
    
    

def serialise_model(Model: object, filename: str = "model") -> None:
    with open(filename, "wb") as model_file:
        dill.dump(Model, model_file)
        
    
    
def load_model(filename: str = "model") -> object:
    with open(filename, "rb") as model_file:
        return dill.load(model_file)
        