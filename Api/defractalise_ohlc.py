from typing import Dict, List

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
