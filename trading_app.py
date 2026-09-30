# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from platform_connector.platform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from queue import Queue
from trading_director.trading_director import TradingDirector
from signal_generator.signals.signal_ma_crossover import SignalMACrossover
from position_sizer.position_sizer import PositionSizer
from position_sizer.properties.position_sizer_properties import MinSizingProps, FixedSizingProps, RiskPctSizingProps


if __name__ == "__main__":
        # Definición de variables necesarias para la estrategia
    symbols = ['EURUSD', 'USDCLP'] #un simbolo en mt5 es un par de divisas, por ejemplo EURUSD, USDJPY, GBPUSD, USDCLP del MarketWatch (la ventana q se ve en la plataforma de mt5 donde estan todos los simbolos que podemos tradear y q se activa con ctrl +M)
    timeframe = '1min' #el timeframe de las velas que queremos recuperar, en este caso 1min, es decir, cada vela representa 1 minuto
    slow_ma_period = 20 #periodo de la media movil lenta, es decir, el numero de velas que se van a promediar para calcular la media movil lenta
    fast_ma_period = 5 #periodo de la media movil rapida, es decir
        # Creación de la cola de eventos principal
    events_queue = Queue()


    CONNECT = PlatformConnector(symbol_list=symbols) #instanciamos la clase PlatformConnector, que se encargara de inicializar la plataforma y añadir los simbolos al MarketWatch
    
    DATA_PROVIDER = DataProvider(events_queue=events_queue, symbol_list=symbols, timeframe=timeframe)

    SIGNAL_GENERATOR = SignalMACrossover(events_queue=events_queue,
                                        data_provider=DATA_PROVIDER,
                                        timeframe=timeframe,
                                        fast_period=fast_ma_period,
                                        slow_period=slow_ma_period)

    POSITION_SIZER = PositionSizer(events_queue=events_queue,
                                    data_provider=DATA_PROVIDER,
                                    sizing_properties=FixedSizingProps(volume=0.05))
    
    # Creación del trading director y ejecución del método principal
    TRADING_DIRECTOR = TradingDirector(events_queue=events_queue,
                                        data_provider=DATA_PROVIDER,
                                        signal_generator=SIGNAL_GENERATOR,   
                                        position_sizer=POSITION_SIZER)
    
    TRADING_DIRECTOR.execute()
   