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

    def get_latest_closed_bar(self, symbol: str, timeframe: str) -> pd.Series:
        """
        Retrieves the latest closed bar for a given symbol and timeframe.

        Args:
            symbol (str): The symbol to retrieve the bar data for.
            timeframe (str): The timeframe of the bars.

        Returns:
            pd.Series: The latest closed bar data as a pandas Series object.
        """
        
        # Definir los parámetros adecuados
        tf = self._map_timeframes(timeframe)
        from_position = 1
        num_bars = 1
        
        # Recuperamos los datos de la última vela
        try:
            bars_np_array = mt5.copy_rates_from_pos(symbol, tf, from_position, num_bars)
            if bars_np_array is None:
                print(f"El símbolo {symbol} no existe o no se han podido recuperar su datos")

                # Vamos a devolver una Series empty
                return pd.Series()

            bars = pd.DataFrame(bars_np_array)

            # Convertimos la columna time a datetime y la hacemos el índice
            bars['time'] = pd.to_datetime(bars['time'], unit='s')
            bars.set_index('time', inplace=True)

            # Cambiamos nombres de columnas y las reorganizamos
            bars.rename(columns={'tick_volume': 'tickvol', 'real_volume': 'vol'}, inplace=True)
            bars = bars[['open', 'high', 'low', 'close', 'tickvol', 'vol', 'spread']]
        
        except Exception as e:
            print(f"No se han podido recuperar los datos de la última vela de {symbol} {timeframe} - MT5 Error: {mt5.last_error()}, exception: {e}")
        
        else:
            # Si el DF está vacío, devolvemos una serie vacía
            if bars.empty:
                return pd.Series()
            else:
                return bars.iloc[-1] #iloc returns the last row of the DataFrame as a Series object