from events.events import DataEvent, SignalEvent
from ..interfaces.signal_generator_interface import ISignalGenerator

class SignalMACrossover(ISignalGenerator):

    def generate_signal(self, data_event: DataEvent) ->  None:

        # Cogemos el símbolo del evento
        symbol = data_event.symbol

        # Recuperamos los datos necesarios para calcular las medias móviles
        bars = self.DATA_PROVIDER.get_latest_closed_bars(symbol, self.timeframe, self.slow_period)

        #Calculamos el valor de los indicadores 
        fast_ma = bars['close'][-self.fast_period:].mean() #media movil rapida
        slow_ma = bars['close'].mean()

        #Detectar una señal de compra
        if fast_ma >slow_ma:
            signal = "BUY"

        #Detectar una señal de venta
        elif fast_ma < slow_ma:
            signal = "SELL"

        else:
            signal = ""

         # Si tenemos señal, generamos SignalEvent y lo colocamos en la cola de Eventos
        if signal != "":None
