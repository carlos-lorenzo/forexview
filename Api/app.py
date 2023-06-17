import pandas as pd

from models.broker import Broker
from models.pair import Pair


eur_usd_time_frames = {
    "1m": {"ohlc": pd.read_csv("Data/1m_EURUSD.csv"), "n_candles": 1},
    "15m": {"ohlc": pd.read_csv("Data/15m_EURUSD.csv"), "n_candles": 15},
    "1h": {"ohlc": pd.read_csv("Data/1h_EURUSD.csv"), "n_candles": 60},
    "4h": {"ohlc": pd.read_csv("Data/4h_EURUSD.csv"), "n_candles": 240},
    "1D": {"ohlc": pd.read_csv("Data/1D_EURUSD.csv"), "n_candles": 1440},
}

eurusd = Pair(name="EURUSD",
              time_frames=eur_usd_time_frames)

pairs = {
    "EURUSD": eurusd
}


broker = Broker(balance=10000,
                pairs=pairs)

api = broker.api
api.run()




