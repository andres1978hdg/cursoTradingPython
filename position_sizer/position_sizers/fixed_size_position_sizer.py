# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import FixedSizingProps


class FixedSizePositionSizer(IPositionSizer):

    def __init__(self, properties: FixedSizingProps): #la idea de tener una clase de propiedades es que si en el futuro se quieren agregar más propiedades a este Position Sizer, se pueden agregar a la clase FixedSizingProps y no hay que modificar el código del Position Sizer.
       
        self.fixed_volume = properties.volume


    def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
       
        # Devolver el tamaño de posición fija
        if self.fixed_volume >= 0.0:
            return self.fixed_volume
        else:
            return 0.0