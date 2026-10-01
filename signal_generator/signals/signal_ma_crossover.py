from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent
from portfolio.portfolio import Portfolio
from ..interfaces.signal_generator_interface import ISignalGenerator
from queue import Queue

class SignalMACrossover(ISignalGenerator):

    def __init__(self, events_queue: Queue, data_provider: DataProvider, portfolio: Portfolio, timeframe: str, fast_period: int, slow_period: int):
       self.events_queue = events_queue
       self.data_provider = data_provider   
       self.portfolio = portfolio
       self.timeframe = timeframe
       self.fast_period = fast_period if fast_period > 1 else 2 # Aseguramos que el periodo rápido sea al menos 2
       self.slow_period = slow_period if slow_period >2 else 3 # Aseguramos que el periodo lento sea al menos 3, y mayor que el periodo rápido
       if self.fast_period>=self.slow_period:
           raise Exception("El periodo rápido debe ser menor que el periodo lento para un cruce de medias móviles.")

    def _create_and_put_signal_event(self, symbol: str, signal: str, target_order: str, target_price: float, magic_number: int, sl: float, tp: float):
        # Creamos un evento de señal
        signal_event = SignalEvent(symbol=symbol, 
                                   signal=signal, 
                                   target_order=target_order, 
                                   target_price=target_price, 
                                   magic_number=magic_number, 
                                   sl=sl, 
                                   tp=tp)
       

        #Ponemos en la cola de eventos el evento de señal generado, para que sea procesado por el resto del sistema
        self.events_queue.put(signal_event)

    def generate_signal(self, data_event: DataEvent, portfolio: Portfolio) ->  None:

        # Cogemos el símbolo del evento
        symbol = data_event.symbol

        # Recuperamos los datos necesarios para calcular las medias móviles
        bars = self.data_provider.get_latest_closed_bars(symbol, self.timeframe, self.slow_period)

        # Recuperamos las posiciones abiertas por esta estrategia en el símbolo donde hemos tenido el Data Event
        open_positions = portfolio.get_number_of_strategy_open_positions_by_symbol(symbol)

        #Calculamos el valor de los indicadores. Seguimos la filosofìa de Trend Following, no la de Mean Reversion
        fast_ma = bars['close'][self.fast_period:].mean() #media movil rapida, que es el precio de cierre de unas pocas velas (de cinco velas por ejemplo) en un periodo de tiempo determinado (por ejemplo, 1 minuto, 5 minutos, 1 hora, etc.)
        slow_ma = bars['close'].mean() #media movil lenta, que es el precio de cierre de muchas velas (de 20 velas por ejemplo) en un periodo de tiempo determinado (por ejemplo, 1 minuto, 5 minutos, 1 hora, etc.)

        #Detectar una señal de compra. Compro justo poco despues del cruce. Compro caro para vender mas caro.
        #Lo de open_positions['LONG'] == 0 es para verificar si no hay posisiones ya abiertas de compra, lo que significa que ya estamos comprando y por lo tanto no es necesario emitir una nueva señal de compra
        if open_positions['LONG'] == 0 and fast_ma >slow_ma: #esto significa que la media movil rapida esta por encima de la media movil lenta, lo que indica de alta demanda de mercado, por lo tanto se genera una señal de compra. Esto significa que yo como trader, estoy dispuesto a comprar el activo a un precio más alto que el precio actual del mercado, lo que indica que espero que el precio siga subiendo. En otras palabras, estoy dispuesto a pagar más por el activo porque creo que su valor aumentará en el futuro.
            signal = "BUY"

        #Detectar una señal de venta. Vendo justo poco despues del cruce. Vendo barato para no quedarme y despues tener que vender mas barato aun.
        elif open_positions['SHORT'] == 0 and fast_ma < slow_ma: #esto significa que la media movil rapida esta por debajo de la media movil lenta, lo que indica de baja demanda de mercado, por lo tanto se genera una señal de venta. Esto significa que yo como trader, estoy dispuesto a vender el activo a un precio más bajo que el precio actual del mercado, lo que indica que espero que el precio siga bajando. En otras palabras, estoy dispuesto a vender el activo a un precio más bajo porque creo que su valor disminuirá en el futuro.
            signal = "SELL"

        else:
            signal = ""

         # Si tenemos señal, generamos SignalEvent y lo colocamos en la cola de Eventos
        if signal != "":
            self._create_and_put_signal_event(symbol=symbol,
                                              signal=signal,
                                              target_order="MARKET", #orden de mercado, es decir, se ejecuta al precio actual del mercado, tal como esta definido en la clase OrderType de events.py
                                              target_price=0.0, #el precio objetivo para target_order="MARKET" no es relevante, ya que se ejecuta al precio actual del mercado
                                              magic_number=self.portfolio.magic, #un numero magico cualquiera, que se puede usar para identificar la estrategia que genero la señal
                                              sl=0.0, #el nivel de stop loss para target_order="MARKET" no es relevante, ya que se ejecuta al precio actual del mercado
                                              tp=0.0) #el nivel de take profit para target_order="MARKET" no es relevante, ya que se ejecuta al precio actual del mercado