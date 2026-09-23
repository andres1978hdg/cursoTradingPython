# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
import MetaTrader5 as mt5
#cada activo tiene un volumen minimo distinto a otro activo y esto es impuesto por el broker, por lo que el volumen no es fijo.
class MinSizePositionSizer(IPositionSizer): #este sizer se basa en el concepto de que el tamaño de la posición será siempre el mínimo permitido por el broker para ese símbolo, que se obtiene a través de la función mt5.symbol_info(symbol).volume_min. Esto asegura que las operaciones se realicen con el tamaño mínimo permitido, lo cual puede ser útil para estrategias de trading que buscan minimizar el riesgo o para probar estrategias con un capital limitado.

    def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
        
        volume = mt5.symbol_info(signal_event.symbol).volume_min # o sea el volumen q viene del broker conectado a mt5.

        if volume is not None:
            return volume
        else:
            print(f"- ERROR (MinSizePositionSizer): No se ha podido determinar el volumen mínimo para {signal_event.symbol}")
            return 0.0