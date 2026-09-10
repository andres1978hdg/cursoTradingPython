# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

#from utils.utils import Utils
import MetaTrader5 as mt5
import pandas as pd
from typing import Dict
from datetime import datetime
#from events.events import DataEvent
from queue import Queue


class DataProvider():

    def __init__(self):
        pass


    def _map_timeframes(self, timeframe: str) -> int:
        """
        Maps a string timeframe to its corresponding integer value.

        Args:
            timeframe (str): The string representation of the timeframe.

        Returns:
            int: The integer value of the mapped timeframe.

        Raises:
            None

        """
        timeframe_mapping = {
            '1min': mt5.TIMEFRAME_M1,
            '2min': mt5.TIMEFRAME_M2,                        
            '3min': mt5.TIMEFRAME_M3,                        
            '4min': mt5.TIMEFRAME_M4,                        
            '5min': mt5.TIMEFRAME_M5,                        
            '6min': mt5.TIMEFRAME_M6,                        
            '10min': mt5.TIMEFRAME_M10,                       
            '12min': mt5.TIMEFRAME_M12,
            '15min': mt5.TIMEFRAME_M15,
            '20min': mt5.TIMEFRAME_M20,                       
            '30min': mt5.TIMEFRAME_M30,                       
            '1h': mt5.TIMEFRAME_H1,                          
            '2h': mt5.TIMEFRAME_H2,                          
            '3h': mt5.TIMEFRAME_H3,                          
            '4h': mt5.TIMEFRAME_H4,                          
            '6h': mt5.TIMEFRAME_H6,                          
            '8h': mt5.TIMEFRAME_H8,                          
            '12h': mt5.TIMEFRAME_H12,
            '1d': mt5.TIMEFRAME_D1,                       
            '1w': mt5.TIMEFRAME_W1,                       
            '1M': mt5.TIMEFRAME_MN1,                       
        }

        try:
            return timeframe_mapping[timeframe]
        except:
            print(f"Timeframe {timeframe} no es válido.")

    
    def get_latest_closed_bar(self, symbol: str, timeframe: str) :
       tf = self._map_timeframes(timeframe)
       from_position = 1
       num_bars= 1 #ultima vela cerrada