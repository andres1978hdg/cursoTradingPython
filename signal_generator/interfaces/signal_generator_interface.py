# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from typing import Protocol
from events.events import DataEvent, SignalEvent
from data_provider.data_provider import DataProvider
#from portfolio.portfolio import Portfolio
#from order_executor.order_executor import OrderExecutor

class ISignalGenerator(Protocol):

    def generate_signal(self, data_event: DataEvent) -> SignalEvent | None: #self en esta linea  significa que es un método de instancia, es decir, que se llama sobre una instancia de la clase que implementa la interfaz ISignalGenerator. data_event es un parámetro que representa el evento de datos que se va a procesar para generar una señal de trading. data_provider es un parámetro que representa el proveedor de datos que se utilizará para obtener información adicional si es necesario. portfolio es un parámetro que representa la cartera de trading actual, que puede ser utilizada para tomar decisiones sobre la generación de señales. order_executor es un parámetro que representa el ejecutor de órdenes, que puede ser utilizado para enviar órdenes al mercado si se genera una señal. El tipo de retorno SignalEvent | None indica que el método puede devolver un objeto SignalEvent si se genera una señal, o None si no se genera ninguna señal.
        ... #los tres puntos indican que es un método abstracto, es decir, que no tiene implementación y debe ser implementado por cualquier clase que herede de ISignalGenerator
