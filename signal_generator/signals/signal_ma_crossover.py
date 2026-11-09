# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from events.events import DataEvent, SignalEvent
from data_provider.data_provider import DataProvider
from ..interfaces.signal_generator_interface import ISignalGenerator
from ..properties.signal_generator_properties import MACrossoverProps
from portfolio.portfolio import Portfolio
from order_executor.order_executor import OrderExecutor

class SignalMACrossover(ISignalGenerator):
    
    def __init__(self, properties: MACrossoverProps):
        """
        Initializes the MACrossover object.

        Args:
            properties (MACrossoverProps): The properties object containing the parameters for the moving average crossover.

        Raises:
            Exception: If the fast period is greater than or equal to the slow period.

        """
        self.timeframe = properties.timeframe
        self.fast_period = properties.fast_period if properties.fast_period > 1 else 2 # Aseguramos que el periodo rápido sea al menos 2
        self.slow_period = properties.slow_period if properties.slow_period > 2 else 3 # Aseguramos que el periodo lento sea al menos 3, y mayor que el periodo rápido

        if self.fast_period >= self.slow_period:
            raise Exception(f"ERROR: el periodo rápido ({self.fast_period}) es mayor o igual al periodo lento ({self.slow_period}) para el cálculo de las medias móviles")

    
    def generate_signal(self, data_event: DataEvent, data_provider: DataProvider, portfolio: Portfolio, order_executor: OrderExecutor) -> SignalEvent:
        """
        Generates a signal based on the moving average crossover strategy.

        Args:
            data_event (DataEvent): The data event that triggered the signal generation.
            data_provider (DataProvider): The data provider used to retrieve the necessary data.
            portfolio (Portfolio): The portfolio containing the open positions.
            order_executor (OrderExecutor): The order executor used to execute the orders.

        Returns:
            SignalEvent: The generated signal event.
        """
        # Cogemos el símbolo del evento
        symbol = data_event.symbol

        # Recuperamos los datos necesarios para calcular las medias móviles
        bars = data_provider.get_latest_closed_bars(symbol, self.timeframe, self.slow_period)

        # Recuperamos las posiciones abiertas por esta estrategia en el símbolo donde hemos tenido el Data Event
        open_positions = portfolio.get_number_of_strategy_open_positions_by_symbol(symbol)

        # Calculamos el valor de los indicadores.  Seguimos la filosofìa de Trend Following, no la de Mean Reversion
        fast_ma = bars['close'][-self.fast_period:].mean()  #media movil rapida, que es el precio de cierre de unas pocas velas (de cinco velas por ejemplo) en un periodo de tiempo determinado (por ejemplo, 1 minuto, 5 minutos, 1 hora, etc.)
        slow_ma = bars['close'].mean() #media movil lenta, que es el precio de cierre de muchas velas (de 20 velas por ejemplo) en un periodo de tiempo determinado (por ejemplo, 1 minuto, 5 minutos, 1 hora, etc.)

        # Detectar una señal de compra. Compro justo poco despues del cruce. Compro caro para vender mas caro.
          #Lo de open_positions['LONG'] == 0 es para verificar si no hay posisiones ya abiertas de compra, lo que significa que ya estamos comprando y por lo tanto no es necesario emitir una nueva señal de compra
        if open_positions['LONG'] == 0 and fast_ma > slow_ma: #esto significa que la media movil rapida esta por encima de la media movil lenta, lo que indica de alta demanda de mercado, por lo tanto se genera una señal de compra. Esto significa que yo como trader, estoy dispuesto a comprar el activo a un precio más alto que el precio actual del mercado, lo que indica que espero que el precio siga subiendo. En otras palabras, estoy dispuesto a pagar más por el activo porque creo que su valor aumentará en el futuro.
            if open_positions['SHORT'] > 0:
                # Tenemos señal de compra, pero tenemos posición de venta. Debemos cerrar la venta ANTES de abrir la compra.
                order_executor.close_strategy_short_positions_by_symbol(symbol)
            signal = "BUY"

        # Señal de venta.  Vendo justo poco despues del cruce. Vendo barato para no quedarme y despues tener que vender mas barato aun.
       
        elif open_positions['SHORT'] == 0 and slow_ma > fast_ma:
            if open_positions['LONG'] > 0:
                order_executor.close_strategy_long_positions_by_symbol(symbol)
            signal = "SELL"

        else:
            signal = ""

        # Si tenemos señal, generamos SignalEvent y lo colocamos en la cola de Eventos
        if signal != "":
            signal_event = SignalEvent(symbol=symbol,
                                    signal=signal,
                                    target_order="MARKET", #orden de mercado, es decir, se ejecuta al precio actual del mercado, tal como esta definido en la clase OrderType de events.py
                                    target_price=0.0, #el precio objetivo para target_order="MARKET" no es relevante, ya que se ejecuta al precio actual del mercado
                                    magic_number=portfolio.magic, #un numero magico cualquiera, que se puede usar para identificar la estrategia que genero la señal
                                    sl=0.0, #el nivel de stop loss para target_order="MARKET" no es relevante, ya que se ejecuta al precio actual del mercado
                                    tp=0.0) #el nivel de take profit para target_order="MARKET" no es relevante, ya que se ejecuta al precio actual del mercado
            
            return signal_event









