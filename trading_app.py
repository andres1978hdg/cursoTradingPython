# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from platform_connector.platform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from queue import Queue


if __name__ == "__main__":
        # Definición de variables necesarias para la estrategia
    symbols = ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCLP'] #un simbolo en mt5 es un par de divisas, por ejemplo EURUSD, USDJPY, GBPUSD, USDCLP del MarketWatch (la ventana q se ve en la plataforma de mt5 donde estan todos los simbolos que podemos tradear y q se activa con ctrl +M)
    timeframe = '1min' #el timeframe de las velas que queremos recuperar, en este caso 1min, es decir, cada vela representa 1 minuto

        # Creación de la cola de eventos principal
    events_queue = Queue()


    CONNECT = PlatformConnector(symbol_list=symbols) #instanciamos la clase PlatformConnector, que se encargara de inicializar la plataforma y añadir los simbolos al MarketWatch
    DATA_PROVIDER = DataProvider(events_queue=events_queue, symbol_list=symbols, timeframe=timeframe)
   